from prometheus.alerts.rules import AlertRuleEngine
from prometheus.alerts.scoring import calculate_alert_score, get_alert_level
from datetime import datetime

class AlertEngine:
    @staticmethod
    def generate_alert(
        current_apix: float, 
        historical_apix: list[float], 
        route_contributions: dict[str, float],
        lead_time_pressure: dict[str, float],
        ml_anomaly_score: float = 0.5,
        forecast_deviation: float = 0.0
    ) -> dict:
        
        # historical_apix should be ordered oldest to newest, so -1 is latest, -7 is week ago.
        # Ensure we have enough data, fallback to first if not.
        if len(historical_apix) >= 8:
            previous_week = historical_apix[-8]
        elif len(historical_apix) > 0:
            previous_week = historical_apix[0]
        else:
            previous_week = current_apix
            
        wow_change = AlertRuleEngine.check_wow_change(current_apix, previous_week)
        z_score = AlertRuleEngine.calculate_z_score(current_apix, historical_apix)
        
        score = calculate_alert_score(wow_change, z_score, ml_anomaly_score, forecast_deviation)
        level = get_alert_level(score)
        
        # Sort contributors
        sorted_contributors = sorted(route_contributions.items(), key=lambda x: x[1], reverse=True)[:3]
        main_contributors = [{"route": k, "contribution": round(v, 2)} for k, v in sorted_contributors]
        
        formatted_lead_time = {k: round(v, 2) for k, v in lead_time_pressure.items()}

        message = AlertEngine._generate_message(level, main_contributors, formatted_lead_time)

        return {
            "severity": level,
            "score": score,
            "wow_change": round(wow_change, 2),
            "z_score": round(z_score, 2),
            "anomaly_score": round(ml_anomaly_score, 2),
            "forecast_deviation": round(forecast_deviation, 2),
            "apix_value": round(current_apix, 2),
            "message": message,
            "contributors_detail": main_contributors,
            "lead_time_pressure": formatted_lead_time,
            "created_at": datetime.now()
        }

    @staticmethod
    def _generate_message(level: str, main_contributors: list, lead_time_pressure: dict) -> str:
        if level == "NORMAL":
            return "Airfare prices are within normal range."
        
        msg = f"Airfare inflation is {level.lower()}."
        if main_contributors:
            top = main_contributors[0]
            msg += f" Primarily driven by {top['route']} ({top['contribution']:+.1f}%)."
        
        if lead_time_pressure.get("T+1", 0) > 10.0:
            msg += " ⚠ Near-term fares are driving the spike."
            
        return msg.strip()
