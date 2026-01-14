"""
Stage 1: Structural Capability - Data Models

Output schema for structural capability evaluation.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional
from datetime import date


class ConfidenceLevel(Enum):
    """Confidence classification for structural capability."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


@dataclass
class BehaviorScore:
    """Score for a single structural behavior."""
    
    name: str
    score: float  # 0-100
    evidence_used: Dict[str, float] = field(default_factory=dict)
    evidence_missing: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "score": self.score,
            "evidence_used": self.evidence_used,
            "evidence_missing": self.evidence_missing,
        }


@dataclass
class StructuralCapability:
    """
    Complete structural capability assessment for a symbol.
    
    This is the output contract between Stage 1 and Stage 2.
    """
    
    symbol: str
    evaluation_date: str
    structural_capability_score: float  # 0-100
    behavior_breakdown: Dict[str, float]
    evidence_summary: Dict[str, float]
    confidence_level: str
    known_limitations: List[str]
    version: str
    
    # Optional detailed breakdown
    behavior_details: Optional[List[BehaviorScore]] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "evaluation_date": self.evaluation_date,
            "structural_capability_score": self.structural_capability_score,
            "behavior_breakdown": self.behavior_breakdown,
            "evidence_summary": self.evidence_summary,
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
        known_limitations: List[str],
        version: str,
    ) -> "StructuralCapability":
        """
        Factory method to create capability from behavior scores.
        """
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
        
        # Determine confidence level
        from . import config
        if final_score >= config.CONFIDENCE_THRESHOLDS["high"] * 100:
            confidence = ConfidenceLevel.HIGH.value
        elif final_score >= config.CONFIDENCE_THRESHOLDS["moderate"] * 100:
            confidence = ConfidenceLevel.MODERATE.value
        else:
            confidence = ConfidenceLevel.LOW.value
        
        return cls(
            symbol=symbol,
            evaluation_date=date.today().isoformat(),
            structural_capability_score=round(final_score, 2),
            behavior_breakdown=behavior_breakdown,
            evidence_summary={k: round(v, 4) for k, v in evidence_summary.items()},
            confidence_level=confidence,
            known_limitations=known_limitations,
            version=version,
            behavior_details=behavior_scores,
        )
