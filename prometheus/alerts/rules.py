import numpy as np
from typing import List

class AlertRuleEngine:
    @staticmethod
    def check_wow_change(current_index: float, previous_week_index: float) -> float:
        if previous_week_index == 0:
            return 0.0
        pct_change = ((current_index - previous_week_index) / previous_week_index) * 100.0
        return pct_change

    @staticmethod
    def calculate_z_score(current_value: float, historical_values: List[float]) -> float:
        if len(historical_values) < 2:
            return 0.0
        mean = np.mean(historical_values)
        std = np.std(historical_values)
        if std == 0:
            return 0.0
        return (current_value - mean) / std
