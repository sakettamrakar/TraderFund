import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from .enums import Market, SignalCategory, SignalDirection, SignalState

@dataclass(frozen=True)
class Signal:
    """
    Immutable Signal Object.
    Represents a single version of a market signal.
    """
    # Identity
    signal_id: str
    signal_name: str
    market: Market
    asset_id: str
    
    # Classification
    signal_category: SignalCategory
    direction: SignalDirection
    
    # Timing
    trigger_timestamp: datetime
    expected_horizon: str
    expiry_timestamp: datetime
    
    # State
    lifecycle_state: SignalState
    version: int
    created_at: datetime
    
    # Payload
    raw_strength: float
    explainability_payload: Dict[str, Any]
    
    # Optional / Mutable via Versioning
    confidence_score: Optional[float] = None
    invalidation_reason: Optional[str] = None
    
    @classmethod
    def create(cls, 
               name: str, 
               market: Market, 
               asset: str, 
               category: SignalCategory,
               direction: SignalDirection,
               trigger_time: datetime,
               horizon: str,
               expiry_time: datetime,
               strength: float,
               explanation: Dict,
               confidence: float = None) -> 'Signal':
        
        return cls(
            signal_id=str(uuid.uuid4()),
            signal_name=name,
            market=market,
            asset_id=asset,
            signal_category=category,
            direction=direction,
            trigger_timestamp=trigger_time,
            expected_horizon=horizon,
            expiry_timestamp=expiry_time,
            lifecycle_state=SignalState.CREATED,
            version=1,
            created_at=datetime.utcnow(),
            raw_strength=strength,
            explainability_payload=explanation,
            confidence_score=confidence
        )

    def transition_to(self, new_state: SignalState, reason: str = None) -> 'Signal':
        """
        Returns a NEW Signal instance with updated state and incremented version.
        Enforces valid transitions.
        """
        # Validator
        valid_transitions = {
            SignalState.CREATED: {SignalState.ACTIVE, SignalState.INVALIDATED},
            SignalState.ACTIVE: {SignalState.WEAKENED, SignalState.EXPIRED, SignalState.INVALIDATED},
            SignalState.WEAKENED: {SignalState.EXPIRED, SignalState.INVALIDATED},
            SignalState.EXPIRED: set(), # Terminal
            SignalState.INVALIDATED: set() # Terminal
        }
        
        if new_state not in valid_transitions.get(self.lifecycle_state, set()):
             raise ValueError(f"Invalid transition from {self.lifecycle_state} to {new_state}")

        # Create new dict from current
        data = asdict(self)
        data['lifecycle_state'] = new_state
        data['version'] = self.version + 1
        
        if reason:
            data['invalidation_reason'] = reason
            
        # Re-instantiate
        return Signal(**data)

    def update_confidence(self, new_score: float, explanation: Dict) -> 'Signal':
        """
        Returns a NEW Signal instance with updated confidence/explanation 
        and incremented version. State remains same.
        """
        data = asdict(self)
        data['confidence_score'] = new_score
        data['explainability_payload'] = explanation
        data['version'] = self.version + 1
        
        return Signal(**data)
        
    def to_dict(self) -> Dict:
        """Serializes to JSON-safe dictionary."""
        data = asdict(self)
        # Convert enums to strings
        data['market'] = self.market.value
        data['signal_category'] = self.signal_category.value
        data['direction'] = self.direction.value
        data['lifecycle_state'] = self.lifecycle_state.value
        
        # Convert datetimes to ISO
        for key in ['trigger_timestamp', 'expiry_timestamp', 'created_at']:
            val = getattr(self, key)
            if val:
                data[key] = val.isoformat()
                
        return data

    @staticmethod
    def from_dict(data: Dict) -> 'Signal':
        """Deserializes from dictionary."""
        # Enums
        data['market'] = Market(data['market'])
        data['signal_category'] = SignalCategory(data['signal_category'])
        data['direction'] = SignalDirection(data['direction'])
        data['lifecycle_state'] = SignalState(data['lifecycle_state'])
        
        # Datetimes
        for key in ['trigger_timestamp', 'expiry_timestamp', 'created_at']:
            if data.get(key):
                data[key] = datetime.fromisoformat(data[key])
                
        return Signal(**data)
