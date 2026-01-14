"""Stage 3: Participation Trigger - Models"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import date

class TriggerState(Enum):
    NONE = "none"
    EMERGING = "emerging"
    ACTIVE = "active"

@dataclass
class BehaviorScore:
    name: str
    score: float
    evidence_used: Dict[str, float] = field(default_factory=dict)
    evidence_missing: List[str] = field(default_factory=list)

@dataclass
class ParticipationTrigger:
    symbol: str
    evaluation_date: str
    participation_score: float
    trigger_state: str
    behavior_breakdown: Dict[str, float]
    evidence_summary: Dict[str, float]
    energy_score: Optional[float]
    confidence_level: str
    known_limitations: List[str]
    version: str
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol, "evaluation_date": self.evaluation_date,
            "participation_score": self.participation_score, "trigger_state": self.trigger_state,
            "behavior_breakdown": self.behavior_breakdown, "evidence_summary": self.evidence_summary,
            "energy_score": self.energy_score, "confidence_level": self.confidence_level,
            "known_limitations": self.known_limitations, "version": self.version,
        }
    
    @classmethod
    def create(cls, symbol: str, behavior_scores: List[BehaviorScore], weights: Dict[str, float],
               energy_score: Optional[float], known_limitations: List[str], version: str):
        from . import config
        total_weight = sum(weights.get(bs.name, 0) for bs in behavior_scores)
        weighted_sum = sum(bs.score * weights.get(bs.name, 0) for bs in behavior_scores)
        final_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0
        
        behavior_breakdown = {bs.name: round(bs.score, 2) for bs in behavior_scores}
        evidence_summary = {}
        for bs in behavior_scores:
            evidence_summary.update(bs.evidence_used)
        
        if final_score >= config.TRIGGER_STATE_THRESHOLDS["active"]:
            trigger_state = TriggerState.ACTIVE.value
        elif final_score >= config.TRIGGER_STATE_THRESHOLDS["emerging"]:
            trigger_state = TriggerState.EMERGING.value
        else:
            trigger_state = TriggerState.NONE.value
        
        confidence = "high" if final_score >= 70 else "moderate" if final_score >= 40 else "low"
        
        return cls(symbol=symbol, evaluation_date=date.today().isoformat(),
                   participation_score=round(final_score, 2), trigger_state=trigger_state,
                   behavior_breakdown=behavior_breakdown,
                   evidence_summary={k: round(v, 4) for k, v in evidence_summary.items()},
                   energy_score=energy_score, confidence_level=confidence,
                   known_limitations=known_limitations, version=version)
