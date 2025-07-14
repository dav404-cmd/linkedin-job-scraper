import asyncio

from linkedin_scraper.linkedin_scraper import LINKEDIN_SCRAPER
from utils.logger import get_logger

main_log = get_logger("main")

async def run_scraper():
    try:
        scraper = LINKEDIN_SCRAPER()
        url = await scraper.get_url("machine learning engineer","United States")
        await scraper.scrape(url,limit=30,test_mode=False)
    except Exception  as e:
        main_log.error(f"[run_scraper] ! error {e}")

if __name__ == "__main__":
    asyncio.run(run_scraper())