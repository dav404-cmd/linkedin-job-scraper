# LinkedIn Job Scraper

A Python-powered tool for automatically extracting job postings from LinkedIn.  
This project automates the collection of LinkedIn job data for research, analytics, or personal job tracking.

---

## Author's Note

> This project is originally part of a bigger system.  
> I am currently dissecting it into smaller, standalone modules for easier development, reuse, and open source contribution.

---

## Features

- **Automated Browser Control:** Uses Playwright to interact with LinkedIn like a real user.
- **Login Support:** Supports both credential and cookie-based login (set via `.env`).
- **Flexible Search:** Search jobs by title and location.
- **Detailed Data Extraction:** Collects job title, company, location, post date, salary, job type, workplace type, and more.
- **Batch Processing:** Writes results in batches to CSV for large-scale runs.
- **Pagination & Scrolling:** Automatically goes through multiple result pages and scrolls job lists.
- **Proxy Support:** Integrates with a ProxyManager to enable requests through HTTP proxies, supporting geo-unblocking and enhancing scraping reliability.
- **Error Handling:** Retries and fallback logic for reliability.
- **Test Mode:** Save results to a separate directory during development.

---

## Usage

### Prerequisites

- Python 3.8+
- [Playwright](https://playwright.dev/python/)
- [pandas](https://pandas.pydata.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [parsel](https://pypi.org/project/parsel/)
- [aiohttp](https://docs.aiohttp.org/)
- [pytest](https://docs.pytest.org/)

Install dependencies:

```bash
pip install playwright pandas python-dotenv parsel aiohttp pytest 
playwright install
```
or 
```bash
pip install -r requirements.txt
playwright install
```

### Environment Variables

Create a `.env` file in your `linkedin_scraper` directory:

```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_COOKIES=your_cookies_string   # Optional
```

### Running the Scraper

The main entry point is `main.py`:

```bash
python main.py
```

This will:

- Start a headless browser (optionally through a proxy)
- Log into LinkedIn (from `.env`)
- Search for jobs (default: "machine learning engineer" in "United States")
- Scrape up to 30 jobs (adjustable)
- Save results to `data/jobs_data/linkedin_jobs.csv`

#### Customizing the Search

Change the job query and location in `main.py`:

```python
url = await scraper.get_url("software engineer", "Canada")
await scraper.scrape(url, limit=100)
```

### Output

- Scraped jobs saved as CSV in `data/jobs_data/`
- Batch files for large runs
- Test mode saves to `data/test_data/`

---

## Project Structure

```
linkedin-job-scraper/
│
├── linkedin_scraper/
│   ├── .env                  # Your LinkedIn credentials (not included)
│   ├── linkedin_scraper.py   # Main scraping logic
│   ├── xpaths.py             # XPaths for LinkedIn elements
│   └── linkedin_login.py     # Login handling
├── proxy/
│   └── proxy_manager.py      # Proxy management for rotating proxies and geo-unblocking
├── utils/
│   └── logger.py             # Logging utility
├── data/
│   ├── jobs_data/            # Output CSVs
│   └── test_data/            # Test output
├── main.py                   # Entry script
└── README.md
```

### Module Descriptions

- **linkedin_scraper/**  
  Main scraping logic, LinkedIn login process, XPaths for scraping, and environment configuration.
- **proxy/**  
  Contains `proxy_manager.py` which handles HTTP proxies, enabling features like IP rotation and bypassing geo-restrictions.
- **utils/**  
  Contains `logger.py` for standardized logging throughout the project.
- **data/**  
  Output folders for scraped job data (production and test/batch outputs).

---

## Disclaimer

This tool is for educational and research purposes only. Scraping LinkedIn may violate their terms of service; use responsibly and at your own risk.

---

**Author:** [dav404-cmd](https://github.com/dav404-cmd)