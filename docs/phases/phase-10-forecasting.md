# Phase 10 — Forecasting: SARIMA & Prophet Time-Series Fare Index Baseline Forecaster

## Objective
Build a time-series forecasting engine that predicts the Airfare Price Index (APIx) 7–14 days ahead,
providing a "forecast baseline" against which real-time scraped values are compared for anomaly detection and user alerts.

## Alignment with problem statement & feasibility
Directly addresses SIH26056's requirement for predictive price intelligence. Gives judges a forward-looking  
dashboard metric beyond the raw index value.

> **MVP Status**: **EXCLUDED from MVP (Phase 1)**. This is a Phase 2 extension point.  
> The `PROMETHEUS_FORECAST_HORIZON_DAYS` and `PROMETHEUS_ML_CONTAMINATION` env vars are already wired  
> in `prometheus/config.py` so existing ML code does not break at import time.

## Prerequisites
- Phase 06 (Index Engine) completed — `airfare_index` table populated with ≥ 30 daily snapshots.
- Phase 09 (ML Anomaly) completed — Isolation Forest scores available.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| statsmodels | ≥0.14.0 | SARIMA model fitting |
| prophet | ≥1.1.5 | Facebook Prophet seasonal decomposition |
| pandas | ≥2.0.0 | Time-series DataFrame operations |
| numpy | ≥1.26.0 | Numerical operations |
| scikit-learn | ≥1.4.0 | Train/test split, metrics |

## Repo layout after this phase
```
prometheus/
└── ml/
    ├── __init__.py
    ├── forecasting.py      ← SARIMA + Prophet ensemble
    ├── feature_store.py    ← Pulls historical APIx from DB
    └── evaluation.py       ← MAPE, RMSE evaluation metrics
```

## Implementation Steps

### Step 1: Feature Store — Pull APIx History from DB
```python
# prometheus/ml/feature_store.py
import pandas as pd
from sqlalchemy import text
from prometheus.database.session import get_db_session

async def load_apix_series(origin: str = "DEL", destination: str = "BOM") -> pd.Series:
    async with get_db_session() as session:
        result = await session.execute(
            text("""
                SELECT DATE(calculated_at) AS dt, AVG(airfare_index) AS apix
                FROM airfare_index
                WHERE origin = :origin AND destination = :destination
                GROUP BY DATE(calculated_at)
                ORDER BY dt ASC
            """),
            {"origin": origin, "destination": destination},
        )
        rows = result.mappings().all()
    df = pd.DataFrame(rows)
    df["dt"] = pd.to_datetime(df["dt"])
    return df.set_index("dt")["apix"]
```

### Step 2: SARIMA Forecasting Model
```python
# prometheus/ml/forecasting.py
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
from prometheus.config import settings

def forecast_sarima(series: pd.Series, horizon: int | None = None) -> pd.Series:
    """Fit SARIMA(1,1,1)(1,1,1)[7] and return horizon-day forecast."""
    h = horizon or settings.FORECAST_HORIZON_DAYS
    model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7),
                    enforce_stationarity=False, enforce_invertibility=False)
    fit = model.fit(disp=False)
    forecast = fit.get_forecast(steps=h)
    return forecast.predicted_mean
```

### Step 3: Prophet Model (ensemble partner)
```python
from prophet import Prophet
import pandas as pd

def forecast_prophet(series: pd.Series, horizon: int = 14) -> pd.Series:
    df = series.reset_index().rename(columns={"dt": "ds", "apix": "y"})
    m = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
    m.fit(df)
    future = m.make_future_dataframe(periods=horizon)
    forecast = m.predict(future)
    return forecast[["ds", "yhat"]].tail(horizon).set_index("ds")["yhat"]
```

### Step 4: Expose via API endpoint
```
GET /api/forecast?origin=DEL&destination=BOM&horizon=14
```

## Deliverables
- `prometheus/ml/forecasting.py`
- `prometheus/ml/feature_store.py`
- `prometheus/ml/evaluation.py`
- `prometheus/api/routers/forecast.py` — `GET /api/forecast`
- `tests/unit/test_forecasting.py`

## Definition of Done
```bash
pytest tests/unit/test_forecasting.py -v
# GET /api/forecast?origin=DEL&destination=BOM returns a 14-day forecast array
```

## Out of Scope
- Deep learning (LSTM) models.
- Multi-route ensemble weighting.
- Real-time retraining pipelines.

## Notes
- Requires at least 30 days of `airfare_index` observations for stable SARIMA fitting.
- If less data is available, fall back to naive last-value + linear trend.
- Prophet handles missing dates gracefully; SARIMA requires imputation.
