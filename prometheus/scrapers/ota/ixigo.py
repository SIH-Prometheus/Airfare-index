import re
import logging
from datetime import datetime, timezone
import scrapy
from prometheus.scrapers.items import FlightItem

logger = logging.getLogger(__name__)


class IxigoSpider(scrapy.Spider):
    """Spider to scrape flight quotes from ixigo (OTA) using Playwright."""

    name = "ixigo"
    allowed_domains = ["ixigo.com"]

    def __init__(
        self,
        origin="DEL",
        destination="BOM",
        date=None,
        lead_time="",
        headless="true",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.origin = str(origin).strip().upper()
        self.destination = str(destination).strip().upper()
        self.lead_time = str(lead_time).strip()

        if not date:
            raise ValueError("Parameter 'date' (YYYY-MM-DD or DD/MM/YYYY) is required.")

        raw_date = str(date).strip()
        # ixigo takes DDMMYYYY in URL (e.g. 19092026)
        if "/" in raw_date:
            parts = raw_date.split("/")
            if len(parts) == 3:
                d, m, y = parts[0], parts[1], parts[2]
                self.date_compact = f"{int(d):02d}{int(m):02d}{y}"
                self.date_display = f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                self.date_compact = raw_date
                self.date_display = raw_date
        elif "-" in raw_date:
            parts = raw_date.split("-")
            if len(parts) == 3:
                y, m, d = parts[0], parts[1], parts[2]
                self.date_compact = f"{int(d):02d}{int(m):02d}{y}"
                self.date_display = f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                self.date_compact = raw_date
                self.date_display = raw_date
        elif len(raw_date) == 8 and raw_date.isdigit():
            # YYYYMMDD
            y, m, d = raw_date[:4], raw_date[4:6], raw_date[6:8]
            self.date_compact = f"{d}{m}{y}"
            self.date_display = f"{y}-{m}-{d}"
        else:
            self.date_compact = raw_date
            self.date_display = raw_date

        self.headless = str(headless).lower() in ("true", "1", "yes")

        # ixigo one-way search URL format
        self.start_url = (
            f"https://www.ixigo.com/search/result/flight?"
            f"from={self.origin}&to={self.destination}&date={self.date_compact}"
            f"&adults=1&children=0&infants=0&class=e"
        )
        self.start_urls = [self.start_url]

    async def start(self):
        for req in self.start_requests():
            yield req

    def start_requests(self):
        logger.info(
            f"Searching ixigo: {self.origin} -> {self.destination} on {self.date_display} (Lead time: {self.lead_time})"
        )
        yield scrapy.Request(
            url=self.start_url,
            callback=self.parse,
            dont_filter=True,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_context_kwargs": {
                    "user_agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "viewport": {"width": 1280, "height": 900},
                },
            },
        )

    async def parse(self, response):
        page = response.meta.get("playwright_page")
        if not page:
            logger.warning("No Playwright page found in response meta.")
            return

        try:
            logger.info("ixigo page loaded. Waiting for flight results...")

            # Wait for search results container
            try:
                await page.wait_for_selector("div[class*='Listing_listItem'], div[class*='shadow-card']", timeout=25000)
                logger.info("ixigo flight cards detected.")
            except Exception:
                logger.warning("Timeout waiting for ixigo flight card elements.")

            await page.wait_for_timeout(4000)

            # Scroll to trigger lazy loading
            for _ in range(4):
                await page.evaluate("window.scrollBy(0, 1000)")
                await page.wait_for_timeout(400)

            rendered_html = await page.content()
            logger.info(f"Rendered HTML length: {len(rendered_html)} chars")

            selector = scrapy.Selector(text=rendered_html)
            flight_count = 0
            for item in self.parse_flight_cards(selector):
                flight_count += 1
                yield item

            logger.info(f"Extracted {flight_count} flights from ixigo.")

        except Exception as exc:
            logger.error(f"ixigo parse error: {exc}", exc_info=True)
        finally:
            await page.close()

    def parse_flight_cards(self, selector):
        """Extract FlightItems from rendered ixigo HTML selector."""
        now_str = datetime.now(timezone.utc).isoformat()
        cards = selector.css("div[class*='Listing_listItem'], div[class*='shadow-card']")

        for card in cards:
            txt = " ".join([t.strip() for t in card.xpath(".//text()").getall() if t.strip()])
            if not txt:
                continue

            # 1. Price
            p_match = re.search(r"₹\s*([\d,]+)", txt)
            if not p_match:
                continue
            price_raw = p_match.group(1)

            # 2. Airline
            airline = ""
            for al in ["Air India Express", "Air India", "IndiGo", "Akasa Air", "AkasaAir", "SpiceJet", "Vistara"]:
                if al in txt:
                    airline = "Akasa Air" if "Akasa" in al else al
                    break
            if not airline:
                continue

            # 3. Flight Number
            fn_match = re.search(r"\b([A-Z0-9]{2}\s*[-]?\s*\d{3,4})\b", txt)
            flight_number = fn_match.group(1).replace(" ", "-") if fn_match else "Unknown"

            # 4. Departure & Arrival Times (HH:MM)
            times = re.findall(r"\b(\d{1,2}:\d{2})\b", txt)
            dep_time = times[0] if len(times) > 0 else ""
            arr_time = times[1] if len(times) > 1 else ""

            # 5. Duration
            dur_match = re.search(r"\b(\d{1,2}h\s*\d{1,2}m)\b", txt)
            duration = dur_match.group(1) if dur_match else ""

            # 6. Stops
            stops = "Non-stop" if "Non-stop" in txt else "1 stop" if "1 stop" in txt else "Multi-stop"

            yield FlightItem(
                airline=airline,
                flight_number=flight_number,
                departure_time=dep_time,
                arrival_time=arr_time,
                origin=self.origin,
                destination=self.destination,
                duration=duration,
                stops=stops,
                price=price_raw,
                currency="INR",
                source_platform="ixigo",
                lead_time=self.lead_time,
                scraped_at=now_str,
            )
