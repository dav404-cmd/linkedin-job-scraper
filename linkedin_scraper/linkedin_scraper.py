import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
import logging

from linkedin_scraper.linkedin_login import login

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LINKEDIN_SCRAPER:
    def __init__(self):
        self.playwright = None
        self.page = None
        self.browser = None
        self.context = None

    async def start_browser(self):
        self.playwright = await async_playwright().start()

        launch_args = {"headless": False}

        self.browser = await self.playwright.chromium.launch(**launch_args)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    @staticmethod
    async def get_url(query,location):
        query_clean = query.replace(" ","%20")
        clean_location = location.replace(" ","%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={query_clean}&location={clean_location}"
        return str(url)

    async def scrape(self,url):
        await self.start_browser()
        load_dotenv()

        # Access values
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        cookies = os.getenv("LINKEDIN_COOKIES")

        success = await login(self.context,self.page,email = email,password=password,cookies=cookies)
        if not success:
            await self.close_browser()
            await self.start_browser()
            success_cred = await login(self.context,self.page,email = email,password=password,cookies=None)
            if not success_cred:
                logger.error("[scraper/login] ! failed to login")
                await self.close_browser()
        print(url)
        await self.page.goto(url)

        await asyncio.sleep(3)
        await self.close_browser()


if __name__ == "__main__":
    scraper = LINKEDIN_SCRAPER()
    url_fetch = scraper.get_url("machine learning engineer","United States")
    run = scraper.scrape(url_fetch)
    asyncio.run(run)


