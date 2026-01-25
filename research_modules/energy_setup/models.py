"""
Stage 2: Energy Setup - Data Models
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional
from datetime import date


class EnergyState(Enum):
    """Energy state classification."""
    NONE = "none"
    FORMING = "forming"
    MATURE = "mature"


@dataclass
class BehaviorScore:
    """Score for a single energy behavior."""
    name: str
    score: float
    evidence_used: Dict[str, float] = field(default_factory=dict)
    evidence_missing: List[str] = field(default_factory=list)


@dataclass
class EnergySetup:
    """Complete energy setup assessment for a symbol."""
    
    symbol: str
    evaluation_date: str
    energy_setup_score: float  # 0-100
    energy_state: str  # none/forming/mature
    behavior_breakdown: Dict[str, float]
    evidence_summary: Dict[str, float]
    structural_score: Optional[float]  # From Stage 1
    confidence_level: str
    known_limitations: List[str]
    version: str
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "evaluation_date": self.evaluation_date,
            "energy_setup_score": self.energy_setup_score,
            "energy_state": self.energy_state,
            "behavior_breakdown": self.behavior_breakdown,
            "evidence_summary": self.evidence_summary,
            "structural_score": self.structural_score,
            "confidence_level": self.confidence_level,
            "known_limitations": self.known_limitations,
            "version": self.version,
        }
    
    @classmethod
    def create(
        cls,
        symbol: str,
        behavior_scores: List[BehaviorScore],
        weights: Dict[str, float],
        structural_score: Optional[float],
        known_limitations: List[str],
        version: str,
    ) -> "EnergySetup":
        from . import config
        
        # Calculate weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        behavior_breakdown = {}
        evidence_summary = {}
        
        for bs in behavior_scores:
            weight = weights.get(bs.name, 0.0)
            weighted_sum += bs.score * weight
            total_weight += weight
            behavior_breakdown[bs.name] = round(bs.score, 2)
            evidence_summary.update(bs.evidence_used)
        
        final_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0
        
        # Determine energy state
        if final_score >= config.ENERGY_STATE_THRESHOLDS["mature"]:
            energy_state = EnergyState.MATURE.value
        elif final_score >= config.ENERGY_STATE_THRESHOLDS["forming"]:
            energy_state = EnergyState.FORMING.value
        else:
            energy_state = EnergyState.NONE.value
        
        # Determine confidence
        if final_score >= config.CONFIDENCE_THRESHOLDS["high"] * 100:
            confidence = "high"
        elif final_score >= config.CONFIDENCE_THRESHOLDS["moderate"] * 100:
            confidence = "moderate"
        else:
            confidence = "low"
        
        return cls(
            symbol=symbol,
            evaluation_date=date.today().isoformat(),
            energy_setup_score=round(final_score, 2),
            energy_state=energy_state,
            behavior_breakdown=behavior_breakdown,
            evidence_summary={k: round(v, 4) for k, v in evidence_summary.items()},
            structural_score=structural_score,
            confidence_level=confidence,
            known_limitations=known_limitations,
            version=version,
        )
