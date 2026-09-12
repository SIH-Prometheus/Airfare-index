from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertRuleType(str, Enum):
    WOW_PERCENT_CHANGE = "WOW_PERCENT_CHANGE"
    Z_SCORE_SPIKE = "Z_SCORE_SPIKE"
    ABSOLUTE_CHANGE = "ABSOLUTE_CHANGE"
    ML_ANOMALY = "ML_ANOMALY"

class Alert(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique alert identifier")
    triggered_at: datetime
    rule_type: AlertRuleType
    severity: AlertSeverity
    route_pair: str = Field(..., description="Affected route pair e.g. DEL-BOM")
    current_value: float = Field(..., description="Observed index or fare value")
    baseline_value: float = Field(..., description="Baseline index or fare value")
    percentage_change: float = Field(..., description="Percentage change observed")
    message: str = Field(..., description="Human-readable alert summary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional alert payload metadata")
