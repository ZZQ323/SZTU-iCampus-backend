package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.loginhandle.LoginHandle;
import cn.edu.sztui.base.domain.model.loginhandle.LoginType;
import cn.edu.sztui.base.domain.model.loginhandle.impl.*;
import cn.edu.sztui.base.domain.utils.PlaywrightBrowserPool;
import cn.edu.sztui.base.infrastructure.persistence.util.LoginSessionCacheUtil;
import cn.edu.sztui.common.util.enums.ResultCodeEnum;
import cn.edu.sztui.common.util.enums.SysReturnCode;
import cn.edu.sztui.common.util.exception.BusinessException;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.LoadState;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.util.Map;
import java.util.Objects;

import static cn.edu.sztui.base.domain.model.loginhandle.LoginHandle.loginURL;

@Service
@Slf4j
public class AuthServiceImpl implements AuthService {

    @Resource
    private PlaywrightBrowserPool browserPool;

    /**
     * 多维度判断当前激活的登录方式
     * 维度1：读取页面authMethodIDs隐藏框的值
     * 维度2：检测哪个tabCon处于显示状态
     * 维度3：检测tabBar中选中的标签（dq类）
     *
     * @return
     */

    @Override
    public LoginType loginCheck() {
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true));
            BrowserContext context = browser.newContext(new Browser.NewContextOptions().setIgnoreHTTPSErrors(true));
            Page page = context.newPage();

            // 访问登录页面
            page.navigate(loginURL);
            page.waitForLoadState(LoadState.NETWORKIDLE);

            LoginType ret = getCurrentLoginType(page);
            if (Objects.isNull(ret)) {
                throw new RuntimeException("无法判断登录类型");
            }
            // 这个时候就进行请求，同时进行跳转
            if (ret == LoginType.SMS) {
                Locator sendSmsBtn = page.locator("#smsBtn1");
                if (sendSmsBtn.isEnabled()) {
                    sendSmsBtn.click();
                    System.out.println("已点击短信验证码发送按钮，等待60秒倒计时...");
                    page.waitForTimeout(2000); // 等待发送请求完成
                }
            }
            return ret;
        }
    }

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

    @Resource
    private LoginSessionCacheUtil loginSessionCacheUtil;

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
            try {
                // 访问登录页面
                page.navigate(loginURL);
                // NETWORKIDLE 不等于 "JS 执行完"。需要等待目标元素可交互。
                page.waitForLoadState(LoadState.LOAD);
                page.waitForLoadState(LoadState.DOMCONTENTLOADED);
                page.waitForLoadState(LoadState.NETWORKIDLE);

                handleLoginByType(page, cmd.getLoginType(), cmd.getUserId(), cmd.getCode());

                // 等待登录响应，同时执行登录操作
                Response loginResponse = page.waitForResponse(
                    resp -> resp.url().contains("login") && resp.ok(),
                    () -> handleLoginByType(page, cmd.getLoginType(), cmd.getUserId(), cmd.getCode())
                );
                // 等待登录后页面稳定
                page.waitForLoadState(LoadState.LOAD);
                page.waitForLoadState(LoadState.DOMCONTENTLOADED);
                page.waitForLoadState(LoadState.NETWORKIDLE,new Page.WaitForLoadStateOptions().setTimeout(10000));

                // 验证登录是否成功（避免获取到错误页面的cookies）
                String currentUrl = page.url();
                if (page.content().contains("error") || currentUrl.equals(loginURL))
                    throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(),"登录失败：页面未跳转至登录成功页，当前URL=" + currentUrl,ResultCodeEnum.BAD_REQUEST.getCode());

                // 获取登录后的上下文信息
                LoginResultsVo ret = new LoginResultsVo();
                ret.setCookies(context.cookies(loginURL));
                ret.setPage(page);
                if( Objects.isNull( ret.getCookies() ) || Objects.isNull( ret.getPage() ) ){
                    throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "爬虫登录失败"+page.content(), ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
                }
                log.info("用户{}登录成功，已获取cookies", cmd.getUserId());
                // 登录成功后保存
                loginSessionCacheUtil.saveCookies(cmd.getUserId(), context.cookies());

                return ret;
            } catch (Exception e) {
                log.error(e.getMessage(), e);
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "爬虫无法进行登录！！", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
            }
        });
    }

    /**
     * 只获取短信，获取全新后就清空context
     *
     * @param id
     * @return
     */
    @Override
    public LoginResultsVo getSms(String id) {
        return browserPool.executeWithContext(context -> {
            Page page = context.newPage();
            // 访问登录页面
            page.navigate(loginURL);
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

                loginSessionCacheUtil.saveCookies(id, context.cookies());
                ret.setCookies(context.cookies(loginURL));
                ret.setPage(page);
                return ret;
            } catch (Exception e) {
                log.error(e.getMessage(), e);
                throw new BusinessException(SysReturnCode.BASE_PROXY.getCode(), "爬虫无法进行验证码获取！！", ResultCodeEnum.INTERNAL_SERVER_ERROR.getCode());
            }
        });
    }

    @Resource
    private Map<LoginType, LoginHandle> loginHandlers;

    /**
     * 【设计模式】
     *
     * 在登录框架中，经过测试发现，如果已有cookie的话，可以使用密码登录（是不是什么时候的cookie都行呢？）；
     * 但如果什么都没有就只能使用验证码登录；
     * 暂时未见任何其他登录方式
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
     * 注销函数，操作缓存
     *
     * @return
     */
    @Override
    public String logout() {
        return "";
    }
}
