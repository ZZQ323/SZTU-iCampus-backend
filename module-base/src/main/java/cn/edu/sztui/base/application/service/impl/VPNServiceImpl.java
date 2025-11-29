package cn.edu.sztui.base.application.service.impl;

import cn.edu.sztui.base.application.service.VPNService;
import com.microsoft.playwright.*;
import com.microsoft.playwright.options.Cookie;
import com.microsoft.playwright.options.LoadState;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@Slf4j
public class VPNServiceImpl implements VPNService {

    /**
     * @param username
     * @param password
     * @return
     */
    @Override
    public String login(String username, String password) {
        if(username == null || username.isEmpty()) {
            throw new IllegalArgumentException("Username required");
        }
        if(password == null || password.isEmpty()) {
            throw new IllegalArgumentException("Password required");
        }
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().launch(
                    new BrowserType.LaunchOptions().setHeadless(true)
            );

            BrowserContext context = browser.newContext(
                    new Browser.NewContextOptions().setIgnoreHTTPSErrors(true)
            );

            Page page = context.newPage();

            // 访问登录页面
            page.navigate("https://home.sztu.edu.cn/bmportal");
            page.waitForLoadState(LoadState.NETWORKIDLE);
            page.waitForTimeout(2000);

            // 填写表单
            page.locator("input[id='j_username']").fill(username);
            page.locator("input[id='j_password']").fill(password);

            // ✅ 关键修改：使用first()只点击第一个按钮
            page.locator("button[id='loginButton']").first().click();

            // 等待登录完成
            page.waitForLoadState(LoadState.NETWORKIDLE);
            page.waitForTimeout(60000);

            String finalUrl = page.url();
            System.out.println("最终URL: " + finalUrl);
            List<Cookie> cookies = context.cookies();
            System.out.println("获得 " + cookies.size() + " 个Cookie");
            String content = page.content();
            // 检查是否真的加载完成
            if (content.contains("Loading...") && !content.contains("bmportal-page")) {
                System.out.println("⚠️ 页面可能未完全加载");
            } else {
                System.out.println("✓ 登录成功");
            }
            // 返回结果
            return content;
        } catch (Exception e) {
            throw new RuntimeException("登录失败: " + e.getMessage(), e);
        }
    }
}
