"""
Portfolio Feedback Engine — Strategy-Level Bias Modifier
=========================================================
Computes a deterministic per-strategy bias modifier in [-0.40, 0.0] based on
portfolio exposure, drawdown, and strategy health.

The bias flows:  Portfolio State → Bias Modifier → Convergence Weighting

Guarantees:
  • Bias is never positive — cannot reinforce via portfolio feedback
  • Bias magnitude ≤ 0.40
  • Identical inputs → identical bias (deterministic)
  • Does not modify trust, stability, strategy health, or regime
  • Zero randomness, no I/O, no external calls
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

# ── Constants ─────────────────────────────────────────────────────────────────

_BIAS_FLOOR: float = -0.40       # absolute minimum bias per strategy

# Exposure thresholds
_EXPOSURE_THRESHOLD_1: float = 0.40
_EXPOSURE_BIAS_1: float = -0.15
_EXPOSURE_THRESHOLD_2: float = 0.55
_EXPOSURE_BIAS_2: float = -0.30

# Drawdown thresholds
_DRAWDOWN_THRESHOLD_1: float = 0.08
_DRAWDOWN_BIAS_1: float = -0.10
_DRAWDOWN_THRESHOLD_2: float = 0.15
_DRAWDOWN_BIAS_2: float = -0.20

# Strategy health threshold
_HEALTH_THRESHOLD: float = 0.50
_HEALTH_BIAS: float = -0.10


# ── Data contract ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PortfolioContext:
    """
    Snapshot of portfolio state for feedback calculation.

    Fields
    ------
    strategy_exposures     : {strategy_id: exposure_value} — capital allocated per strategy
    strategy_health_scores : {strategy_id: health_score} — rolling health ∈ [0, 1]
    current_drawdown       : portfolio-level drawdown as fraction (0.10 = 10%)
    regime                 : current regime string (for informational logging only)
    """
    strategy_exposures: Dict[str, float]
    strategy_health_scores: Dict[str, float]
    current_drawdown: float
    regime: str


# ── Engine ────────────────────────────────────────────────────────────────────

class PortfolioFeedbackEngine:
    """
    Deterministic portfolio state → per-strategy bias modifier.

    Steps:
      1. Exposure pressure: penalise strategies consuming > 40% or > 55% of total
      2. Drawdown guard: global bias when portfolio drawdown > 8% or > 15%
      3. Strategy underperformance dampener: penalise strategies with health < 0.50

    Output: {strategy_id: bias} where bias ∈ [-0.40, 0.0]
    """

    def compute_bias(self, context: PortfolioContext) -> Dict[str, float]:
        """
        Return {strategy_id: bias_modifier} for every strategy in the portfolio.

        All values are in [-0.40, 0.0].  No positive bias is ever produced.
        """
        exposures = context.strategy_exposures
        health_scores = context.strategy_health_scores
        drawdown = max(0.0, float(context.current_drawdown))

        total_exposure = sum(exposures.values())
        if total_exposure <= 0.0:
            total_exposure = 1.0  # avoid division by zero; no exposure → no penalty

        # Global drawdown bias (applies to all strategies)
        drawdown_bias = self._drawdown_guard(drawdown)

        result: Dict[str, float] = {}
        for strategy_id, exposure in exposures.items():
            # Step 1 — Exposure pressure
            exposure_bias = self._exposure_pressure(exposure, total_exposure)

            # Step 3 — Strategy health dampener
            health = health_scores.get(strategy_id, 1.0)
            health_bias = self._health_dampener(health)

            # Combine: sum all bias components, then clamp
            raw_bias = exposure_bias + drawdown_bias + health_bias
            clamped_bias = max(_BIAS_FLOOR, min(0.0, raw_bias))
            result[strategy_id] = clamped_bias

        return result

    def describe(self, context: PortfolioContext) -> Dict[str, dict]:
        """
        Return per-strategy breakdown of bias components for observability.
        """
        exposures = context.strategy_exposures
        health_scores = context.strategy_health_scores
        drawdown = max(0.0, float(context.current_drawdown))

        total_exposure = sum(exposures.values())
        if total_exposure <= 0.0:
            total_exposure = 1.0

        drawdown_bias = self._drawdown_guard(drawdown)

        breakdown: Dict[str, dict] = {}
        for strategy_id, exposure in exposures.items():
            exposure_ratio = exposure / total_exposure
            exposure_bias = self._exposure_pressure(exposure, total_exposure)
            health = health_scores.get(strategy_id, 1.0)
            health_bias = self._health_dampener(health)
            raw_bias = exposure_bias + drawdown_bias + health_bias
            clamped = max(_BIAS_FLOOR, min(0.0, raw_bias))
            breakdown[strategy_id] = {
                "exposure_ratio": round(exposure_ratio, 6),
                "exposure_bias": round(exposure_bias, 6),
                "drawdown_bias": round(drawdown_bias, 6),
                "health_score": round(health, 6),
                "health_bias": round(health_bias, 6),
                "raw_bias": round(raw_bias, 6),
                "clamped_bias": round(clamped, 6),
            }
        return breakdown

    # ── Steps ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _exposure_pressure(strategy_exposure: float, total_exposure: float) -> float:
        """Step 1: penalise strategy crowding."""
        ratio = strategy_exposure / total_exposure
        if ratio > _EXPOSURE_THRESHOLD_2:
            return _EXPOSURE_BIAS_2
        if ratio > _EXPOSURE_THRESHOLD_1:
            return _EXPOSURE_BIAS_1
        return 0.0

    @staticmethod
    def _drawdown_guard(drawdown: float) -> float:
        """Step 2: global drawdown penalty."""
        if drawdown > _DRAWDOWN_THRESHOLD_2:
            return _DRAWDOWN_BIAS_2
        if drawdown > _DRAWDOWN_THRESHOLD_1:
            return _DRAWDOWN_BIAS_1
        return 0.0

    @staticmethod
    def _health_dampener(health_score: float) -> float:
        """Step 3: penalise unhealthy strategies."""
        if health_score < _HEALTH_THRESHOLD:
            return _HEALTH_BIAS
        return 0.0
