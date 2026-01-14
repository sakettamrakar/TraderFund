import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from signals.core.enums import Market
from .enums import AlphaPatternType, ValidationState

@dataclass(frozen=True)
class AlphaHypothesis:
    """
    Stuctured Hypothesis of a cross-market alpha pattern.
    Example: "US Tech Leads India IT by 1 Day"
    """
    alpha_id: str
    title: str
    pattern_type: AlphaPatternType
    
    # Context
    source_market: Market
    target_market: Market
    related_assets: List[str] # e.g. ["QQQ", "NIFTYIT"]
    
    # Evidence & Confidence
    confidence_score: float # 0-100
    decay_profile: str      # e.g., "FAST", "SLOW"
    validation_state: ValidationState
    version: int
    
    # Traceability
    supporting_signals: List[str]    # signal_ids
    supporting_narratives: List[str] # narrative_ids
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    evidence_payload: Dict[str, Any] # Statistical proof
    
    @classmethod
    def create(cls, title: str, pattern: AlphaPatternType, source: Market, target: Market, assets: List[str], confidence: float, evidence: Dict) -> 'AlphaHypothesis':
        return cls(
            alpha_id=str(uuid.uuid4()),
            title=title,
            pattern_type=pattern,
            source_market=source,
            target_market=target,
            related_assets=assets,
            confidence_score=confidence,
            decay_profile="SLOW", # Default
            validation_state=ValidationState.PROPOSED,
            version=1,
            supporting_signals=[],
            supporting_narratives=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            evidence_payload=evidence
        )

    def update_evidence(self, new_confidence: float, new_evidence: Dict) -> 'AlphaHypothesis':
        """Updates belief with new data."""
        data = asdict(self)
        data['confidence_score'] = new_confidence
        data['evidence_payload'] = new_evidence
        data['updated_at'] = datetime.utcnow()
        data['version'] = self.version + 1
        
        # State Promotion Logic (Simple)
        if new_confidence > 80.0:
            data['validation_state'] = ValidationState.CONFIRMED
        elif new_confidence < 20.0:
            data['validation_state'] = ValidationState.INVALIDATED
            
        return AlphaHypothesis(**data)

    def to_dict(self):
        d = asdict(self)
        d['pattern_type'] = self.pattern_type.value
        d['source_market'] = self.source_market.value
        d['target_market'] = self.target_market.value
        d['validation_state'] = self.validation_state.value
        for k in ['created_at', 'updated_at']:
            if d.get(k):
                d[k] = datetime.isoformat(d[k])
        return d

    @staticmethod
    def from_dict(d: Dict) -> 'AlphaHypothesis':
        d['pattern_type'] = AlphaPatternType(d['pattern_type'])
        d['source_market'] = Market(d['source_market'])
        d['target_market'] = Market(d['target_market'])
        d['validation_state'] = ValidationState(d['validation_state'])
        for k in ['created_at', 'updated_at']:
             if d.get(k):
                 d[k] = datetime.fromisoformat(d[k])
        return AlphaHypothesis(**d)
