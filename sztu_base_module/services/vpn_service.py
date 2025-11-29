# from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from config import settings

async def login_vpn(username: str, password: str):
    result = {"cookies": [], "html": "", "json_responses": []}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        def log_response(response):
            try:
                if "application/json" in response.headers.get("content-type", ""):
                    result["json_responses"].append({
                        "url": response.url,
                        "data": response.json()
                    })
            except:
                pass

        page.on("response", log_response)

        # 打开学校 webvpn 入口
        await page.goto(settings.VPN_URL)
        # 会自动跟随大量重定向直到出现登录页
        await page.wait_for_load_state("networkidle")
        # 输入学号密码
        await page.fill("input[id='j_username']", username)
        await page.fill("input[id='j_password']", password)
        # 点击登录按钮
        await page.click("button[id='loginButton'][type='button']")
        # 等待登录完成
        await page.wait_for_load_state("networkidle")
        result["cookies"] = await context.cookies()
        result["html"] = await page.content()
    return result
