try:
    from prefect import task
except ImportError:
    def task(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        def decorator(func):
            return func
        return decorator

from typing import List, Dict, Any

@task
def run_scrape() -> List[Dict[str, Any]]:
    """
    Simulates scraping data for routes.
    Returns raw data.
    """
    # In a real implementation, this would call prometheus.scrapers.*
    return [{"route": "DEL-BOM", "fare": 5000, "airline": "6E"}]

@task
def run_etl(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Simulates ETL (cleaning, deduplication, normalisation).
    """
    # In a real implementation, this would call prometheus.etl.*
    clean_data = []
    for item in raw_data:
        if item.get("fare") > 0:
            clean_data.append(item)
    return clean_data

@task
def run_index_computation(clean_data: List[Dict[str, Any]]) -> float:
    """
    Simulates Jevons index computation based on cleaned data.
    """
    # In a real implementation, this would call prometheus.index.jevons.*
    if not clean_data:
        return 100.0
    return 105.5  # Simulated index value

@task
def check_alerts(index_value: float) -> bool:
    """
    Simulates checking for alert thresholds.
    """
    # In a real implementation, this would trigger alerts via prometheus.alerts.*
    if index_value > 150.0:
        print(f"Alert generated for high index: {index_value}")
        return True
    return False
