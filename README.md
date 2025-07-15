# LinkedIn Job Scraper

A Python-powered scraper for automatically extracting job postings from LinkedIn. This project is designed to automate the collection of LinkedIn job data for research, analytics, or personal job tracking.

## Features

- **Automated Browser Control:** Uses Playwright to simulate a real user and interact with LinkedIn job search pages.
- **Login Support:** Supports logging into LinkedIn using credentials and/or cookies (loaded via environment variables).
- **Flexible Search:** Easily construct search URLs by job title and location.
- **Data Extraction:** Collects job details such as title, company, location, post date, salary, job type, and workplace type.
- **Batch Processing:** Saves collected jobs in batches to CSV files for easier large-scale analysis.
- **Scrolling & Pagination:** Automatically scrolls through job lists and paginates through multiple result pages.
- **Error Handling & Fallback:** Robust against errors, with fallback logic and retries for improved reliability.
- **Test Mode:** Optionally save results to a test location for development/debugging.

## Usage

### Prerequisites

- Python 3.8+
- [Playwright](https://playwright.dev/python/)
- [pandas](https://pandas.pydata.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [parsel](https://pypi.org/project/parsel/)

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

Create a `.env` file in your linkedin_scraper directory with the following:

```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_COOKIES=your_cookies_string   # Optional, can be blank
```

### Running the Scraper

The typical entry point is `main.py`:

```bash
python main.py
```

This will:

- Start a headless browser
- Login to LinkedIn (using credentials from `.env`)
- Search for jobs (default: "machine learning engineer" in "United States")
- Scrape up to 30 jobs (changeable via code)
- Save results to `data/jobs_data/linkedin_jobs.csv`

#### Customizing the Search

You can modify the job query and location in `main.py`:

```python
url = await scraper.get_url("software engineer","Canada")
await scraper.scrape(url,limit=100)
```

### Output

- Scraped jobs are saved as CSV in `data/jobs_data/`.
- Batch files are saved for large runs.
- Test runs save to `data/test_data/`.

## Project Structure

```
linkedin-job-scraper/
│
├── linkedin_scraper/
│   ├── .env                  # Your LinkedIn credentials (not included)
│   ├── linkedin_scraper.py   # Main scraping logic
│   ├── xpaths.py             # XPaths for LinkedIn page elements
│   └── linkedin_login.py     # Login handling (not shown)
├── utils/
│   └── logger.py             # Logging utility
├── data/
│   ├── jobs_data/            # Output CSVs
│   └── test_data/            # Test output
├── main.py                   # Example entry script
└── README.md
```

## Disclaimer

This tool is for educational and research purposes only. Scraping LinkedIn may violate their terms of service; use responsibly and at your own risk.

---

**Author:** [dav404-cmd](https://github.com/dav404-cmd)