"""PROMETHEUS OTA (Online Travel Aggregator) spiders package."""

from prometheus.scrapers.ota.easemytrip import EaseMyTripSpider
from prometheus.scrapers.ota.cleartrip import CleartripSpider
from prometheus.scrapers.ota.ixigo import IxigoSpider

__all__ = [
    "EaseMyTripSpider",
    "CleartripSpider",
    "IxigoSpider",
]
