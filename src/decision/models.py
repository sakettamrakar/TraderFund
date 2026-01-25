from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

class DecisionAction(Enum):
    ENTER = "ENTER"
    EXIT = "EXIT"
    HOLD = "HOLD"
    DO_NOTHING = "DO_NOTHING"

@dataclass
class Decision:
    decision_id: str
    timestamp: str
    narrative_ref: str
    action: DecisionAction
    confidence: float
    rationale: str
    risk_parameters: Dict[str, Any]
    
    @classmethod
    def create(cls, narrative_id: str, action: DecisionAction, confidence: float, rationale: str, risk: Dict = None):
        return cls(
            decision_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            narrative_ref=narrative_id,
            action=action,
            confidence=confidence,
            rationale=rationale,
            risk_parameters=risk or {}
        )
        
    def to_dict(self):
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp,
            "narrative_ref": self.narrative_ref,
            "action": self.action.value,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "risk_parameters": self.risk_parameters
        }
