"""Narrative Evolution - Models"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class NarrativeType(Enum):
    STRUCTURAL_STRENGTH = "structural_strength"
    ENERGY_BUILDUP = "energy_buildup"
    EARLY_MOMENTUM = "early_momentum"
    CONFIRMED_MOMENTUM = "confirmed_momentum"
    MOMENTUM_FRAGILITY = "momentum_fragility"
    DEGRADATION = "degradation"
    NEUTRAL = "neutral"

class NarrativeState(Enum):
    EMERGING = "emerging"
    STRENGTHENING = "strengthening"
    STABLE = "stable"
    WEAKENING = "weakening"
    INVALIDATED = "invalidated"

class LifecycleStatus(Enum):
    ACTIVE = "active"
    DECAYING = "decaying"
    ARCHIVED = "archived"

@dataclass
class StageEvidence:
    """Stage-level evidence supporting a narrative."""
    structural_score: Optional[float] = None
    energy_score: Optional[float] = None
    participation_score: Optional[float] = None
    momentum_score: Optional[float] = None
    risk_score: Optional[float] = None
    risk_profile: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "structural_score": self.structural_score,
            "energy_score": self.energy_score,
            "participation_score": self.participation_score,
            "momentum_score": self.momentum_score,
            "risk_score": self.risk_score,
            "risk_profile": self.risk_profile,
        }

@dataclass
class Narrative:
    """Core narrative object."""
    narrative_id: str
    symbol: str
    narrative_type: str
    narrative_state: str
    narrative_summary: str
    supporting_evidence: Dict[str, float]
    confidence_level: str
    risk_context: str
    lifecycle_status: str
    created_at: str
    last_updated: str
    what_changed: str
    version: str
    previous_state: Optional[str] = None
    days_in_state: int = 0
    
    def to_dict(self) -> dict:
        return {
            "narrative_id": self.narrative_id,
            "symbol": self.symbol,
            "narrative_type": self.narrative_type,
            "narrative_state": self.narrative_state,
            "narrative_summary": self.narrative_summary,
            "supporting_evidence": self.supporting_evidence,
            "confidence_level": self.confidence_level,
            "risk_context": self.risk_context,
            "lifecycle_status": self.lifecycle_status,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "what_changed": self.what_changed,
            "version": self.version,
            "previous_state": self.previous_state,
            "days_in_state": self.days_in_state,
        }
    
    @classmethod
    def create(cls, symbol: str, narrative_type: NarrativeType, 
               evidence: StageEvidence, summary: str, 
               risk_context: str, what_changed: str = "Initial generation"):
        now = datetime.utcnow().isoformat()
        
        # Determine confidence from evidence spread
        scores = [v for v in evidence.to_dict().values() if isinstance(v, (int, float))]
        avg = sum(scores) / len(scores) if scores else 0
        confidence = "high" if avg >= 60 else "moderate" if avg >= 40 else "low"
        
        return cls(
            narrative_id=str(uuid.uuid4())[:8],
            symbol=symbol,
            narrative_type=narrative_type.value,
            narrative_state=NarrativeState.EMERGING.value,
            narrative_summary=summary,
            supporting_evidence=evidence.to_dict(),
            confidence_level=confidence,
            risk_context=risk_context,
            lifecycle_status=LifecycleStatus.ACTIVE.value,
            created_at=now,
            last_updated=now,
            what_changed=what_changed,
            version="1.0.0",
        )
