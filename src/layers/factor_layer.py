"""
Factor Layer (L6.5) - Operationalizes Factor Layer Policy.
Produces FactorPermission objects for strategy gating.
"""
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel

class FactorPermission(BaseModel):
    momentum_permitted: bool
    value_permitted: bool
    max_exposure: Dict[str, float]
    granted_at: datetime
    expires_at: Optional[datetime]

def get_factor_permissions(regime_state: dict) -> FactorPermission:
    # Placeholder for policy enforcement logic
    return FactorPermission(
        momentum_permitted=False,
        value_permitted=False,
        max_exposure={},
        granted_at=datetime.utcnow()
    )
