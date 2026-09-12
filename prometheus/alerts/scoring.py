def calculate_alert_score(wow_signal: float, z_score_signal: float, ml_anomaly: float, forecast_deviation: float) -> float:
    """
    Combines different signals into a single alert score (0 to 1).
    Weights: WoW (0.30), Z-score (0.20), ML Anomaly (0.35), Forecast (0.15)
    """
    # Normalize wow_signal: cap at 15% change
    norm_wow = min(max(abs(wow_signal) / 15.0, 0.0), 1.0)
    
    # Normalize z_score_signal: cap at 3 std dev
    norm_z = min(max(abs(z_score_signal) / 3.0, 0.0), 1.0)
    
    # ML and forecast are assumed to be 0 to 1
    norm_ml = min(max(ml_anomaly, 0.0), 1.0)
    norm_fc = min(max(abs(forecast_deviation) / 10.0, 0.0), 1.0) # Assuming 10% is max deviation
    
    score = (0.30 * norm_wow) + (0.20 * norm_z) + (0.35 * norm_ml) + (0.15 * norm_fc)
    return round(score, 2)

def get_alert_level(score: float) -> str:
    """
    0.00–0.40 → NORMAL
    0.40–0.65 → WATCH
    0.65–0.80 → ELEVATED
    0.80–1.00 → HIGH
    """
    if score >= 0.80:
        return "HIGH"
    elif score >= 0.65:
        return "ELEVATED"
    elif score >= 0.40:
        return "WATCH"
    else:
        return "NORMAL"
