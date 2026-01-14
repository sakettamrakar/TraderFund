import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
from signals.core.enums import Market
from .enums import EventType, NarrativeState, NarrativeScope

@dataclass(frozen=True)
class Event:
    """
    Atomic market event.
    Input to Narrative Engine.
    """
    event_id: str
    event_type: EventType
    market: Market
    timestamp: datetime
    severity_score: float # 0.0 to 1.0
    source_reference: str # e.g., "signal:SIGNAL_UUID"
    payload: Dict[str, Any]
    
    # Optional asset for linking
    asset_id: Optional[str] = None
    
    @classmethod
    def create(cls, etype: EventType, market: Market, time: datetime, severity: float, source: str, payload: Dict, asset: str = None) -> 'Event':
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=etype,
            market=market,
            timestamp=time,
            severity_score=severity,
            source_reference=source,
            payload=payload,
            asset_id=asset
        )

@dataclass(frozen=True)
class Narrative:
    """
    Clustered story explaining market context.
    Immutable, Versioned.
    """
    narrative_id: str
    title: str
    market: Market
    scope: NarrativeScope
    
    # Relations
    related_assets: List[str]
    supporting_events: List[str] # List[event_id]
    
    # Confidence & State
    confidence_score: float
    lifecycle_state: NarrativeState
    version: int
    
    created_at: datetime
    updated_at: datetime
    
    explainability_payload: Dict[str, Any]
    
    @classmethod
    def create(cls, title: str, market: Market, scope: NarrativeScope, assets: List[str], events: List[str], confidence: float, explanation: Dict) -> 'Narrative':
        return cls(
            narrative_id=str(uuid.uuid4()),
            title=title,
            market=market,
            scope=scope,
            related_assets=assets,
            supporting_events=events,
            confidence_score=confidence,
            lifecycle_state=NarrativeState.BORN,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            explainability_payload=explanation
        )

    def transition_to(self, new_state: NarrativeState, reason: str = None) -> 'Narrative':
        data = asdict(self)
        data['lifecycle_state'] = new_state
        data['version'] = self.version + 1
        data['updated_at'] = datetime.utcnow()
        if reason:
             data['explainability_payload']['transition_reason'] = reason
             
        return Narrative(**data)
        
    def add_events(self, new_events: List[str], new_confidence: float) -> 'Narrative':
        """Reinforce narrative with new events."""
        data = asdict(self)
        # Append unique
        current = set(self.supporting_events)
        for e in new_events:
            current.add(e)
            
        data['supporting_events'] = list(current)
        data['confidence_score'] = new_confidence
        data['lifecycle_state'] = NarrativeState.REINFORCED
        data['version'] = self.version + 1
        data['updated_at'] = datetime.utcnow()
        
        return Narrative(**data)
    
    def to_dict(self):
        d = asdict(self)
        # DateTime serialization
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        # Enum serialization
        d['market'] = self.market.value
        d['scope'] = self.scope.value
        d['lifecycle_state'] = self.lifecycle_state.value
        return d
    
    @staticmethod
    def from_dict(d: Dict) -> 'Narrative':
        d['market'] = Market(d['market'])
        d['scope'] = NarrativeScope(d['scope'])
        d['lifecycle_state'] = NarrativeState(d['lifecycle_state'])
        for k in ['created_at', 'updated_at']:
            if d.get(k):
                d[k] = datetime.fromisoformat(d[k])
        return Narrative(**d)
