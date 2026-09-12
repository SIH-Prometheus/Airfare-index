import scrapy


class FlightItem(scrapy.Item):
    airline = scrapy.Field()
    flight_number = scrapy.Field()
    departure_time = scrapy.Field()
    arrival_time = scrapy.Field()
    origin = scrapy.Field()
    destination = scrapy.Field()
    duration = scrapy.Field()
    stops = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    source_platform = scrapy.Field()
    lead_time = scrapy.Field()
    scraped_at = scrapy.Field()
