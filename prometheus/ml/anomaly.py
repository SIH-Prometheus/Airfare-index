"""
prometheus/ml/anomaly.py
Isolation Forest anomaly detector for airfare pricing.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

# Path to the pre-trained model (produced by ml/train.py)
_MODEL_PATH = Path(__file__).resolve().parent / "anomaly_model.pkl"


class AnomalyDetector:
    """Thin wrapper around scikit-learn IsolationForest."""

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(
            n_estimators=300,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )

    def fit(self, X: np.ndarray) -> None:
        """Train the model on historical data."""
        self.model.fit(X)

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Return (predictions, anomaly_scores).
        predictions: 1=normal, -1=anomaly
        anomaly_scores: higher = more anomalous (0–1 range approx)
        """
        predictions = self.model.predict(X)
        raw_scores = -self.model.score_samples(X)
        return predictions, raw_scores


# ── Service function ──────────────────────────────────────────────────────────

def _flights_to_feature_matrix(flights: list[dict[str, Any]]) -> np.ndarray:
    """Convert raw flight dicts to a minimal feature matrix for inference."""
    rows: list[list[float]] = []
    for f in flights:
        price = float(f.get("price", 0) or 0)
        rows.append([price])
    return np.array(rows, dtype=float)


def score_flights(flights: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Run anomaly detection on a list of flight dicts.

    Returns the same list enriched with:
      - anomaly_score  (float, higher = more anomalous)
      - is_anomaly     (bool)
      - alert_level    ("NORMAL" | "WATCH" | "HIGH")

    Tries to load the pre-trained model; falls back to fitting on the
    supplied data if the model file is missing.
    """
    if not flights:
        return []

    X = _flights_to_feature_matrix(flights)

    detector = AnomalyDetector(contamination=0.05)

    # Try loading pre-trained model
    try:
        import joblib
        if _MODEL_PATH.exists():
            detector = joblib.load(_MODEL_PATH)
            logger.info("Loaded pre-trained anomaly model from %s", _MODEL_PATH)
        else:
            logger.warning("Model not found at %s — fitting on current data", _MODEL_PATH)
            detector.fit(X)
    except Exception as exc:
        logger.warning("Model load failed (%s) — fitting on current data", exc)
        detector.fit(X)

    predictions, scores = detector.predict(X)

    result: list[dict[str, Any]] = []
    for i, f in enumerate(flights):
        score = float(scores[i])
        is_anomaly = bool(predictions[i] == -1)
        if score >= 0.65 or is_anomaly:
            level = "HIGH"
        elif score >= 0.45:
            level = "WATCH"
        else:
            level = "NORMAL"
        result.append({
            **f,
            "anomaly_score": round(score, 4),
            "is_anomaly": is_anomaly,
            "alert_level": level,
        })
    return result
