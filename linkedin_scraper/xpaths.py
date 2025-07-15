#xpaths for login:

EMAIL_FIELD = "input[name='session_key']"
PASSWORD_FIELD = "input[name='session_password']"
SUBMIT_BTN = "button[type='submit']"

#xpaths for job scraping :

JOB_CARD = "//a[contains(@href, '/jobs/view/')]/ancestor::div[contains(@class, 'job-card-container')]"
# This assumes the right-side job detail panel is already loaded after clicking the card
TITLE = "//div[contains(@class, 'job-details-jobs-unified-top-card__job-title')]//h1//text()"
COMPANY = "//div[contains(@class, 'job-details-jobs-unified-top-card__company-name')]//a/text()"
NEXT_BTN = "//button[@aria-label='View next page' and not(@disabled)]"
LOCATION = "//span[contains(@class, 'tvm__text') and contains(@class, 'low-emphasis') and contains(text(), ',')]/text()"
POST_DATE = (
    "//span[contains(@class, 'tvm__text') and "
    "(contains(@class, 'tvm__text--positive') or contains(@class, 'tvm__text--low-emphasis'))]"
    "[.//span[contains(text(), 'ago') or contains(text(), 'week') or contains(text(), 'month')]]"
    "//span/text()"
)
#the job_point are just preference btw .Eg : salary,job type(remote),skills,etc.
JOB_POINTS = "(//div[contains(@class,'job-details-fit-level-preferences')]//strong)/text()"

#NOTE: SCROLL_CONTAINER changes regularly .
SCROLL_CONTAINER = "div.HNvtVchiEpyZXjvHcrhpPhuiGsgEuhbAiKgHQ"