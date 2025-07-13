import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

from linkedin_scraper.linkedin_login import login
from linkedin_scraper.xpaths import JOB_CARD
from utils.logger import get_logger

linkedin_log = get_logger("linkedin_scraper")

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
                linkedin_log.error(" ! failed to login")
                await self.close_browser()

        await self.page.goto(url)
        await asyncio.sleep(3)


        try:
            job_cards = await self.page.query_selector_all(JOB_CARD)
            if not job_cards:
                linkedin_log.warning(" ! No job card found;waiting 2 sec;retrying..")
                await asyncio.sleep(2)
                job_cards = await self.page.query_selector_all(JOB_CARD)
                if not job_cards:
                    linkedin_log.error(" ! JOB_CARD not found.")
                    await self.close_browser()
        except Exception as e:
            linkedin_log.error(f" ! error in finding job_cards :  {e}")
            await self.close_browser()
        print(f"found {len(job_cards)}")
        await self.close_browser()


if __name__ == "__main__":
    scraper = LINKEDIN_SCRAPER()
    url_fetch = scraper.get_url("machine learning engineer","United States")
    run = scraper.scrape(url_fetch)
    asyncio.run(run)


