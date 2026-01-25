"""Narrative Diff - Models"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime
import uuid

class ChangeType(Enum):
    NONE = "none"
    PROMOTION = "promotion"
    DEGRADATION = "degradation"
    STABILIZATION = "stabilization"
    RISK_CHANGE = "risk_change"

@dataclass
class NarrativeDiff:
    diff_id: str
    symbol: str
    previous_narrative_id: Optional[str]
    current_narrative_id: str
    change_detected: bool
    change_type: str
    change_summary: str
    change_drivers: List[str]
    risk_implication: str  # improved/unchanged/increased
    confidence_shift: Optional[str]
    detected_at: str
    version: str
    
    def to_dict(self) -> dict:
        return {
            "diff_id": self.diff_id,
            "symbol": self.symbol,
            "previous_narrative_id": self.previous_narrative_id,
            "current_narrative_id": self.current_narrative_id,
            "change_detected": self.change_detected,
            "change_type": self.change_type,
            "change_summary": self.change_summary,
            "change_drivers": self.change_drivers,
            "risk_implication": self.risk_implication,
            "confidence_shift": self.confidence_shift,
            "detected_at": self.detected_at,
            "version": self.version,
        }
    
    @classmethod
    def no_change(cls, symbol: str, current_id: str, previous_id: Optional[str] = None):
        return cls(
            diff_id=str(uuid.uuid4())[:8],
            symbol=symbol,
            previous_narrative_id=previous_id,
            current_narrative_id=current_id,
            change_detected=False,
            change_type=ChangeType.NONE.value,
            change_summary="No meaningful change detected.",
            change_drivers=[],
            risk_implication="unchanged",
            confidence_shift=None,
            detected_at=datetime.utcnow().isoformat(),
            version="1.0.0",
        )
    
    @classmethod
    def create(cls, symbol: str, current_id: str, previous_id: str,
               change_type: ChangeType, summary: str, drivers: List[str],
               risk_impl: str, confidence_shift: Optional[str] = None):
        return cls(
            diff_id=str(uuid.uuid4())[:8],
            symbol=symbol,
            previous_narrative_id=previous_id,
            current_narrative_id=current_id,
            change_detected=True,
            change_type=change_type.value,
            change_summary=summary,
            change_drivers=drivers,
            risk_implication=risk_impl,
            confidence_shift=confidence_shift,
            detected_at=datetime.utcnow().isoformat(),
            version="1.0.0",
        )
