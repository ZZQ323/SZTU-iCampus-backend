package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthServiceV1;
import cn.edu.sztui.base.application.vo.CaptchaVO;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.loginhandle.LoginHandle;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import cn.edu.sztui.base.infrastructure.util.browserpool.PlaywrightBrowserPool;
import cn.edu.sztui.base.infrastructure.util.cache.LoginSessionCacheUtil;
import cn.edu.sztui.base.infrastructure.util.ocr.CaptchaOcrUtil;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.Cookie;
import com.microsoft.playwright.options.LoadState;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import static cn.edu.sztui.base.domain.model.SchoolAPIs.gatewayURL;
import static cn.edu.sztui.base.domain.model.SchoolAPIs.loginURL;

@Service
@Slf4j
public class AuthServiceV1Impl implements AuthServiceV1 {

    @Resource
    private PlaywrightBrowserPool browserPool;
    @Resource
    private LoginSessionCacheUtil loginSessionCacheUtil;
    @Resource
    private CaptchaOcrUtil captchaOcrUtil;


    @Resource
    private Map<LoginType, LoginHandle> loginHandlers;

    private static LoginType getCurrentLoginType(Page page) {
        // 维度1：优先读取页面内置的authMethodIDs
        String authMethodIdsStr = page.locator("input[id='authMethodIDs']").inputValue();
        if (!authMethodIdsStr.isEmpty() && !"null".equals(authMethodIdsStr)) {
            try {
                int authId = Integer.parseInt(authMethodIdsStr);
                LoginType type = LoginType.getByAuthId(authId);
                if (type != null) {
                    // 验证：该登录方式的tabCon是否显示（交叉验证）
                    Locator tabCon = page.locator("#" + type.getTabConId());
                    if (tabCon.isVisible()) {
                        return type;
                    }
                }
            } catch (NumberFormatException e) {
                log.warn("authMethodIDs解析失败：" + authMethodIdsStr);
            }
        }

        // 维度2：遍历所有tabCon，找显示状态的
        for (LoginType type : LoginType.values()) {
            Locator tabCon = page.locator("#" + type.getTabConId());
            if (tabCon.isVisible() && "block".equals(tabCon.evaluate("el => el.style.display").toString())) {
                return type;
            }
        }

        // 维度3：检测tabBar中选中的标签（dq类）
        Locator activeTab = page.locator("#tabBarIds li.dq");
        if (activeTab.isVisible()) {
            String tabText = activeTab.textContent().toLowerCase();
            if (tabText.contains("短信")) {
                return LoginType.SMS;
            } else if (tabText.contains("密码")) {
                return LoginType.USERNAME_PASSWORD;
            } else if (tabText.contains("otp") || tabText.contains("动态口令")) {
                return LoginType.OTP;
            }
        }

        return null; // 所有维度都失效，走兜底定位
    }

    /**
     * 只获取短信，获取全新后就清空context，但缓存 cookies
     *
     * @param id
     * @return
     */
    @Override
    public LoginResultsVo getSms(String id) {
        return browserPool.executeWithContext(context -> {
            Page page = context.newPage();
            if (loginSessionCacheUtil.hasValidSession(id)) {
                List<Cookie> cookies = loginSessionCacheUtil.getCookies(id);
                context.addCookies(cookies);
            }
            // 访问登录页面
            page.navigate(gatewayURL);
            // NETWORKIDLE 不等于 "JS 执行完"。需要等待目标元素可交互。
            page.waitForLoadState(LoadState.LOAD);
            page.waitForLoadState(LoadState.DOMCONTENTLOADED);
            page.waitForLoadState(LoadState.NETWORKIDLE);

            page.waitForSelector("input[id='" + LoginType.SMS.getConfig().getUsernameInputId() + "']", new Page.WaitForSelectorOptions());
            // 进行必要的等待，因为太快模拟点击会失败
            page.waitForSelector("#" + LoginType.SMS.getConfig().getSendSmsButtonId(), new Page.WaitForSelectorOptions().setTimeout(4000));

            LoginResultsVo ret = new LoginResultsVo();
            try {
                Locator usernameInput = page.locator("input[id='" + LoginType.SMS.getConfig().getUsernameInputId() + "']");
                usernameInput.clear();
                usernameInput.fill(id);
                page.locator("#" + LoginType.SMS.getConfig().getSendSmsButtonId()).click();
                page.waitForLoadState(LoadState.LOAD);
                page.waitForLoadState(LoadState.DOMCONTENTLOADED);
                page.waitForLoadState(LoadState.NETWORKIDLE);
                // 进入过网关后需要缓存 cookies
                loginSessionCacheUtil.saveCookies(id, context.cookies());
                // ret.setCookies(context.cookies(loginURL));
                // String bodyText = page.textContent("body");
                ret.setHtmlDoc("");
                return ret;
            } catch (Exception e) {
                log.error(e.getMessage(), e);
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "爬虫无法进行验证码获取！！", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
            }
        });
    }

    /**
     * 登录框架
     *
     * @param cmd
     * @return
     */
    @Override
    public LoginResultsVo loginFrame(LoginRequestCommand cmd) {
        return browserPool.executeWithContext(context -> {
            Page page = context.newPage();
            // 如果先前有cookie的话一定要注意
            if (loginSessionCacheUtil.hasValidSession(cmd.getUserId())) {
                List<Cookie> cookies = loginSessionCacheUtil.getCookies(cmd.getUserId());
                context.addCookies(cookies);
            }
            // 访问登录页面
            page.navigate(gatewayURL);
            // NETWORKIDLE 不等于 "JS 执行完"。需要等待目标元素可交互。
            page.waitForLoadState(LoadState.LOAD);
            page.waitForLoadState(LoadState.DOMCONTENTLOADED);
            page.waitForLoadState(LoadState.NETWORKIDLE);
            String curLogin = page.url().trim();

            // 可能直接就进去了，因为cookie 通过
            if ( page.content().contains("登录") ){
                handleLoginByType(page, cmd.getLoginType(), cmd.getUserId(), cmd.getCode());
                // 等待登录响应，同时执行登录操作
                Response loginResponse = page.waitForResponse(
                        resp -> resp.url().contains("login") && resp.ok(),
                        () -> handleLoginByType(page, cmd.getLoginType(), cmd.getUserId(), cmd.getCode())
                );
            }
            // 等待登录后页面稳定
            page.waitForLoadState(LoadState.LOAD, new Page.WaitForLoadStateOptions().setTimeout(3000));
            if( page.isVisible("#j_checkcodeImgCode41") ){
                // 检查是否出现 kaptcha
                try {
                    // 尝试识别
                    Locator captchaImg = page.locator("#j_checkcodeImgCode41");
                    byte[] imageBytes = captchaImg.screenshot();
                    String ret = captchaOcrUtil.recognize(imageBytes);
                    log.info("用户{}：ocr识别结果： {}",cmd.getUserId(),ret);
                } catch (Exception e) {
                    // getCaptcha()
                    log.error("用户{}：ocr无法识别图片，此处应当再多一层处理方式",cmd.getUserId());
                }
            }else{
                log.info("用户{}：未触发kaptcha",cmd.getUserId());
            }
            // 验证登录是否成功
            if ( page.url().equals(loginURL) )
                 throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), cmd.getUserId()+"：登录失败：页面未跳转至登录成功页，当前URL=" + page.url(), ResultCodeEnum.BAD_REQUEST.getCode());
            // 获取登录后的上下文信息
            LoginResultsVo ret = new LoginResultsVo();
            List<Cookie> cc = context.cookies(page.url());
            if ( Objects.isNull(cc))
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), cmd.getUserId()+"：爬虫登录失败" + page.content(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());

            log.info("用户{} 登录成功，已获取cookies：{}", cmd.getUserId(), cc );
            // 登录成功后缓存 cookie
            loginSessionCacheUtil.saveCookies(cmd.getUserId(), cc);
            // ret.setCookies(cc);
            // 获取整个页面的HTML内容
            String bodyText = page.textContent("body");
            ret.setHtmlDoc(bodyText);
            // 获取标题和URL
            log.info("Title: " + page.title());
            log.info("URL: " + page.url());

            return ret;
        });
    }

    /**
     * 策略模式处理不同登录方式
     * <p>
     * 经过测试发现，如果已有cookie的话，可以使用密码登录（是不是什么时候的cookie都行呢？）；
     * <li>但如果什么都没有就只能使用验证码登录；
     * <li>暂时未见任何其他登录方式
     *
     * @param page
     * @param type
     * @param userId
     * @param code
     */
    private void handleLoginByType(Page page, LoginType type, String userId, String code) {
        // 等待登录面板加载
        LoginHandle handler = loginHandlers.get(type);
        if (handler == null) {
            throw new IllegalArgumentException("不支持的登录模式: " + type.getMode());
        }
        handler.login(page, type, userId, code);
    }

    /**
     * 获取验证码图片，缓存上下文，并等待前端传值
     * @return
     */
    public CaptchaVO getCaptcha() {
        return browserPool.executeWithContext(context -> {

            Page page = context.newPage();
            page.navigate(loginURL);
            page.waitForLoadState(LoadState.NETWORKIDLE);

            // 截图验证码
            byte[] captchaImage = page.locator("#j_checkcodeImgCode41").screenshot();
            // 利用工号的唯一性
            // 缓存 page（注意：context 也要保持引用，并且不能随意清空状态）

            CaptchaVO vo = new CaptchaVO();
            vo.setCookies(context.cookies());
            vo.setCaptchaBase64(Base64.getEncoder().encodeToString(captchaImage));
            return vo;
        });
    }


    /**
     * 只通过未过期的cookie进行尝试登录
     * @param cmd
     * @return
     */
    @Override
    public LoginResultsVo loginByCookie(LoginRequestCommand cmd) {
        return browserPool.executeWithContext(context -> {
            // 直接看看这个cookie好不好用
            List<Cookie> cookies = cmd.getCookies();
            context.addCookies(cookies);
            Page page = context.newPage();
            // 访问登录页面
            page.navigate(loginURL);
            // NETWORKIDLE 不等于 "JS 执行完"。需要等待目标元素可交互。
            page.waitForLoadState(LoadState.LOAD);
            page.waitForLoadState(LoadState.DOMCONTENTLOADED);
            page.waitForLoadState(LoadState.NETWORKIDLE, new Page.WaitForLoadStateOptions().setTimeout(4000));

            if ( page.url().equals(loginURL) )
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), cmd.getUserId()+"：登录失败，登录凭证已过期，请重新登录！" + page.content(), ResultCodeEnum.UNAUTHORIZED.getCode());

            LoginResultsVo ret = new LoginResultsVo();
            // ret.setCookies(context.cookies(page.url()));
            ret.setHtmlDoc(page.textContent("body"));
            return ret;
        });
    }

    /**
     * 注销函数，操作缓存
     *
     * @return
     */
    @Override
    public String logout() {
        return "";
    }
}
