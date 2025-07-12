import asyncio

from linkedin_scraper.linkedin_scraper import LINKEDIN_SCRAPER

def run_scraper():
    try:
        scraper = LINKEDIN_SCRAPER()
        asyncio.run(scraper.scrape())
    except Exception  as e:
        print(f"[main/run_scraper] ! error {e}")

if __name__ == "__main__":
    run_scraper()