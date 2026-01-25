import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional
from signals.core.enums import Market, SignalCategory
from .enums import RecommendationType, ReviewStatus

@dataclass(frozen=True)
class AdvisoryScore:
    """
    Internal scoring metrics calculated for advisory purposes.
    Not for live use.
    """
    category_health_score: float # 0-100
    calibration_error_magnitude: float
    regime_sensitivity: float
    stability_duration_days: int

@dataclass(frozen=True)
class EvolutionProposal:
    """
    A proposal to evolve the signal engine.
    Strictly advisory.
    """
    proposal_id: str
    generated_at: datetime
    
    # Target
    market: Market
    signal_category: SignalCategory
    
    # Advice
    recommendation: RecommendationType
    suggested_action: str # Text description
    confidence_level: str # HIGH/MED/LOW logic confidence
    
    # Evidence
    advisory_score: AdvisoryScore
    evidence_payload: Dict[str, Any] # Links to Insight IDs, Metrics
    
    # Workflow
    review_status: ReviewStatus
    review_notes: Optional[str]
    
    @classmethod
    def create(cls, market: Market, category: SignalCategory, 
               rec: RecommendationType, action: str, conf: str, 
               score: AdvisoryScore, evidence: Dict) -> 'EvolutionProposal':
        
        return cls(
            proposal_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            market=market,
            signal_category=category,
            recommendation=rec,
            suggested_action=action,
            confidence_level=conf,
            advisory_score=score,
            evidence_payload=evidence,
            review_status=ReviewStatus.PENDING,
            review_notes=None
        )

    def to_dict(self):
        d = asdict(self)
        d['generated_at'] = d['generated_at'].isoformat()
        d['market'] = d['market'].value
        d['signal_category'] = d['signal_category'].value
        d['recommendation'] = d['recommendation'].value
        d['review_status'] = d['review_status'].value
        return d
