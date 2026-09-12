"""
PROMETHEUS Scrapers package.

Provides Scrapy + Playwright flight scraping framework with spiders for:
- EaseMyTrip (OTA)
- Cleartrip (OTA)
- ixigo (OTA)
- Google Flights (Airline aggregator)

Core route matrix: 6 DGCA routes × 4 advance-purchase lead times (T+1, T+7, T+15, T+30).
"""

from prometheus.scrapers.base import DEFAULT_ROUTES, DEFAULT_WINDOWS, CITY_MAP
from prometheus.scrapers.items import FlightItem
from prometheus.scrapers.pipelines import FlightCleanerPipeline

__all__ = [
    "DEFAULT_ROUTES",
    "DEFAULT_WINDOWS",
    "CITY_MAP",
    "FlightItem",
    "FlightCleanerPipeline",
]
