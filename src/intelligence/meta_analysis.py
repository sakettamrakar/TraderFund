"""
Meta-Analysis Layer (L3).

Responsibility: Consolidate intelligence and enforce regime dependency.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from traderfund.regime.types import MarketBehavior

class MetaAnalysis:
    """
    Implements L3 Meta-Analysis logic.
    """
    def __init__(self):
        self.trust_score = 0.0
        self.status = "PENDING"
        self.regime_state = None

    def _get_regime_category(self, behavior: Any) -> str:
        """
        Classifies MarketBehavior into CHOP, TRANSITION, or TRENDING.
        """
        # Ensure behavior is compared correctly whether it's string or Enum
        if behavior in [MarketBehavior.MEAN_REVERTING_LOW_VOL, MarketBehavior.MEAN_REVERTING_HIGH_VOL]:
            return "CHOP"
        elif behavior in [MarketBehavior.TRENDING_NORMAL_VOL, MarketBehavior.TRENDING_HIGH_VOL]:
            return "TRENDING"
        else:
            return "TRANSITION"

    def analyze(self,
                regime_state: Optional[Dict[str, Any]] = None,
                technical_breakout_trust: float = 0.0,
                momentum_trust: float = 0.0,
                factor_alignment: bool = False,
                **kwargs) -> Dict[str, Any]:
        """
        Perform meta-analysis with strict regime dependency check (L3 Invariant 01).
        And Invariant 3: Regime-Aware Trust Adjustment.
        """
        # Invariant 01 - Regime Dependency
        if not regime_state:
            self.trust_score = 0.0
            self.status = "INSUFFICIENT_CONTEXT"
            return {
                "trust_score": self.trust_score,
                "status": self.status,
                "reason": "Meta-Analysis MUST NOT execute without L1 context."
            }

        self.regime_state = regime_state

        # Extract behavior from regime_state
        behavior = regime_state.get("behavior")

        # Default to UNDEFINED if not present (handled as TRANSITION)
        if not behavior:
            behavior = MarketBehavior.UNDEFINED

        regime_category = self._get_regime_category(behavior)

        # Invariant 3 — Regime-Aware Trust Adjustment
        # In CHOP or TRANSITION regime: Technical breakout trust ≤ 0.50
        if regime_category in ["CHOP", "TRANSITION"]:
            if technical_breakout_trust > 0.50:
                self.trust_score = 0.0
                self.status = "REJECTED"
                return {
                    "trust_score": self.trust_score,
                    "status": self.status,
                    "reason": f"Invariant 3 Violation: Breakout trust {technical_breakout_trust} > 0.50 in {regime_category} ({behavior})."
                }

        # In TRENDING regime: Momentum trust ≥ 0.60 IF factor alignment present
        if regime_category == "TRENDING":
            if factor_alignment and momentum_trust < 0.60:
                self.trust_score = 0.0
                self.status = "REJECTED"
                return {
                    "trust_score": self.trust_score,
                    "status": self.status,
                    "reason": f"Invariant 3 Violation: Momentum trust {momentum_trust} < 0.60 in TRENDING ({behavior}) with factor alignment."
                }

        self.status = "ACTIVE"
        # Placeholder for actual meta-analysis logic
        self.trust_score = 1.0 # Mock success if context provided

        return {
            "trust_score": self.trust_score,
            "status": self.status,
            "regime_context": regime_state
        }
