import re
from datetime import datetime, timezone
from scrapy.exceptions import DropItem


class FlightCleanerPipeline:
    def __init__(self):
        self.seen_flights = set()

    def process_item(self, item, spider=None):
        # Validate airline
        airline = item.get("airline")
        if not airline or not str(airline).strip():
            raise DropItem("Missing airline in flight item")
        item["airline"] = str(airline).strip()

        # Validate and clean price
        raw_price = item.get("price")
        if raw_price is None or raw_price == "":
            raise DropItem("Missing price in flight item")

        if isinstance(raw_price, str):
            clean_digits = re.sub(r"[^\d]", "", raw_price)
            if not clean_digits:
                raise DropItem(f"Invalid price string: {raw_price}")
            item["price"] = int(clean_digits)
        elif isinstance(raw_price, (int, float)):
            item["price"] = int(raw_price)
        else:
            raise DropItem(f"Unsupported price type: {type(raw_price)}")

        # Default currency
        if not item.get("currency"):
            item["currency"] = "INR"

        # Format and clean duration
        if item.get("duration"):
            raw_dur = " ".join(str(item["duration"]).split())
            # Normalize e.g. "2 h 15 m" or "2h 15 m" to "2h 15min"
            item["duration"] = re.sub(r"(\d+)\s*([a-zA-Z]+)", r"\1\2", raw_dur)

        # Format and clean stops
        if item.get("stops"):
            item["stops"] = " ".join(str(item["stops"]).split())

        # Format timings
        if item.get("departure_time"):
            item["departure_time"] = str(item["departure_time"]).strip()
        if item.get("arrival_time"):
            item["arrival_time"] = str(item["arrival_time"]).strip()

        # Format flight number
        if item.get("flight_number"):
            item["flight_number"] = " ".join(str(item["flight_number"]).split())

        # Deduplication check on cleaned data
        flight_key = (
            item.get("source_platform"),
            item.get("origin"),
            item.get("destination"),
            item.get("lead_time"),
            item.get("airline"),
            item.get("flight_number"),
            item.get("departure_time"),
            item.get("arrival_time"),
            item.get("price"),
        )
        if flight_key in self.seen_flights:
            raise DropItem(f"Duplicate flight item: {flight_key}")
        self.seen_flights.add(flight_key)

        # Add scraped timestamp if not present
        if not item.get("scraped_at"):
            item["scraped_at"] = datetime.now(timezone.utc).isoformat()

        return item
