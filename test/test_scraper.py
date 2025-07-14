import pytest
import asyncio

from linkedin_scraper.linkedin_scraper import LINKEDIN_SCRAPER

@pytest.mark.asyncio
async def test_get_url():
    url = await LINKEDIN_SCRAPER.get_url("machine learning engineer", "Remote")
    assert "machine%20learning%20engineer" in url
    assert "Remote" in url
    assert url.startswith("https://www.linkedin.com/jobs/search")

@pytest.mark.asyncio
def test_parse_preferences():
    scraper = LINKEDIN_SCRAPER()

    preferences = [
        "Full-Time",
        "Remote",
        "$80,000 - $100,000"
    ]

    job_type, workplace_type, salary = scraper.parse_preferences(preferences)
    assert job_type.lower() == "full-time"
    assert workplace_type.lower() == "remote"
    assert "$" in salary

@pytest.mark.asyncio
async def test_parse_preferences_no_match():
    scraper = LINKEDIN_SCRAPER()

    preferences = [
        "Volunteer",
        "On vacation",
        "Unpaid"
    ]

    job_type, workplace_type, salary = scraper.parse_preferences(preferences)
    assert job_type == "N/A"
    assert workplace_type == "N/A"
    assert salary == "N/A"
