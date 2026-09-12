
import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyDetector:

    def __init__(
        self,
        contamination=0.05,
        random_state=42
    ):
        self.model = IsolationForest(
            n_estimators=300,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, X):
        """Train the model on historical data."""
        self.model.fit(X)

    def predict(self, X):
        """Predict anomalies on new/unseen data."""

        predictions = self.model.predict(X)

        raw_scores = -self.model.score_samples(X)

        return predictions, raw_scores

