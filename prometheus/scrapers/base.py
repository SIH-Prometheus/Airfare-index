"""
PROMETHEUS Scrapers — Shared constants and route configuration.

Defines the core DGCA routes, advance-purchase lead time windows,
and airport-to-city mappings used across all scraper spiders and runners.
"""

# ── Core 6 routes agreed upon for the APIx MVP prototype ─────────────────────
DEFAULT_ROUTES = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("BLR", "HYD"),
    ("MAA", "DEL"),
]

# ── 4 advance-purchase lead time windows ─────────────────────────────────────
DEFAULT_WINDOWS = [1, 7, 15, 30]

# ── Standard airport code to city name mapping (used by EaseMyTrip URLs) ─────
CITY_MAP = {
    "DEL": "Delhi",
    "BOM": "Mumbai",
    "BLR": "Bangalore",
    "CCU": "Kolkata",
    "HYD": "Hyderabad",
    "MAA": "Chennai",
    "GOI": "Goa",
    "GOX": "Goa",
    "PNQ": "Pune",
    "AMD": "Ahmedabad",
    "JAI": "Jaipur",
    "LKO": "Lucknow",
    "COK": "Kochi",
    "GAU": "Guwahati",
    "PAT": "Patna",
    "IXC": "Chandigarh",
    "BBI": "Bhubaneswar",
    "SXR": "Srinagar",
    "TRV": "Thiruvananthapuram",
    "VNS": "Varanasi",
}
