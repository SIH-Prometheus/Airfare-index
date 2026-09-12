from prometheus.orchestration.flows import daily_pipeline_flow

def test_daily_pipeline_flow():
    """
    Test the basic execution of the daily pipeline Prefect flow.
    """
    # Execute the flow
    result = daily_pipeline_flow()
    
    # Assertions
    assert "records_scraped" in result
    assert "records_processed" in result
    assert "computed_index" in result
    assert "alert_triggered" in result
    
    assert result["records_scraped"] == 1
    assert result["records_processed"] == 1
    assert result["computed_index"] == 105.5
    assert result["alert_triggered"] is False
