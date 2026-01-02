package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.service.LoginService;
import cn.edu.sztui.base.application.vo.LoginResultsVo;
import cn.edu.sztui.base.domain.model.LoginType;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.LoadState;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import static java.rmi.server.LogStream.log;

@Service
@Slf4j
public class LoginServiceImpl implements LoginService {


    final String loginURL ="https://home.sztu.edu.cn/bmportal";
    /**
     * @param userId
     * @param password
     * @return
     */
    @Override
    public LoginResultsVo loginWithPasswd(String userId, String password) {
        if(userId == null || userId.isEmpty()) {
            throw new IllegalArgumentException("Username required");
        }
        if(password == null || password.isEmpty()) {
            throw new IllegalArgumentException("Password required");
        }
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true));
            BrowserContext context = browser.newContext(new Browser.NewContextOptions().setIgnoreHTTPSErrors(true));

            Page page = context.newPage();

            // 访问登录页面
            page.navigate(loginURL);
            page.waitForLoadState(LoadState.NETWORKIDLE);
            page.waitForTimeout(2000);

            // 填写表单
            // page.locator("input[id='j_username']").fill(userId);
            // page.locator("input[id='j_password']").fill(password);
            // ✅ 关键修改：使用first()只点击第一个按钮
            // page.locator("button[id='loginButton']").first().click();
            // 等待登录完成
            // page.waitForLoadState(LoadState.NETWORKIDLE);
            // page.waitForTimeout(60000);

            // 2. 多维度判断当前激活的登录方式（核心：交叉验证，避免单一维度失效）
            LoginType currentLoginType = getCurrentLoginType(page);

            // 3. 根据登录方式定位元素并执行操作
            if (currentLoginType == null) {
                log.error("未识别到激活的登录方式，报错！！");
                // fallbackLocator(page, "你的工号", "你的密码/验证码");
                LoginResultsVo ret = new LoginResultsVo();
                ret.setStatusCode(400);
                ret.setMessage("未识别到激活的登录方式，无法处理");
                return ret;
            }

            System.out.println("当前激活的登录方式：" + currentLoginType.name() + "（ID：" + currentLoginType.getAuthId() + "）");
            handleLoginByType(page, currentLoginType, "你的工号", "你的密码/验证码");

            // 返回结果
            LoginResultsVo ret = new LoginResultsVo();
            ret.setStatusCode(200);
            ret.setMessage("登录成功！");
            ret.setUserId(userId);
            ret.setPasswd(password);
            ret.setCookies(context.cookies(loginURL));
            ret.setPage(page);
            return ret;
        } catch (Exception e) {
            throw new RuntimeException("登录失败: " + e.getMessage(), e);
        }
    }

    /**
     * 多维度判断当前激活的登录方式（鲁棒性核心）
     * 维度1：读取页面authMethodIDs隐藏框的值（最直接）
     * 维度2：检测哪个tabCon处于显示状态（视觉验证）
     * 维度3：检测tabBar中选中的标签（dq类）
     */
    private static LoginType getCurrentLoginType(Page page) {
        // 维度1：优先读取页面内置的authMethodIDs（最可靠）
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
                System.out.println("authMethodIDs解析失败：" + authMethodIdsStr);
            }
        }

        // 维度2：遍历所有tabCon，找显示状态的（兜底维度1失效）
        for (LoginType type : LoginType.values()) {
            Locator tabCon = page.locator("#" + type.getTabConId());
            if (tabCon.isVisible() && "block".equals(tabCon.evaluate("el => el.style.display").toString())) {
                return type;
            }
        }

        // 维度3：检测tabBar中选中的标签（dq类）（最后兜底）
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
     * 根据登录方式执行对应操作（适配不同登录方式的输入框）
     */
    private static void handleLoginByType(Page page, LoginType type, String userId, String code) {
        // 等待当前登录方式的面板加载完成
        page.waitForSelector("#" + type.getTabConId(), new Page.WaitForSelectorOptions().setTimeout(3000));

        // 1. 用户名输入（优先用ID，兜底用name包含j_username）
        Locator usernameInput;
        if (!type.getUsernameInputId().isEmpty()) {
            usernameInput = page.locator("input[id='" + type.getUsernameInputId() + "']");
        } else {
            // 无用户名输入框的登录方式（二维码/证书）
            handleNonInputLoginType(page, type);
            return;
        }

        // 等待输入框可点击，清除默认值（比如"工号"占位符）
        usernameInput.waitFor(new Locator.WaitForOptions().setState(Locator.WaitForState.ENABLED));
        usernameInput.clear();
        usernameInput.fill(userId);

        // 2. 密码/验证码输入（不同登录方式适配）
        if (!type.getCodeInputId().isEmpty()) {
            Locator codeInput = page.locator("input[id='" + type.getCodeInputId() + "']");
            codeInput.waitFor(new Locator.WaitForOptions().setState(Locator.WaitForState.ENABLED));
            codeInput.clear();
            codeInput.fill(code);

            // 特殊处理：短信验证码需要点击"发送验证码"按钮
            if (type == LoginType.SMS) {
                Locator sendSmsBtn = page.locator("#smsBtn1");
                if (sendSmsBtn.isEnabled()) {
                    sendSmsBtn.click();
                    System.out.println("已点击短信验证码发送按钮，等待60秒倒计时...");
                    page.waitForTimeout(2000); // 等待发送请求完成
                }
            }
        }

        // 3. 点击登录按钮（当前登录方式的登录按钮）
        Locator loginBtn = page.locator("#" + type.getTabConId() + " button.loginBt");
        if (loginBtn.isEnabled()) {
            loginBtn.click();
        }
    }

    /**
     * 处理无输入框的登录方式（二维码/证书等）
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

    /**
     * 终极兜底定位（所有判断失效时，基于j_username共性）
     * 核心：所有登录方式的用户名输入框都包含name="j_username"，以此兜底
     */
    private static void fallbackLocator(Page page, String userId, String code) {
        // 兜底定位1：name包含j_username的输入框（所有登录方式的共性）
        Locator usernameInput = page.locator("input[name*='j_username']").first();
        if (usernameInput.isEnabled()) {
            usernameInput.clear();
            usernameInput.fill(userId);
            System.out.println("兜底定位：用户名输入框（name包含j_username）");
        } else {
            // 兜底定位2：placeholder/value包含"工号"的输入框
            usernameInput = page.locator("input[placeholder*='工号'], input[value*='工号']").first();
            usernameInput.clear();
            usernameInput.fill(userId);
            System.out.println("兜底定位：工号输入框（placeholder/value包含工号）");
        }

        // 密码/验证码兜底：优先密码框，其次验证码框
        Locator pwdInput = page.locator("input[type='password'], input[name*='j_password']").first();
        if (pwdInput.isEnabled()) {
            pwdInput.clear();
            pwdInput.fill(code);
        } else {
            Locator codeInput = page.locator("input[name*='sms_checkcode'], input[name*='j_otpcode']").first();
            if (codeInput.isEnabled()) {
                codeInput.clear();
                codeInput.fill(code);
            }
        }

        // 点击第一个可用的登录按钮
        Locator loginBtn = page.locator("button.loginBt").first();
        if (loginBtn.isEnabled()) {
            loginBtn.click();
        }
    }
}
