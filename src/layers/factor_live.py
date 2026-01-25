"""
Factor Layer Live State (L8 - Structural Activation).
Provides read-only factor exposures as descriptive metadata.

SAFETY INVARIANTS:
- This layer exposes FACTS, not CHOICES.
- No security scoring.
- No allocation triggering.
- No selection driving.
- No asset ranking by factor.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class FactorType(str, Enum):
    """Factor classification (READ-ONLY)."""
    MOMENTUM = "MOMENTUM"
    VALUE = "VALUE"
    QUALITY = "QUALITY"
    SIZE = "SIZE"
    VOLATILITY = "VOLATILITY"
    LIQUIDITY = "LIQUIDITY"


class FactorPermission(str, Enum):
    """Factor permission status (READ-ONLY)."""
    PERMITTED = "PERMITTED"
    FORBIDDEN = "FORBIDDEN"
    CONDITIONAL = "CONDITIONAL"


class FactorExposure(BaseModel):
    """
    Single factor exposure metadata.
    
    This is DESCRIPTIVE only. It describes what IS,
    not what SHOULD BE DONE.
    """
    factor_type: FactorType
    exposure_value: float = Field(default=0.0)
    permission: FactorPermission = FactorPermission.FORBIDDEN
    source: str = "factor_layer"
    timestamp: datetime = Field(default_factory=datetime.now)


class FactorSnapshot(BaseModel):
    """
    Immutable factor state snapshot.
    
    This is a DESCRIPTIVE data structure only.
    It MAY NOT be used for decision-making.
    """
    timestamp: datetime = Field(default_factory=datetime.now)
    exposures: Dict[str, FactorExposure] = Field(default_factory=dict)
    source: str = "factor_layer_live"


class FactorLayerLive:
    """
    Read-only factor state provider.
    
    SAFETY GUARANTEES:
    - Exposes exposure metadata only.
    - No methods that return scores, rankings, or allocations.
    - No methods that accept conditionals.
    - All state is immutable once created.
    """
    
    def __init__(self):
        self._current_snapshot: Optional[FactorSnapshot] = None
        self._history: list = []
    
    def update_snapshot(self, snapshot: FactorSnapshot) -> None:
        """
        Update the current factor snapshot.
        This is a STATE UPDATE, not a DECISION.
        """
        if self._current_snapshot is not None:
            self._history.append(self._current_snapshot)
        self._current_snapshot = snapshot
    
    def get_current(self) -> Optional[FactorSnapshot]:
        """Get current factor state (READ-ONLY)."""
        return self._current_snapshot
    
    def get_exposure(self, factor_type: FactorType) -> Optional[FactorExposure]:
        """Get exposure for a specific factor (READ-ONLY)."""
        if self._current_snapshot is None:
            return None
        return self._current_snapshot.exposures.get(factor_type.value)
    
    def get_permission(self, factor_type: FactorType) -> FactorPermission:
        """Get permission status for a factor (READ-ONLY)."""
        exposure = self.get_exposure(factor_type)
        if exposure is None:
            return FactorPermission.FORBIDDEN
        return exposure.permission
    
    def list_permitted_factors(self) -> List[FactorType]:
        """List all currently permitted factors (READ-ONLY, DESCRIPTIVE)."""
        if self._current_snapshot is None:
            return []
        return [
            FactorType(k) for k, v in self._current_snapshot.exposures.items()
            if v.permission == FactorPermission.PERMITTED
        ]
    
    # =========================================
    # FORBIDDEN OPERATIONS (NOT IMPLEMENTED)
    # =========================================
    # The following operations are EXPLICITLY FORBIDDEN:
    # - score_security()
    # - rank_by_factor()
    # - trigger_allocation()
    # - select_by_exposure()
    # - if_permitted_then()
    # Any function that takes factor state and produces
    # a decision, ranking, or action is INVALID.
