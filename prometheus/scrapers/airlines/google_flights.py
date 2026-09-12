import re
import logging
from datetime import datetime, timezone
import scrapy
from prometheus.scrapers.items import FlightItem

logger = logging.getLogger(__name__)


class GoogleFlightsSpider(scrapy.Spider):
    """Spider to scrape flight prices and details from Google Flights using Playwright."""

    name = "google_flights"
    allowed_domains = ["google.com"]

    def __init__(self, origin="DEL", destination="BOM", date=None, lead_time="", headless="true", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = str(origin).strip().upper()
        self.destination = str(destination).strip().upper()
        self.lead_time = str(lead_time).strip()

        if not date:
            raise ValueError("Parameter 'date' (YYYY-MM-DD) is required.")
        date_clean = str(date).strip()
        # Accept YYYY-MM-DD or YYYYMMDD
        if len(date_clean) == 8 and date_clean.isdigit():
            date_clean = f"{date_clean[:4]}-{date_clean[4:6]}-{date_clean[6:8]}"
        self.date_str = date_clean  # YYYY-MM-DD

        self.headless = str(headless).lower() in ("true", "1", "yes")

        # Google Flights search query URL
        self.start_url = (
            f"https://www.google.com/travel/flights?q=flights+from+{self.origin}+to+{self.destination}+on+{self.date_str}&curr=INR"
        )
        self.start_urls = [self.start_url]

    async def start(self):
        for req in self.start_requests():
            yield req

    def start_requests(self):
        logger.info(f"Searching Google Flights: {self.origin} -> {self.destination} on {self.date_str}")
        yield scrapy.Request(
            url=self.start_url,
            callback=self.parse,
            dont_filter=True,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_context_kwargs": {
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
            logger.info("Page loaded. Waiting for flight results to render...")

            # Dismiss consent/cookie dialog if present
            try:
                consent_btn = page.locator('button:has-text("Accept all"), button:has-text("Reject all"), button:has-text("I agree")')
                if await consent_btn.count() > 0:
                    await consent_btn.first.click()
                    await page.wait_for_timeout(1500)
            except Exception:
                pass

            # Wait for flight result list items to appear
            try:
                await page.wait_for_selector('li.pIav2d, ul.Rk10dc li, div[role="link"][aria-label*="flight"]', timeout=20000)
                logger.info("Flight results container detected.")
            except Exception:
                logger.warning("Timeout waiting for flight cards. Proceeding with available DOM...")

            # Wait for dynamic fares to settle
            await page.wait_for_timeout(3000)

            # Scroll down to load more results
            for _ in range(4):
                await page.evaluate("window.scrollBy(0, 1000)")
                await page.wait_for_timeout(600)

            # Click "Show more flights" button if present
            try:
                more_btn = page.locator('button:has-text("more flights"), button:has-text("Show more")')
                if await more_btn.count() > 0:
                    await more_btn.first.click()
                    await page.wait_for_timeout(2500)
                    logger.info("Expanded more flights.")
            except Exception:
                pass

            # Final scroll to ensure all DOM items are attached
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(500)

            rendered_html = await page.content()
            logger.info(f"Rendered HTML length: {len(rendered_html)} chars")

            selector = scrapy.Selector(text=rendered_html)

            flight_count = 0
            for item in self.parse_flight_cards(selector):
                flight_count += 1
                yield item

            logger.info(f"Extracted {flight_count} flights from Google Flights.")

        except Exception as exc:
            logger.error(f"Spider parse error: {exc}", exc_info=True)
        finally:
            await page.close()

    def parse_flight_cards(self, selector):
        """Extract FlightItems from Google Flights rendered HTML selector."""
        now_str = datetime.now(timezone.utc).isoformat()

        cards = selector.css("li.pIav2d") or selector.css("ul.Rk10dc > li")

        for card in cards:
            # 1. Main link / aria-label containing rich summary
            aria = (
                card.css('div[role="link"][aria-label]::attr(aria-label)').get()
                or card.attrib.get("aria-label", "")
                or ""
            )

            # 2. Departure time: look for explicit departure label or role=text span
            dep_time = (
                card.css('span[aria-label^="Departure time"] span[role="text"]::text').get()
                or card.css('div[aria-label^="Departure time"]::text').get()
                or ""
            )
            # 3. Arrival time: look for explicit arrival label or role=text span
            arr_time = (
                card.css('span[aria-label^="Arrival time"] span[role="text"]::text').get()
                or card.css('div[aria-label^="Arrival time"]::text').get()
                or ""
            )

            # Fallback for times: search text of time elements
            if not dep_time or not arr_time:
                time_matches = re.findall(r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b", card.get())
                if len(time_matches) >= 2:
                    if not dep_time:
                        dep_time = time_matches[0]
                    if not arr_time:
                        arr_time = time_matches[1]

            # Clean up narrow non-breaking spaces (\u202f) and whitespace
            dep_time = dep_time.replace("\u202f", " ").replace("&nbsp;", " ").strip()
            arr_time = arr_time.replace("\u202f", " ").replace("&nbsp;", " ").strip()

            # 4. Airline name:
            airline = ""
            airline_match = re.search(r"flight with ([^.]+)\.", aria)
            if airline_match:
                airline = airline_match.group(1).strip()

            if not airline:
                # Try specific span classes Google Flights uses
                s_els = card.css("div.sSHqwe span::text, span.h1fkLb span::text, span[data-test-id='airline-name']::text").getall()
                for s in s_els:
                    clean_s = s.strip()
                    if clean_s and not any(x in clean_s for x in ["DEL", "BOM", "hr", "min", "stop", "AM", "PM", "+"]):
                        airline = clean_s
                        break

            # 5. Duration:
            duration = (
                card.css("div.gvkrdb::text").get()
                or card.css("div[aria-label^='Total duration']::text").get()
                or card.css("div.Ak5kof div::text").get()
                or ""
            ).strip()
            if not duration:
                dur_match = re.search(r"Total duration\s+([^.]+)\.", aria)
                if dur_match:
                    duration = dur_match.group(1).strip()

            # 6. Stops:
            stops = (
                card.css("span.ogfYpf[aria-label*='stop']::text").get()
                or card.css("span.ogfYpf[aria-label*='Nonstop']::text").get()
                or ""
            ).strip()
            if not stops:
                if "Nonstop" in aria or "nonstop" in aria.lower():
                    stops = "Nonstop"
                else:
                    stop_m = re.search(r"(\d+\s*stop[s]?)", aria, re.IGNORECASE)
                    stops = stop_m.group(1) if stop_m else "Non-stop"

            # 7. Price:
            price = (
                card.css("span[aria-label*='Indian rupees'] span[role='text']::text").get()
                or card.css("span[aria-label*='rupees']::text").get()
                or card.css("div.YMlIz span::text").get()
                or ""
            ).strip()
            if not price:
                p_match = re.search(r"From\s+([\d,]+)\s+Indian rupees", aria)
                if p_match:
                    price = p_match.group(1)

            if not price:
                price_match = re.search(r"[₹￥$][\s,\d]+|(?:INR|Rs\.?)\s*[\s,\d]+", card.get())
                if price_match:
                    price = price_match.group(0).strip()

            # Clean price string
            price = price.replace("\u202f", " ").replace("&nbsp;", " ").strip()

            # 8. Flight number (if available)
            flight_number = ""
            flt_match = re.search(r"\b(6E|AI|SG|QP|UK|G8|I5|IX|AA|BA|EK|QR|SQ|LH)\s*[-]?\s*(\d{2,4})\b", card.get())
            if flt_match:
                flight_number = f"{flt_match.group(1)} {flt_match.group(2)}"

            # Require at least airline or price to consider a valid flight item
            if not airline and not price:
                continue

            yield FlightItem(
                airline=airline or "Unknown Airline",
                flight_number=flight_number,
                departure_time=dep_time,
                arrival_time=arr_time,
                origin=self.origin,
                destination=self.destination,
                duration=duration,
                stops=stops,
                price=price,
                currency="INR",
                source_platform="Google Flights",
                lead_time=self.lead_time,
                scraped_at=now_str,
            )
