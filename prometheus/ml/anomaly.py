from sklearn.ensemble import IsolationForest
import numpy as np


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42
        )

    def train_and_predict(self, feature_matrix: np.ndarray) -> np.ndarray:
        return self.model.fit_predict(feature_matrix)