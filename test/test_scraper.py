import pytest
from linkedin_scraper.linkedin_scraper import LINKEDIN_SCRAPER

@pytest.mark.asyncio
async def test_get_url():
    scraper = LINKEDIN_SCRAPER()
    url = await scraper.get_url("machine learning engineer", "Remote")
    assert "machine%20learning%20engineer" in url
    assert "Remote" in url


@pytest.mark.asyncio
async def test_scrape_jobs():
    limit = 3
    scraper = LINKEDIN_SCRAPER()
    url = await scraper.get_url("machine learning engineer", "United States")
    jobs = await scraper.scrape(url, limit=limit, test_mode=True)

    assert isinstance(jobs, list), "Expected scrape() to return a list"
    assert len(jobs) == limit, f"Expected {limit} jobs, but got {len(jobs)}"

    for job in jobs:
        assert "title" in job and job["title"] != "N/A", "Missing or invalid job title"
        assert "company" in job and job["company"] != "N/A", "Missing or invalid company name"
        assert "job_id" in job and job["job_id"] != "N/A", "Missing or invalid job ID"
        assert "url" in job and job["url"].startswith("https://www.linkedin.com/jobs/view/"), "Invalid job URL"