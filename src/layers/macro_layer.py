"""
Macro Layer State (L8 - Structural Activation).
Provides read-only macro context as immutable state snapshots.

SAFETY INVARIANTS:
- This layer exposes FACTS, not CHOICES.
- No signal generation.
- No opportunity labeling.
- No asset ranking.
- No conditional logic on values.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RegimeState(str, Enum):
    """Macro regime classification (READ-ONLY)."""
    EXPANSION = "EXPANSION"
    CONTRACTION = "CONTRACTION"
    RECOVERY = "RECOVERY"
    SLOWDOWN = "SLOWDOWN"
    UNDEFINED = "UNDEFINED"


class RateEnvironment(str, Enum):
    """Rate environment classification (READ-ONLY)."""
    RISING = "RISING"
    FALLING = "FALLING"
    STABLE = "STABLE"
    UNDEFINED = "UNDEFINED"


class MacroSnapshot(BaseModel):
    """
    Immutable macro state snapshot.
    
    This is a DESCRIPTIVE data structure only.
    It MAY NOT be used for decision-making.
    """
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Regime context (read-only)
    regime: RegimeState = RegimeState.UNDEFINED
    regime_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Rate environment (read-only)
    rate_environment: RateEnvironment = RateEnvironment.UNDEFINED
    
    # Inflation context (read-only)
    inflation_trend: Optional[str] = None
    
    # Source provenance
    source: str = "macro_layer"


class MacroLayer:
    """
    Read-only macro state provider.
    
    SAFETY GUARANTEES:
    - Exposes state snapshots only.
    - No methods that return signals, scores, or rankings.
    - No methods that accept callbacks or conditionals.
    - All state is immutable once created.
    """
    
    def __init__(self):
        self._current_snapshot: Optional[MacroSnapshot] = None
        self._history: list = []
    
    def update_snapshot(self, snapshot: MacroSnapshot) -> None:
        """
        Update the current macro snapshot.
        This is a STATE UPDATE, not a DECISION.
        """
        if self._current_snapshot is not None:
            self._history.append(self._current_snapshot)
        self._current_snapshot = snapshot
    
    def get_current(self) -> Optional[MacroSnapshot]:
        """Get current macro state (READ-ONLY)."""
        return self._current_snapshot
    
    def get_regime(self) -> RegimeState:
        """Get current regime classification (READ-ONLY)."""
        if self._current_snapshot is None:
            return RegimeState.UNDEFINED
        return self._current_snapshot.regime
    
    def get_rate_environment(self) -> RateEnvironment:
        """Get current rate environment (READ-ONLY)."""
        if self._current_snapshot is None:
            return RateEnvironment.UNDEFINED
        return self._current_snapshot.rate_environment
    
    # =========================================
    # FORBIDDEN OPERATIONS (NOT IMPLEMENTED)
    # =========================================
    # The following operations are EXPLICITLY FORBIDDEN:
    # - generate_signal()
    # - label_opportunity()
    # - rank_assets()
    # - score_by_macro()
    # - if_regime_then()
    # Any function that takes macro state and produces
    # a decision, ranking, or signal is INVALID.
