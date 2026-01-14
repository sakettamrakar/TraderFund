"""Stage 5: Sustainability & Risk - Models"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import date

class RiskProfile(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

@dataclass
class BehaviorScore:
    name: str
    score: float
    evidence_used: Dict[str, float] = field(default_factory=dict)
    evidence_missing: List[str] = field(default_factory=list)

@dataclass
class SustainabilityRisk:
    symbol: str
    evaluation_date: str
    sustainability_score: float
    failure_risk_score: float
    risk_profile: str
    behavior_breakdown: Dict[str, float]
    evidence_summary: Dict[str, float]
    recommended_posture: str
    momentum_score: Optional[float]
    confidence_level: str
    known_limitations: List[str]
    version: str
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol, "evaluation_date": self.evaluation_date,
            "sustainability_score": self.sustainability_score, "failure_risk_score": self.failure_risk_score,
            "risk_profile": self.risk_profile, "behavior_breakdown": self.behavior_breakdown,
            "evidence_summary": self.evidence_summary, "recommended_posture": self.recommended_posture,
            "momentum_score": self.momentum_score, "confidence_level": self.confidence_level,
            "known_limitations": self.known_limitations, "version": self.version,
        }
    
    @classmethod
    def create(cls, symbol: str, behavior_scores: List[BehaviorScore], weights: Dict[str, float],
               momentum_score: Optional[float], known_limitations: List[str], version: str):
        from . import config
        total_weight = sum(weights.get(bs.name, 0) for bs in behavior_scores)
        weighted_sum = sum(bs.score * weights.get(bs.name, 0) for bs in behavior_scores)
        risk_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0
        sustainability_score = 100 - risk_score
        
        behavior_breakdown = {bs.name: round(bs.score, 2) for bs in behavior_scores}
        evidence_summary = {k: v for bs in behavior_scores for k, v in bs.evidence_used.items()}
        
        if risk_score >= config.RISK_THRESHOLDS["high"]:
            risk_profile = RiskProfile.HIGH.value
        elif risk_score >= config.RISK_THRESHOLDS["moderate"]:
            risk_profile = RiskProfile.MODERATE.value
        else:
            risk_profile = RiskProfile.LOW.value
        
        posture = config.POSTURE_MAP.get(risk_profile, "monitor")
        confidence = "high" if sustainability_score >= 70 else "moderate" if sustainability_score >= 40 else "low"
        
        return cls(symbol=symbol, evaluation_date=date.today().isoformat(),
                   sustainability_score=round(sustainability_score, 2), failure_risk_score=round(risk_score, 2),
                   risk_profile=risk_profile, behavior_breakdown=behavior_breakdown,
                   evidence_summary={k: round(v, 4) for k, v in evidence_summary.items()},
                   recommended_posture=posture, momentum_score=momentum_score,
                   confidence_level=confidence, known_limitations=known_limitations, version=version)
