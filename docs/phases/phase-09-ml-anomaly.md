# Phase 09 — ML Anomaly: Isolation Forest Unsupervised Anomaly Detection

## Objective
Deploy machine learning anomaly detection to isolate irregular flight pricing patterns across lead times and routes.

## Alignment with problem statement & feasibility
Enhances analytical depth by differentiating true inflation from isolated carrier pricing anomalies.

## Prerequisites
Phase 08 completed.

## Tech choices (this phase)
| Tool | Version | Purpose |
|---|---|---|
| Scikit-Learn | 1.5.0 | Isolation Forest algorithm |

## Repo layout after this phase
```
prometheus/ml/
├── __init__.py
├── features.py
└── anomaly.py
```

## Implementation Steps
### Step 1: Anomaly Detector in `prometheus/ml/anomaly.py`
```python
from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(contamination=contamination, random_state=42)

    def train_and_predict(self, feature_matrix: np.ndarray) -> np.ndarray:
        return self.model.fit_predict(feature_matrix)
```

## Deliverables
- `prometheus/ml/features.py`
- `prometheus/ml/anomaly.py`
- `tests/unit/test_ml_anomaly.py`

## Definition of Done
```bash
pytest tests/unit/test_ml_anomaly.py
```

## Out of Scope
Deep learning autoencoders.

## Notes
Retrain model weekly.
