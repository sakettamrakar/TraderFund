"""
Performance Feedback Engine — Rolling Strategy Performance Modifier
===================================================================
Computes a deterministic performance modifier in [-0.20, +0.20] that reflects
how a strategy's realized 30-session rolling metrics compare to its expected
baseline.  The modifier is consumed by L6 ConvergenceEngine to nudge final
convergence scores toward empirical evidence.

Guarantees:
  • Zero randomness — identical inputs → identical modifier
  • Modifier strictly clamped to [-0.20, +0.20]
  • No external calls, no global mutable state, no I/O
"""
from __future__ import annotations

from dataclasses import dataclass

# ── Constants ─────────────────────────────────────────────────────────────────

_MODIFIER_CAP: float = 0.20          # hard ceiling / floor on the modifier
_HIT_WEIGHT: float = 0.60            # relative weight of hit-rate signal
_RETURN_WEIGHT: float = 0.40         # relative weight of return signal
_RETURN_NORM_FLOOR: float = 0.01     # minimum denominator for return normalisation
                                     # prevents division by zero when expected ≈ 0


# ── Data contract ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PerformanceContext:
    """
    30-session rolling performance snapshot for a single strategy.

    Fields
    ------
    strategy_id           : identifier matching the strategy registry key
    realized_hit_rate     : fraction of profitable sessions over the window, [0, 1]
    expected_hit_rate     : backtest-derived baseline, [0, 1]
    realized_avg_return   : mean session return over the window  (e.g. 0.018 = 1.8%)
    expected_avg_return   : backtest-derived mean session return (e.g. 0.015 = 1.5%)
    """
    strategy_id: str
    realized_hit_rate: float
    expected_hit_rate: float
    realized_avg_return: float
    expected_avg_return: float


# ── Engine ────────────────────────────────────────────────────────────────────

class PerformanceFeedbackEngine:
    """
    Deterministic strategy performance → convergence score modifier.

    Formula
    -------
        hit_delta               = realized_hit_rate   - expected_hit_rate
        return_delta            = realized_avg_return - expected_avg_return
        return_delta_normalized = clamp(return_delta / max(|expected_avg_return|, 0.01),
                                        -1.0, +1.0)
        modifier_raw            = 0.60 * hit_delta + 0.40 * return_delta_normalized
        modifier                = clamp(modifier_raw, -0.20, +0.20)

    Interpretation
    --------------
    modifier > 0  → strategy outperforming → convergence score nudged upward
    modifier < 0  → strategy underperforming → convergence score nudged downward
    modifier = 0  → no evidence of divergence from baseline
    """

    def compute_modifier(self, context: PerformanceContext) -> float:
        """
        Return modifier ∈ [-0.20, +0.20].  Fully deterministic.

        Parameters
        ----------
        context : PerformanceContext — strategy performance snapshot

        Returns
        -------
        float — performance modifier, strictly in [-0.20, +0.20]
        """
        realized_hit = _clamp_unit(context.realized_hit_rate)
        expected_hit = _clamp_unit(context.expected_hit_rate)
        hit_delta = realized_hit - expected_hit

        return_delta = context.realized_avg_return - context.expected_avg_return
        norm_factor = max(abs(context.expected_avg_return), _RETURN_NORM_FLOOR)
        return_delta_normalized = max(-1.0, min(1.0, return_delta / norm_factor))

        modifier_raw = _HIT_WEIGHT * hit_delta + _RETURN_WEIGHT * return_delta_normalized
        return max(-_MODIFIER_CAP, min(_MODIFIER_CAP, modifier_raw))

    def describe(self, context: PerformanceContext) -> dict:
        """
        Return a fully observable breakdown of the modifier computation.
        Useful for logging and glass-box auditing.
        """
        modifier = self.compute_modifier(context)
        realized_hit = _clamp_unit(context.realized_hit_rate)
        expected_hit = _clamp_unit(context.expected_hit_rate)
        hit_delta = realized_hit - expected_hit
        return_delta = context.realized_avg_return - context.expected_avg_return
        norm_factor = max(abs(context.expected_avg_return), _RETURN_NORM_FLOOR)
        return_delta_normalized = max(-1.0, min(1.0, return_delta / norm_factor))
        modifier_raw = _HIT_WEIGHT * hit_delta + _RETURN_WEIGHT * return_delta_normalized
        return {
            "strategy_id": context.strategy_id,
            "hit_delta": round(hit_delta, 6),
            "return_delta": round(return_delta, 6),
            "return_delta_normalized": round(return_delta_normalized, 6),
            "modifier_raw": round(modifier_raw, 6),
            "modifier_clamped": round(modifier, 6),
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
