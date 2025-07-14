import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
import pandas as pd
import time
from parsel import Selector
import re

from linkedin_scraper.linkedin_login import login
from linkedin_scraper.xpaths import JOB_CARD,SCROLL_CONTAINER,NEXT_BTN,TITLE,COMPANY,POST_DATE,LOCATION
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

    @staticmethod
    def safe_get(sel, xpath):
        val = sel.xpath(xpath).get()
        return val.strip() if val else "N/A"

    async def fall_back(self,last_url):
        if not last_url:
            linkedin_log.warning("Fallback aborted — no last URL.")
            return False
        retry = 1
        max_retry = 3
        while retry < max_retry:
            linkedin_log.info(f"Attempting to fall_back to : {last_url},attempt = {retry}")
            try:
                await self.close_browser()
                await self.start_browser()
                email = os.getenv("LINKEDIN_EMAIL")
                password = os.getenv("LINKEDIN_PASSWORD")
                cookies = os.getenv("LINKEDIN_COOKIES")
                fallback_login = await login(self.context,self.page,email,password,cookies)
                if not fallback_login:
                    linkedin_log.warning("(fallback): !! cookies login failed or redirected — trying email/password...")
                    await self.close_browser()
                    await self.start_browser()
                    fallback_login = await login(self.context,self.page,email,password,cookies=None)
                    if not fallback_login:
                        linkedin_log.error("(fallback): !! Login with email/password also failed.")
                        return []
                    await self.page.goto(last_url)
            except Exception as e:
                linkedin_log.error(f"!!ERROR in fallback : {e}")
                retry += 1
        linkedin_log.error(f"!!Failed to fall_back.")
        return False

    async def scroll_job_list_container(self, container_selector=SCROLL_CONTAINER):
        container = await self.page.query_selector(container_selector)
        if not container:
            linkedin_log.error("!! Scroll container not found.")
            return

        previous_height = 0
        same_scroll_count = 0

        for _ in range(30):  # Max scroll attempts
            await self.page.evaluate(
                """(container) => {
                    container.scrollBy(0, container.clientHeight);
                }""",
                container,
            )
            await asyncio.sleep(1.2)  # Wait for new jobs to load

            current_height = await self.page.evaluate(
                "(container) => container.scrollHeight", container
            )

            if current_height == previous_height:
                same_scroll_count += 1
            else:
                same_scroll_count = 0

            previous_height = current_height

            if same_scroll_count >= 3:
                linkedin_log.info("* Finished scrolling — no new job cards loading.")
                break

    async def click_next_button(self):
        try:
            next_btn = await self.page.query_selector(NEXT_BTN)
            if next_btn:
                await next_btn.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                await next_btn.click()
                await self.page.wait_for_timeout(3000)  # wait for new cards to load
                return True
            linkedin_log.error("! Next button not found or disabled")
            return False
        except Exception as e:
            linkedin_log.error(f"! Error clicking next button: {e}")
            return False

    async def scrape(self,url,limit = 30,test_mode = True):
        start_time = time.time()
        await self.start_browser()
        load_dotenv()

        # Access values
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        cookies = os.getenv("LINKEDIN_COOKIES")

        output_path = os.path.join("data", "jobs_data", "linkedin_jobs.csv")
        output_path2 = os.path.join("data", "jobs_data", "jobs_batches_linkedin.csv")
        test_batched_path = os.path.join("data", "test_data", "batched_jobs_test.csv")
        test_path = os.path.join("data", "test_data", "linkedin_test_data.csv")

        output_file = test_path if test_mode else output_path
        output_file2 = test_batched_path if test_mode else output_path2

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

        jobs = []
        job_batches = []
        run_cycles = 0
        page_num = 1
        seen_ids = set()
        job_count = 0
        last_url = None

        while job_count < limit:
            linkedin_log.info(f"* Processing page {page_num}...")

            try:
                await self.scroll_job_list_container()
                job_cards = await self.page.query_selector_all(JOB_CARD)
                if not job_cards:
                    linkedin_log.warning("No cards found. Waiting 2s and retrying...")
                    await asyncio.sleep(2)
                    job_cards = await self.page.query_selector_all(JOB_CARD)
                    if not job_cards:
                        success = await self.click_next_button()
                        linkedin_log.debug("click error next btn")
                        if not success:
                            break
                        page_num += 1
                        continue

                for idx, card in enumerate(job_cards):
                    # linkedin_log.debug(f"* Found {len(job_cards)} job cards on page {page_num}")

                    await card.scroll_into_view_if_needed()
                    await asyncio.sleep(1)

                    try:
                        await card.click()
                    except Exception as e:
                        linkedin_log.error(f"! Failed to click card {idx}: {e}")
                        continue

                    await asyncio.sleep(3)
                    html = await self.page.content()
                    sel = Selector(html)

                    card_href = await card.query_selector("a[href*='/jobs/view/']")
                    href = await card_href.get_attribute("href") if card_href else None
                    job_id_match = re.search(r'/jobs/view/(\d+)', href) if href else None
                    job_id = job_id_match.group(1) if job_id_match else "N/A"

                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    job_url = f"https://www.linkedin.com/jobs/view/{job_id}/" if job_id != "N/A" else "N/A"

                    last_url = job_url

                    preferences = sel.xpath(
                        "(//div[contains(@class,'job-details-fit-level-preferences')]//strong)/text()").getall()
                    preferences = [p.strip() for p in preferences if p.strip()]

                    job_type = next(
                        (p for p in preferences if
                         any(x in p.lower() for x in ["full-time", "part-time", "internship"])),
                        "N/A")
                    workplace_type = next(
                        (p for p in preferences if
                         any(x in p.lower() for x in ["remote", "on-site", "hybrid", "on site"])),
                        "N/A")
                    salary = next((p for p in preferences if "$" in p or "hr" in p.lower() or "-" in p), "N/A")

                    jobs.append(jobs_data := {
                        "title": self.safe_get(sel, TITLE),
                        "company": self.safe_get(sel, COMPANY),
                        "post_date": self.safe_get(sel, POST_DATE),
                        "job_id": job_id,
                        "location": self.safe_get(sel, LOCATION),
                        "salary": str(salary),
                        "job_type": job_type,
                        "workplace_type": workplace_type,
                        "url": job_url
                    })

                    job_batches.append(jobs_data)

                    job_count += 1
                    linkedin_log.info(f"job count : {job_count}")

                    if job_count > 0 and job_count % 100 == 0:
                        df = pd.DataFrame(job_batches)
                        run_cycles += 1
                        if not df.empty:
                            file_is_empty = not os.path.exists(output_file2) or os.stat(output_file2).st_size == 0
                            df.to_csv(output_file2, mode="a", header=file_is_empty, index=False)
                            linkedin_log.info(
                                f"** Scraped {len(job_batches)} jobs,completed {run_cycles} cycle, Successfully . ")
                            job_batches.clear()
                            # Calculate the runtime each _ jobs
                            elapsed = time.time() - start_time
                            linkedin_log.info(f"** Elapsed time: {elapsed:.2f}s for {job_count} jobs")
                            # rest.
                            linkedin_log.info("Resting for 10 sec.....")
                            await asyncio.sleep(10)

                    if job_count >= limit:
                        break

                    await asyncio.sleep(2)

            except Exception as e:
                linkedin_log.error(f"!!ERROR in while scraping : {e}")
                try:
                    linkedin_log.info(f"*Trying fall_back.")
                    await self.fall_back(last_url)
                    continue
                except Exception as e:
                    linkedin_log.error(f"!!ERROR while executing fall_back : {e}")
                    await self.close_browser()

            # Click next after finishing all cards on the page
            next_clicked = await self.click_next_button()
            linkedin_log.info("next_btn to page clicked.")
            if not next_clicked:
                linkedin_log.info("No more pages or cannot click next.")
                break
            page_num += 1

        await self.close_browser()
        linkedin_log.info(f"path : {output_file}")
        df = pd.DataFrame(jobs)
        if not df.empty:
            df.to_csv(output_file, index=False)
            linkedin_log.info(f"Scraped {len(jobs)} jobs")
            linkedin_log.info(f"** Finished scraping. Total jobs collected: {job_count}")
        return jobs


if __name__ == "__main__":
    scraper = LINKEDIN_SCRAPER()
    url_fetch = scraper.get_url("machine learning engineer","United States")
    run = scraper.scrape(url_fetch)
    asyncio.run(run)


