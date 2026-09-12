"""
prometheus/scrapers/__init__.py
Safe package init — does NOT import Scrapy at the top level.
Scrapy is only available when running the full scraper stack (not inside Docker MVP).
"""
