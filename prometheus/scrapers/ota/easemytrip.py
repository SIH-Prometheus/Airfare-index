import re
import logging
from datetime import datetime, timezone
import scrapy
from prometheus.scrapers.items import FlightItem
from prometheus.scrapers.base import CITY_MAP

logger = logging.getLogger(__name__)


class EaseMyTripSpider(scrapy.Spider):
    """Spider to scrape flight quotes and details from EaseMyTrip (OTA) using Playwright."""

    name = "easemytrip"
    allowed_domains = ["easemytrip.com"]

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
        # Parse date and standardize to DD/MM/YYYY for EaseMyTrip and YYYY-MM-DD for tracking
        if "/" in raw_date:
            parts = raw_date.split("/")
            if len(parts) == 3:
                # If given DD/MM/YYYY
                d, m, y = parts[0], parts[1], parts[2]
                self.date_emt = f"{int(d):02d}/{int(m):02d}/{y}"
                self.date_iso = f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                self.date_emt = raw_date
                self.date_iso = raw_date
        elif "-" in raw_date:
            parts = raw_date.split("-")
            if len(parts) == 3:
                # If given YYYY-MM-DD
                y, m, d = parts[0], parts[1], parts[2]
                self.date_emt = f"{int(d):02d}/{int(m):02d}/{y}"
                self.date_iso = f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                self.date_emt = raw_date
                self.date_iso = raw_date
        elif len(raw_date) == 8 and raw_date.isdigit():
            # YYYYMMDD
            y, m, d = raw_date[:4], raw_date[4:6], raw_date[6:8]
            self.date_emt = f"{d}/{m}/{y}"
            self.date_iso = f"{y}-{m}-{d}"
        else:
            self.date_emt = raw_date
            self.date_iso = raw_date

        self.headless = str(headless).lower() in ("true", "1", "yes")

        origin_city = CITY_MAP.get(self.origin, self.origin)
        dest_city = CITY_MAP.get(self.destination, self.destination)

        # EaseMyTrip one-way search URL format
        self.start_url = (
            f"https://flight.easemytrip.com/FlightList/Index?"
            f"srch={self.origin}-{origin_city}-India|{self.destination}-{dest_city}-India|{self.date_emt}"
            f"&px=1-0-0&cbn=0&ar=undefined&isSplit=false"
        )
        self.start_urls = [self.start_url]

    async def start(self):
        for req in self.start_requests():
            yield req

    def start_requests(self):
        logger.info(
            f"Searching EaseMyTrip: {self.origin} -> {self.destination} on {self.date_emt} (Lead time: {self.lead_time})"
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
            logger.info("EaseMyTrip page loaded. Waiting for flight results...")

            # Wait for flight card container
            try:
                await page.wait_for_selector("div.fltResult", timeout=25000)
                logger.info("EaseMyTrip flight results detected.")
            except Exception:
                logger.warning("Timeout waiting for div.fltResult on EaseMyTrip.")

            # Allow dynamic angular/vue bindings to settle
            await page.wait_for_timeout(3000)

            # Scroll down to ensure all lazy loaded cards are in DOM
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 1000)")
                await page.wait_for_timeout(400)

            rendered_html = await page.content()
            logger.info(f"Rendered HTML length: {len(rendered_html)} chars")

            selector = scrapy.Selector(text=rendered_html)
            flight_count = 0
            for item in self.parse_flight_cards(selector):
                flight_count += 1
                yield item

            logger.info(f"Extracted {flight_count} flights from EaseMyTrip.")

        except Exception as exc:
            logger.error(f"EaseMyTrip parse error: {exc}", exc_info=True)
        finally:
            await page.close()

    def parse_flight_cards(self, selector):
        """Extract FlightItems from rendered EaseMyTrip HTML selector."""
        now_str = datetime.now(timezone.utc).isoformat()
        cards = selector.css("div.fltResult")

        for card in cards:
            # 1. Airline Name
            airline = card.css(".txt-r4::text").get()
            if not airline or not airline.strip():
                continue
            airline = airline.strip()

            # 2. Flight Number
            flt_parts = card.css(".txt-r5 ::text").getall()
            flight_number = "".join([p.strip() for p in flt_parts if p.strip()])
            if not flight_number:
                flight_number = "Unknown"

            # 3. Departure & Arrival Times
            times = card.css("span.txt-r2-n::text, span.txt-r2::text").getall()
            dep_time = times[0].strip() if len(times) > 0 else ""
            arr_time = times[1].strip() if len(times) > 1 else ""

            # 4. Duration
            duration = (card.css("span.dura_md::text").get() or "").strip()

            # 5. Stops
            stops = (card.css("span.dura_md2::text").get() or "Non-stop").strip()

            # 6. Price
            price_raw = (
                card.css("span[id^='spnPrice']::text").get()
                or card.css("div.cross-pr-txt::text").get()
                or card.css("label[id^='lblTBAmount']::text").get()
                or card.css("div.prce_mn::text").get()
                or card.css("div.txt-r6-n::text").get()
                or ""
            ).strip()

            if not price_raw:
                # Fallback: search price pattern in card text
                p_match = re.search(r"[₹\s]*([\d,]{4,8})", card.get() or "")
                if p_match:
                    price_raw = p_match.group(1)

            if not price_raw:
                continue

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
                source_platform="EaseMyTrip",
                lead_time=self.lead_time,
                scraped_at=now_str,
            )
