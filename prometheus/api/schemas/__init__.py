"""schemas/__init__.py"""
from .fare import FareObservation, FareListResponse, FareStats
from .index import IndexValue, IndexCurrentResponse, IndexHistoryResponse
from .route import Route, RouteDetail, RouteListResponse
from .alert import Alert, AlertCurrentResponse, AlertHistoryResponse
from .metadata import Airline, Airport

__all__ = [
    "FareObservation", "FareListResponse", "FareStats",
    "IndexValue", "IndexCurrentResponse", "IndexHistoryResponse",
    "Route", "RouteDetail", "RouteListResponse",
    "Alert", "AlertCurrentResponse", "AlertHistoryResponse",
    "Airline", "Airport",
]
