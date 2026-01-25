"""Stage 4: Momentum Confirmation - Models"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import date

class MomentumState(Enum):
    NONE = "none"
    EMERGING = "emerging"
    CONFIRMED = "confirmed"

@dataclass
class BehaviorScore:
    name: str
    score: float
    evidence_used: Dict[str, float] = field(default_factory=dict)
    evidence_missing: List[str] = field(default_factory=list)

@dataclass
class MomentumConfirmation:
    symbol: str
    evaluation_date: str
    momentum_score: float
    momentum_state: str
    behavior_breakdown: Dict[str, float]
    evidence_summary: Dict[str, float]
    participation_score: Optional[float]
    confidence_level: str
    known_limitations: List[str]
    version: str
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol, "evaluation_date": self.evaluation_date,
            "momentum_score": self.momentum_score, "momentum_state": self.momentum_state,
            "behavior_breakdown": self.behavior_breakdown, "evidence_summary": self.evidence_summary,
            "participation_score": self.participation_score, "confidence_level": self.confidence_level,
            "known_limitations": self.known_limitations, "version": self.version,
        }
    
    @classmethod
    def create(cls, symbol: str, behavior_scores: List[BehaviorScore], weights: Dict[str, float],
               participation_score: Optional[float], known_limitations: List[str], version: str):
        from . import config
        total_weight = sum(weights.get(bs.name, 0) for bs in behavior_scores)
        weighted_sum = sum(bs.score * weights.get(bs.name, 0) for bs in behavior_scores)
        final_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0
        
        behavior_breakdown = {bs.name: round(bs.score, 2) for bs in behavior_scores}
        evidence_summary = {k: v for bs in behavior_scores for k, v in bs.evidence_used.items()}
        
        if final_score >= config.STATE_THRESHOLDS["confirmed"]:
            state = MomentumState.CONFIRMED.value
        elif final_score >= config.STATE_THRESHOLDS["emerging"]:
            state = MomentumState.EMERGING.value
        else:
            state = MomentumState.NONE.value
        
        confidence = "high" if final_score >= 70 else "moderate" if final_score >= 40 else "low"
        
        return cls(symbol=symbol, evaluation_date=date.today().isoformat(),
                   momentum_score=round(final_score, 2), momentum_state=state,
                   behavior_breakdown=behavior_breakdown,
                   evidence_summary={k: round(v, 4) for k, v in evidence_summary.items()},
                   participation_score=participation_score, confidence_level=confidence,
                   known_limitations=known_limitations, version=version)
