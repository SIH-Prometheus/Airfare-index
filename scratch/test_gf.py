import httpx
import re
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def test_scrape():
    url = "https://www.google.com/travel/flights?q=flights+from+DEL+to+BOM+on+2026-09-15&curr=INR"
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=20.0) as client:
        resp = client.get(url)
        html = resp.text

    print(f"HTTP Status: {resp.status_code}")
    print(f"HTML Size: {len(html)} bytes")

    # Find aria-labels that describe full flights
    aria_labels = re.findall(r'aria-label="([^"]+)"', html)
    flight_labels = [
        a for a in aria_labels
        if any(air in a for air in ["IndiGo", "Air India", "Akasa Air", "SpiceJet", "Vistara"])
        and any(cur in a for cur in ["rupees", "INR", "\u20b9"])
    ]

    print(f"Total flight cards detected: {len(flight_labels)}\n")

    flights = []
    for a in flight_labels:
        # 1. Airline
        airline = "Unknown"
        for air in ["IndiGo", "Air India", "Akasa Air", "SpiceJet", "Vistara"]:
            if air in a:
                airline = air
                break

        # 2. Times
        times = [t.replace("\u202f", " ") for t in re.findall(r"\b(\d{1,2}:\d{2}(?:\s*(?:AM|PM))?)\b", a)]
        dep_time = times[0] if len(times) >= 1 else ""
        arr_time = times[1] if len(times) >= 2 else ""

        # 3. Duration
        dur_m = re.search(r"duration\s+([\d\s\w]+?)\.", a)
        duration = dur_m.group(1).strip() if dur_m else ""

        # 4. Stops
        stops = "Nonstop" if "Nonstop" in a or "nonstop" in a else "1 stop"

        # 5. Price
        p_m = re.search(r"(?:From\s+)?([\d,]+)\s+Indian rupees", a) or re.search(r"[\u20b9]\s*([\d,]+)", a)
        price = int(p_m.group(1).replace(",", "")) if p_m else 0

        if price > 0:
            flights.append({
                "airline": airline,
                "origin": "DEL",
                "destination": "BOM",
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "duration": duration,
                "stops": stops,
                "price": price,
                "currency": "INR",
                "source_platform": "Google Flights (live OTA)"
            })

    print(f"Successfully extracted {len(flights)} real flight records:\n")
    for idx, f in enumerate(flights[:10], 1):
        print(f"[{idx:02d}] {f['airline']:<10} | {f['origin']}->{f['destination']} | Dep: {f['departure_time']:<8} Arr: {f['arrival_time']:<8} | {f['duration']:<14} | {f['stops']:<8} | INR {f['price']}")

if __name__ == "__main__":
    test_scrape()
