from playwright.sync_api import sync_playwright
from config import settings

def login_vpn(username: str, password: str):
    result = {"cookies": [], "html": "", "json_responses": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

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
        page.goto(settings.VPN_URL)
        page.wait_for_load_state("networkidle")
        page.fill("input[id='j_username']", username)
        page.fill("input[id='j_password']", password)
        page.click("button[id='loginButton'][type='button']")
        page.wait_for_load_state("networkidle")

        result["cookies"] = context.cookies()
        result["html"] = page.content()

    return result
