import logging

logger = logging.getLogger(__name__)


class FlightScraperSpiderMiddleware:
    pass


class FlightScraperDownloaderMiddleware:
    def process_request(self, request, spider):
        # Ensure standard browser headers if not present
        if "User-Agent" not in request.headers:
            request.headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            )
        return None
