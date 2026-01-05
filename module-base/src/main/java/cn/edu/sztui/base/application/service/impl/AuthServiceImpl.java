package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.dto.command.LoginRequestCommand;
import cn.edu.sztui.base.application.service.AuthService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.logintype.LoginType;
import cn.edu.sztui.base.domain.utils.PlaywrightBrowserPool;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.LoadState;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Objects;

import static cn.edu.sztui.base.application.handle.LoginService.loginURL;

@Service
@Slf4j
public class AuthServiceImpl implements AuthService {

    @Autowired
    private PlaywrightBrowserPool browserPool;

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


    /**
     * 多维度判断当前激活的登录方式
     * 维度1：读取页面authMethodIDs隐藏框的值
     * 维度2：检测哪个tabCon处于显示状态
     * 维度3：检测tabBar中选中的标签（dq类）
     *
     * @param page
     * @return
     */
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
     * 登录框架
     * @param cmd
     * @return
     */
    @Override
    public LoginResultsVo loginFrame(LoginRequestCommand cmd) {
        return browserPool.executeWithContext(context -> {
            Page page = context.newPage();
            // 访问登录页面
            page.navigate(loginURL);
            page.waitForLoadState(LoadState.NETWORKIDLE);
            LoginResultsVo ret = new LoginResultsVo();
            try {
                handleLoginByType(page, cmd.getLoginType(), cmd.getUserId(), cmd.getCode());
                // 返回结果
                ret.setStatusCode(200);
                ret.setMessage("登录成功！");
                ret.setCookies(context.cookies(loginURL));
                ret.setPage(page);
                return ret;
            } catch (Exception e) {
                log.error(e.getMessage(), e);
            }finally {
                ret.setStatusCode(500);
                ret.setMessage("登录失败！！！");
                return ret;
            }
        });
    }



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

            page.waitForSelector("input[id='" + LoginType.SMS.getUsernameInputId() + "']",new Page.WaitForSelectorOptions());
            page.waitForSelector("#" + LoginType.SMS.getTabConId(),new Page.WaitForSelectorOptions().setTimeout(4000));

            LoginResultsVo ret = new LoginResultsVo();
            try {
                Locator usernameInput = page.locator("input[id='" + LoginType.SMS.getUsernameInputId() + "']");
                usernameInput.clear();
                usernameInput.fill(id);
                page.locator("#" + LoginType.SMS.getTabConId()).click();

                page.waitForLoadState(LoadState.LOAD);
                page.waitForLoadState(LoadState.DOMCONTENTLOADED);
                page.waitForLoadState(LoadState.NETWORKIDLE);

                ret.setStatusCode(200);
                ret.setMessage("成功获取短信！");
                ret.setCookies(context.cookies(loginURL));
                ret.setPage(page);
            } catch (Exception e) {
                log.error(e.getMessage(), e);
                ret.setStatusCode(500);
                ret.setMessage("爬虫无法进行信息获取！！！");
            } finally {
                page.close();
                return ret;
            }
        });
    }


    /**
     * 根据登录方式执行对应操作（适配不同登录方式的输入框）
     *
     * @param page
     * @param type
     * @param userId
     * @param code
     */
    private static void handleLoginByType(Page page, LoginType type, String userId, String code) {

        // 等待当前登录方式的面板加载完成
        page.waitForSelector("#" + type.getTabConId(), new Page.WaitForSelectorOptions().setTimeout(1000));

        if (!type.getUsernameInputId().isEmpty()) {
            // 学号输入
            Locator usernameInput = page.locator("input[id='" + type.getUsernameInputId() + "']");
            // 等待输入框可点击，清除默认值（比如"工号"占位符）
            // usernameInput.waitFor(new Locator.WaitForOptions().setState(Locator.S.ENABLED));
            usernameInput.clear();
            usernameInput.fill(userId);

            // 输入验证码或者密码
            Locator codeInput = page.locator("input[id='" + type.getCodeInputId() + "']");
            // codeInput.waitFor(new Locator.WaitForOptions().setState(Locator.WaitForState.ENABLED));
            codeInput.clear();
            codeInput.fill(code);

            // 点击登录按钮（当前登录方式的登录按钮）
            Locator loginBtn = page.locator("#" + type.getTabConId() + " button.loginBt");
            if (loginBtn.isEnabled()) {
                loginBtn.click();
            }
        }

        // 无用户名输入框的登录方式（二维码/证书）
        handleNonInputLoginType(page, type);
        return;
    }

    /**
     * 处理无输入框的登录方式，暂无实现
     *
     * @param page
     * @param type
     */
    private static void handleNonInputLoginType(Page page, LoginType type) {
        switch (type) {
            case EPASS_QR:
                System.out.println("当前为e账通二维码登录，等待扫码...");
                page.waitForSelector("#QRImage", new Page.WaitForSelectorOptions().setTimeout(10000));
                break;
            case WECHAT:
                System.out.println("当前为微信二维码登录，等待扫码...");
                page.waitForSelector("#wx_QRImage", new Page.WaitForSelectorOptions().setTimeout(10000));
                break;
            case DINGDING:
                System.out.println("当前为钉钉登录，等待授权...");
                page.waitForSelector("#login_container", new Page.WaitForSelectorOptions().setTimeout(10000));
                break;
            case CERT:
                System.out.println("当前为证书认证，点击登录按钮触发证书验证...");
                page.locator("#tab2Con button.loginBt").click();
                break;
            default:
                System.out.println("暂不支持的登录方式：" + type.name());
        }
    }

}
