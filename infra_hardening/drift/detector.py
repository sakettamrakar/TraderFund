from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum, unique
import numpy as np

@unique
class DriftType(str, Enum):
    VOLUME_SPIKE = "VOLUME_SPIKE"
    VOLUME_DROP = "VOLUME_DROP"
    PRICE_GAP = "PRICE_GAP"
    MISSING_DAYS = "MISSING_DAYS"
    SCHEMA_CHANGE = "SCHEMA_CHANGE"

@unique
class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

@dataclass
class DriftEvent:
    event_id: str
    drift_type: DriftType
    severity: Severity
    market: str
    asset: Optional[str]
    detected_at: datetime
    description: str
    evidence: dict

class DriftDetector:
    """
    Detects statistical anomalies in OHLCV data.
    """
    def __init__(self, volume_threshold: float = 3.0, gap_threshold: float = 0.10):
        self.vol_thresh = volume_threshold # Std devs
        self.gap_thresh = gap_threshold    # 10% price gap
        
    def detect_volume_anomaly(self, volumes: List[float], asset: str, market: str) -> Optional[DriftEvent]:
        if len(volumes) < 10:
            return None
            
        recent = volumes[-1]
        historical = volumes[:-1]
        mean = np.mean(historical)
        std = np.std(historical)
        
        if std == 0:
            return None
            
        z_score = (recent - mean) / std
        
        if z_score > self.vol_thresh:
            return DriftEvent(
                event_id=f"drift_{datetime.utcnow().timestamp()}",
                drift_type=DriftType.VOLUME_SPIKE,
                severity=Severity.WARNING,
                market=market,
                asset=asset,
                detected_at=datetime.utcnow(),
                description=f"Volume spike detected: {z_score:.2f} std devs above mean.",
                evidence={"z_score": z_score, "recent": recent, "mean": mean}
            )
        elif z_score < -self.vol_thresh:
            return DriftEvent(
                event_id=f"drift_{datetime.utcnow().timestamp()}",
                drift_type=DriftType.VOLUME_DROP,
                severity=Severity.WARNING,
                market=market,
                asset=asset,
                detected_at=datetime.utcnow(),
                description=f"Volume drop detected: {abs(z_score):.2f} std devs below mean.",
                evidence={"z_score": z_score, "recent": recent, "mean": mean}
            )
        return None

    def detect_price_gap(self, closes: List[float], asset: str, market: str) -> Optional[DriftEvent]:
        if len(closes) < 2:
            return None
            
        prev = closes[-2]
        curr = closes[-1]
        pct_change = abs(curr - prev) / prev
        
        if pct_change > self.gap_thresh:
            return DriftEvent(
                event_id=f"drift_{datetime.utcnow().timestamp()}",
                drift_type=DriftType.PRICE_GAP,
                severity=Severity.CRITICAL,
                market=market,
                asset=asset,
                detected_at=datetime.utcnow(),
                description=f"Price gap of {pct_change*100:.1f}% detected.",
                evidence={"prev_close": prev, "curr_close": curr, "pct_change": pct_change}
            )
        return None
