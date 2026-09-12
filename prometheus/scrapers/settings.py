import sys
import asyncio

# On Windows, Twisted asyncio reactor requires WindowsSelectorEventLoopPolicy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BOT_NAME = "prometheus_scrapers"

SPIDER_MODULES = ["prometheus.scrapers.ota", "prometheus.scrapers.airlines"]
NEWSPIDER_MODULE = "prometheus.scrapers.ota"

# Travel platforms disallow crawlers in robots.txt for search paths
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 4
DOWNLOAD_TIMEOUT = 60

# Twisted Asyncio Reactor is mandatory for scrapy-playwright
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright download handlers
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = "chromium"

# Use the system Chrome install ('channel': 'chrome') for better stealth.
# Falls back to bundled Chromium if Chrome is not installed.
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,
    "channel": "chrome",
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-infobars",
    ],
}


ITEM_PIPELINES = {
    "prometheus.scrapers.pipelines.FlightCleanerPipeline": 300,
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
