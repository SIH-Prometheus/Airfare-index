# Phase 10 — Forecasting: Time-Series Baseline Forecasting

## Objective
Build predictive models forecasting short-term airfare index trends for 7 to 14 days ahead.

## Alignment with problem statement & feasibility
Delivers forward-looking inflation intelligence to policy analysts.

## Prerequisites
Phase 09 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Statsmodels | 0.14.2 | SARIMA modeling |
| Prophet | 1.1.5 | Seasonal decomposition |

## Repo layout after this phase
```
prometheus/ml/forecasting.py
```

## Implementation Steps
### Step 1: Forecaster in `prometheus/ml/forecasting.py`
```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np

class IndexForecaster:
    @staticmethod
    def forecast_sarima(series: np.ndarray, steps: int = 7) -> np.ndarray:
        model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
        fit = model.fit(disp=False)
        return fit.forecast(steps=steps)
```

## Deliverables
- `prometheus/ml/forecasting.py`
- `tests/unit/test_forecasting.py`

## Definition of Done
```bash
pytest tests/unit/test_forecasting.py
```

## Out of Scope
LSTM / Transformer neural forecasting.

## Notes
Includes 80% confidence interval boundaries.
