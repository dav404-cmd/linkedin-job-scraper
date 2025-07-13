import asyncio

from linkedin_scraper.linkedin_scraper import LINKEDIN_SCRAPER

async def run_scraper():
    try:
        scraper = LINKEDIN_SCRAPER()
        url = await scraper.get_url("machine learning engineer","United States")
        await scraper.scrape(url)
    except Exception  as e:
        print(f"[main/run_scraper] ! error {e}")

if __name__ == "__main__":
    asyncio.run(run_scraper())