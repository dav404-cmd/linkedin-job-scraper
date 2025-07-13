import pytest
from linkedin_scraper.linkedin_scraper import LINKEDIN_SCRAPER

@pytest.mark.asyncio
async def test_get_url():
    scraper = LINKEDIN_SCRAPER()
    url = await scraper.get_url("machine learning engineer", "Remote")
    assert "machine%20learning%20engineer" in url
    assert "Remote" in url