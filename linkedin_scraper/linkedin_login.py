import logging
from playwright.async_api import Page,BrowserContext
import asyncio
import os

from linkedin_scraper.xpaths import EMAIL_FIELD,PASSWORD_FIELD,SUBMIT_BTN
from utils.logger import get_logger

login_log = get_logger("linkedin/login")

async def store_cookies(context, env_file_path=".env"):
    try:
        cookies_all = await context.cookies()
        li_at_cookie = next((cookie for cookie in cookies_all if cookie["name"] == "li_at"), None)
        if li_at_cookie:
            # Read existing .env lines (if any)
            if os.path.exists(env_file_path):
                with open(env_file_path, "r") as f:
                    lines = f.readlines()
            else:
                lines = []

            # Replace or add LINKEDIN_COOKIES entry
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("LINKEDIN_COOKIES="):
                    lines[i] = f"LINKEDIN_COOKIES={li_at_cookie['value']}\n"
                    updated = True
                    break
            if not updated:
                lines.append(f"LINKEDIN_COOKIES={li_at_cookie['value']}\n")

            with open(env_file_path, "w") as f:
                f.writelines(lines)

            login_log.info(f"[store_cookies] * Stored li_at into '{env_file_path}' as LINKEDIN_COOKIES")
    except Exception as e:
        login_log.error(f"[store_cookies] ! Error: {e}")



async def login(context:BrowserContext,page:Page,email:str = None,password:str = None,cookies:str = None) -> bool:
    try:
        if cookies:
            await context.add_cookies([{
                "name": "li_at",
                "value": cookies,
                "domain": ".linkedin.com",
                "path": "/",
                "secure": True,
                "httpOnly": True,
                "sameSite": "Lax"
            }])
        await page.goto("https://www.linkedin.com/feed/")
        await asyncio.sleep(3)
        if await page.locator("a[href*='/in/']").first.is_visible():
            login_log.info(" * cookies login success.")
            return True
        login_log.error("[login] ! cookies login failed.")

        if email and password:
            await page.goto("https://www.linkedin.com/login")
            await asyncio.sleep(2)
            await page.fill(EMAIL_FIELD,email)
            await page.fill(PASSWORD_FIELD,password)
            await page.click(SUBMIT_BTN)
            await asyncio.sleep(3)

            if await page.locator("a[href*='/in/']").first.is_visible():
                login_log.info("[login] * credentials login success.")
                await store_cookies(context)
                return True


            login_log.error("[login] ! credentials login failed.")
        login_log.error("[login] ! login failed invalid cookies or creds.")
    except Exception as e:
        login_log.error(f"[login] ! Error : {e}")
        return False