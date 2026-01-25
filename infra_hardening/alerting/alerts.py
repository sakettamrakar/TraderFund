from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from enum import Enum, unique

@unique
class AlertLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class Alert:
    alert_id: str
    level: AlertLevel
    source: str # "DRIFT", "INTEGRITY", "API_HEALTH"
    message: str
    created_at: datetime
    acknowledged: bool = False

class AlertManager:
    """
    Centralized alert collection.
    Alerts are actionable, not auto-fixes.
    """
    def __init__(self):
        self._alerts: List[Alert] = []
        
    def raise_alert(self, level: AlertLevel, source: str, message: str) -> Alert:
        a = Alert(
            alert_id=f"alert_{datetime.utcnow().timestamp()}",
            level=level,
            source=source,
            message=message,
            created_at=datetime.utcnow()
        )
        self._alerts.append(a)
        print(f"[{level.value}] [{source}] {message}")
        return a
        
    def get_unacknowledged(self) -> List[Alert]:
        return [a for a in self._alerts if not a.acknowledged]
        
    def acknowledge(self, alert_id: str):
        for a in self._alerts:
            if a.alert_id == alert_id:
                a.acknowledged = True
                break
                
    def clear_all(self):
        self._alerts = []
