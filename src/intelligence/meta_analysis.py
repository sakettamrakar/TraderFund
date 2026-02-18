"""
Meta-Analysis Layer (L3).

Responsibility: Consolidate intelligence and enforce regime dependency.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import os as _os
import sys as _sys
import time
from traderfund.regime.types import MarketBehavior

_META_PROJECT_ROOT = _os.path.abspath(
    _os.path.join(_os.path.dirname(__file__), "..", "..", "..")
)
if _META_PROJECT_ROOT not in _sys.path:
    _sys.path.insert(0, _META_PROJECT_ROOT)

try:
    from automation.invariants.layer_integrations import gate_l3_trust as _gate_l3
except ImportError:  # pragma: no cover
    import logging as _logging
    _logging.getLogger(__name__).critical(
        "CATASTROPHIC FIREWALL UNAVAILABLE — L3 invariant gate disabled"
    )
    raise

class MetaAnalysis:
    """
    Implements L3 Meta-Analysis logic.
    """
    def __init__(self):
        self.trust_score = 0.0
        self.status = "PENDING"
        self.regime_state = None
        self.logger = logging.getLogger("MetaAnalysis")

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
                signal_type: str = "Standard",
                **kwargs) -> Dict[str, Any]:
        """
        Perform meta-analysis with strict regime dependency check (L3 Invariant 01).
        And Invariant 3: Regime-Aware Trust Adjustment.
        """
        start_time = time.perf_counter()
        
        # Prepare log fields
        log_signal_type = signal_type
        log_regime_context = regime_state
        log_reason = "Success"
        
        try:
            # Invariant 01 - Regime Dependency
            if not regime_state:
                self.trust_score = 0.0
                self.status = "INSUFFICIENT_CONTEXT"
                log_reason = "Meta-Analysis MUST NOT execute without L1 context."
                return {
                    "trust_score": self.trust_score,
                    "status": self.status,
                    "reason": log_reason
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
                    log_reason = f"Invariant 3 Violation: Breakout trust {technical_breakout_trust} > 0.50 in {regime_category} ({behavior})."
                    return {
                        "trust_score": self.trust_score,
                        "status": self.status,
                        "reason": log_reason
                    }

            # In TRENDING regime: Momentum trust ≥ 0.60 IF factor alignment present
            if regime_category == "TRENDING":
                if factor_alignment and momentum_trust < 0.60:
                    self.trust_score = 0.0
                    self.status = "REJECTED"
                    log_reason = f"Invariant 3 Violation: Momentum trust {momentum_trust} < 0.60 in TRENDING ({behavior}) with factor alignment."
                    return {
                        "trust_score": self.trust_score,
                        "status": self.status,
                        "reason": log_reason
                    }

            self.status = "ACTIVE"
            # Placeholder for actual meta-analysis logic
            self.trust_score = 1.0 # Mock success if context provided

            return {
                "trust_score": self.trust_score,
                "status": self.status,
                "regime_context": regime_state
            }
        finally:
            latency_ms = (time.perf_counter() - start_time) * 1000
            # Invariant 4 - Explainability Requirement
            self.logger.info(
                f"Trust Decision: Signal Type={log_signal_type} | "
                f"Regime Context={log_regime_context} | "
                f"Adjustment Reason={log_reason} | "
                f"Final Trust Score={self.trust_score} | "
                f"Computation Latency={latency_ms:.4f}ms"
            )
            # ── L3 Catastrophic Invariant Gate ──────────────────────────────
            # Only fires when no other exception is already propagating.
            import sys as _sys_exc
            if _sys_exc.exc_info()[0] is None:
                _gate_l3(self.trust_score)
