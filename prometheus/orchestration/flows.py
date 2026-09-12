try:
    from prefect import flow
except ImportError:
    def flow(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        def decorator(func):
            return func
        return decorator

from prometheus.orchestration.tasks import run_scrape, run_etl, run_index_computation, check_alerts
from typing import Dict, Any

@flow(name="daily_pipeline_flow", log_prints=True)
def daily_pipeline_flow() -> Dict[str, Any]:
    """
    Main orchestration flow for Prometheus APix.
    Executes collection, cleaning, indexing, and alerting.
    """
    print("Starting Daily Pipeline Flow...")
    
    # 1. Scrape data
    raw_data = run_scrape()
    print(f"Scraped {len(raw_data)} records.")
    
    # 2. ETL Processing
    clean_data = run_etl(raw_data)
    print(f"ETL completed. {len(clean_data)} valid records remain.")
    
    # 3. Index Computation
    index_value = run_index_computation(clean_data)
    print(f"Computed Airfare Index: {index_value}")
    
    # 4. Check Alerts
    alert_triggered = check_alerts(index_value)
    
    print("Pipeline Flow Completed successfully.")
    
    return {
        "records_scraped": len(raw_data),
        "records_processed": len(clean_data),
        "computed_index": index_value,
        "alert_triggered": alert_triggered
    }

if __name__ == "__main__":
    daily_pipeline_flow()
