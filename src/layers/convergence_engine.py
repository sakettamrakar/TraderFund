"""
Convergence Engine (L6) — Weighted-Vector Regime-Aware Signal Aggregation
==========================================================================
Aggregates structured LensSignals using a weighted vector model with
regime-adjusted weights, enforces multi-lens confirmation & minimum confluence,
applies portfolio bias, performance feedback, dispersion penalty, and computes
a deterministic convergence score with conviction grading.

Guarantees:
  • Zero randomness — identical inputs always produce identical output
  • All scores bounded to [0.0, 1.0]
  • Fail-safe on any missing or degenerate input
  • Full explainability: weights, variance, penalties, biases logged
  • No external calls, no global mutable state, no time-based logic
  • Computation latency measured and enforced (< 1000 ms)
  • Weight normalization stable (no float drift > 1e-8)
  • Portfolio bias never positive, magnitude ≤ 0.40
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from collections import Counter
from typing import Dict, List, Optional

from src.feedback.performance_feedback import PerformanceContext, PerformanceFeedbackEngine
from src.models.convergence_models import (
    ConvergenceResult,
    ConvergenceStatus,
    LensSignal,
)
from src.models.meta_models import RegimeState

# ── Module-level constants ────────────────────────────────────────────────────
_MIN_LENSES_FOR_ELIGIBLE = 3
_MIN_LENSES_FOR_GRADE_A = 4
_LATENCY_LIMIT_MS = 1000.0
_DISPERSION_THRESHOLD = 0.22
_MIN_CONFLUENCE_SCORE = 0.60
_MIN_CONFLUENCE_COUNT = 3

_GRADE_THRESHOLDS = (
    (0.80, "A"),
    (0.65, "B"),
    (0.50, "C"),
)  # anything below → D

# ── Base lens weights (sum = 1.00 for the canonical 5-lens set) ───────────────
_BASE_WEIGHTS: Dict[str, float] = {
    "SENTIMENT":   0.20,  # N — Narrative
    "FLOW":        0.25,  # F — Factor
    "FUNDAMENTAL": 0.20,  # U — Fundamental
    "TECHNICAL":   0.20,  # T — Technical
    "MOMENTUM":    0.15,  # S — Strategy alignment
    "VOLATILITY":  0.20,  # extra lens, uses Fundamental weight
}

# ── Regime weight adjustments ─────────────────────────────────────────────────
_REGIME_WEIGHT_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "TRENDING": {
        "TECHNICAL": +0.05,
        "FLOW":      +0.05,
    },
    "CHOP": {
        "SENTIMENT":   +0.05,
        "FUNDAMENTAL": +0.05,
        "TECHNICAL":   -0.05,
    },
    "STRESS": {
        "FUNDAMENTAL": +0.10,
        "TECHNICAL":   -0.10,
    },
}


# ── File logger ───────────────────────────────────────────────────────────────
def _build_logger(name: str, filename: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        _root = os.path.dirname(os.path.abspath(__file__))
        for _ in range(8):
            if os.path.isdir(os.path.join(_root, "src")):
                break
            _root = os.path.dirname(_root)
        log_dir = os.path.join(_root, "logs")
        os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(os.path.join(log_dir, filename), encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(fh)
        logger.setLevel(logging.INFO)
    return logger


_logger = _build_logger("convergence_engine", "convergence_engine.log")


class ConvergenceEngine:
    """
    L6 Convergence Engine — Weighted Vector Model.

    Accepts:
        lenses              — list of LensSignal from independent analytical lenses
        regime              — RegimeState from L1
        meta_trust          — float trust score from L3 MetaAnalysis
        performance_context — optional PerformanceContext for Phase A feedback
        portfolio_bias      — optional per-strategy bias from PortfolioFeedbackEngine
                              Must be in [-0.40, 0.0]; clamped if out of range.

    Returns:
        ConvergenceResult — fully populated, deterministic
    """

    def compute(
        self,
        lenses: List[LensSignal],
        regime: RegimeState,
        meta_trust: float,
        performance_context: Optional[PerformanceContext] = None,
        portfolio_bias: float = 0.0,
    ) -> ConvergenceResult:
        start = time.perf_counter()

        lenses = lenses if lenses is not None else []
        lens_count = len(lenses)
        regime_str = getattr(regime, "regime", None) if regime is not None else None
        meta_trust_clamped = self._clamp(meta_trust)

        # Clamp portfolio bias: must be <= 0.0 and >= -0.40
        portfolio_bias = max(-0.40, min(0.0, float(portfolio_bias) if portfolio_bias is not None else 0.0))

        # ── Fail-safe gate ────────────────────────────────────────────────────
        if meta_trust_clamped == 0.0 or regime_str is None or lens_count < 2:
            return self._fail_safe(start, lenses, regime_str, meta_trust_clamped)

        # ── Invariant: Directional alignment ─────────────────────────────────
        directions = [ls.direction for ls in lenses]
        unique_dirs = set(directions)
        if len(unique_dirs) > 1:
            return self._conflict_result(start, lenses, regime_str, meta_trust_clamped)

        winning_direction = directions[0]
        aligned_lenses = lens_count

        # ── Invariant: Multi-lens requirement ─────────────────────────────────
        status: ConvergenceStatus = "OK"
        if lens_count < _MIN_LENSES_FOR_ELIGIBLE:
            status = "LOW_CONFIDENCE"

        # ── Regime compatibility gate ─────────────────────────────────────────
        compatibilities = [self._clamp(ls.regime_compatibility) for ls in lenses]
        avg_regime_compat = sum(compatibilities) / len(compatibilities)
        if avg_regime_compat < 0.50:
            status = "REGIME_MISMATCH"

        # ── Confidence extraction ─────────────────────────────────────────────
        confidences = [self._clamp(ls.confidence) for ls in lenses]
        mean_conf = sum(confidences) / len(confidences)

        # ── Dispersion (variance of raw confidences) ──────────────────────────
        dispersion = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
        if dispersion > _DISPERSION_THRESHOLD:
            if status == "OK":
                status = "HIGH_DISPERSION"

        # ── Weighted vector scoring (Phase F) ─────────────────────────────────
        lens_weights = self._compute_regime_weights(lenses, regime_str)
        weighted_score = sum(
            lens_weights.get(ls.lens_name, 0.0) * self._clamp(ls.confidence)
            for ls in lenses
        )

        # ── Score dispersion penalty (on the weighted scores) ─────────────────
        lens_scores = [self._clamp(ls.confidence) for ls in lenses]
        d_penalty = self._dispersion_penalty(lens_scores)

        # ── Minimum confluence rule ───────────────────────────────────────────
        confluence_count = sum(1 for s in lens_scores if s >= _MIN_CONFLUENCE_SCORE)
        if confluence_count < _MIN_CONFLUENCE_COUNT and status == "OK":
            status = "WATCHLIST"

        # ── Convergence score formula ─────────────────────────────────────────
        raw_score = (
            weighted_score
            * meta_trust_clamped
            * avg_regime_compat
            + d_penalty
        )
        base_score = self._clamp(raw_score)

        # ── Performance modifier (Phase A) ────────────────────────────────────
        performance_modifier = 0.0
        if performance_context is not None:
            performance_modifier = PerformanceFeedbackEngine().compute_modifier(
                performance_context
            )

        # ── Portfolio bias (Phase E) ──────────────────────────────────────────
        final_score = self._clamp(
            base_score * (1.0 + performance_modifier) * (1.0 + portfolio_bias)
        )

        # ── Conviction grading ────────────────────────────────────────────────
        grade = self._assign_grade(final_score, aligned_lenses, status)

        # ── Latency guard ─────────────────────────────────────────────────────
        latency = (time.perf_counter() - start) * 1000.0
        if latency > _LATENCY_LIMIT_MS:
            return self._fail_safe(
                start, lenses, regime_str, meta_trust_clamped,
                override_status="LATENCY_VIOLATION",
            )

        input_hash = self._compute_hash(
            lenses, regime_str, meta_trust_clamped, performance_context,
            portfolio_bias,
        )

        weights_json = json.dumps(
            {k: round(v, 8) for k, v in sorted(lens_weights.items())},
            sort_keys=True, separators=(",", ":"),
        )

        _logger.info(json.dumps({
            "component": "ConvergenceEngine",
            "symbol": lenses[0].symbol if lenses else "",
            "weights": lens_weights,
            "variance": round(dispersion, 8),
            "dispersion_penalty": round(d_penalty, 6),
            "portfolio_bias": round(portfolio_bias, 6),
            "base_score": round(base_score, 6),
            "performance_modifier": round(performance_modifier, 6),
            "final_score": round(final_score, 6),
            "status": status,
            "latency_ms": round(latency, 3),
            "input_hash": input_hash,
        }, separators=(",", ":")))

        return ConvergenceResult(
            symbol=lenses[0].symbol if lenses else "",
            direction=winning_direction,
            lens_count=lens_count,
            aligned_lenses=aligned_lenses,
            mean_confidence=mean_conf,
            meta_trust=meta_trust_clamped,
            avg_regime_compatibility=avg_regime_compat,
            score_dispersion=dispersion,
            final_score=final_score,
            conviction_grade=grade,
            status=status,
            latency_ms=latency,
            input_hash=input_hash,
            base_score=base_score,
            performance_modifier=performance_modifier,
            lens_weights=weights_json,
            dispersion_penalty=d_penalty,
            portfolio_bias=portfolio_bias,
        )

    # ── Weighted vector helpers ───────────────────────────────────────────────

    @staticmethod
    def _compute_regime_weights(
        lenses: List[LensSignal], regime_str: str
    ) -> Dict[str, float]:
        """
        Compute normalised weights for the supplied lenses, adjusted for regime.

        Only lenses present in the input get weights. The weights are drawn from
        _BASE_WEIGHTS, adjusted by _REGIME_WEIGHT_ADJUSTMENTS, then normalised
        so they sum to exactly 1.0.
        """
        present_names = [ls.lens_name for ls in lenses]
        raw_weights: Dict[str, float] = {}
        for name in present_names:
            raw_weights[name] = raw_weights.get(name, 0.0) + _BASE_WEIGHTS.get(name, 0.20)

        # Average the weight if a lens_name appears multiple times
        name_counts: Dict[str, int] = {}
        for name in present_names:
            name_counts[name] = name_counts.get(name, 0) + 1
        for name in raw_weights:
            if name_counts.get(name, 1) > 1:
                raw_weights[name] = raw_weights[name] / name_counts[name]

        # Apply regime adjustments
        adjustments = _REGIME_WEIGHT_ADJUSTMENTS.get(regime_str, {})
        for lens_name, delta in adjustments.items():
            if lens_name in raw_weights:
                raw_weights[lens_name] = raw_weights[lens_name] + delta

        # Ensure non-negative
        for k in raw_weights:
            if raw_weights[k] < 0.0:
                raw_weights[k] = 0.0

        # Normalise
        total = sum(raw_weights.values())
        if total <= 0.0:
            # Degenerate: equal weights
            n = len(raw_weights)
            return {k: 1.0 / n if n > 0 else 0.0 for k in raw_weights}

        return {k: v / total for k, v in raw_weights.items()}

    @staticmethod
    def _dispersion_penalty(scores: List[float]) -> float:
        """
        Compute a dispersion penalty based on variance of lens scores.

        variance < 0.02  → -0.05  (too tightly clustered, possible groupthink)
        variance > 0.20  → -0.10  (too dispersed, weak signal)
        otherwise        →  0.00
        """
        if not scores:
            return 0.0
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        if variance < 0.02:
            return -0.05
        if variance > 0.20:
            return -0.10
        return 0.0

    # ── Grading ───────────────────────────────────────────────────────────────

    @staticmethod
    def _assign_grade(
        score: float, aligned_lenses: int, status: ConvergenceStatus
    ) -> str:
        """Deterministic grade assignment. Grade A requires >= 4 aligned lenses."""
        for threshold, grade in _GRADE_THRESHOLDS:
            if score >= threshold:
                if grade == "A" and aligned_lenses < _MIN_LENSES_FOR_GRADE_A:
                    return "B"
                return grade
        return "D"

    # ── Hashing ───────────────────────────────────────────────────────────────

    @staticmethod
    def _compute_hash(
        lenses: List[LensSignal],
        regime_str: str,
        meta_trust: float,
        performance_context: Optional[PerformanceContext] = None,
        portfolio_bias: float = 0.0,
    ) -> str:
        """SHA-256 (16-char prefix) over the deterministic canonical serialisation."""
        lens_payload = sorted(
            [
                {
                    "symbol": ls.symbol,
                    "direction": ls.direction,
                    "confidence": float(ls.confidence),
                    "regime_compatibility": float(ls.regime_compatibility),
                    "lens_name": ls.lens_name,
                }
                for ls in lenses
            ],
            key=lambda d: d["lens_name"],
        )
        perf_payload = None
        if performance_context is not None:
            perf_payload = {
                "strategy_id": performance_context.strategy_id,
                "realized_hit_rate": float(performance_context.realized_hit_rate),
                "expected_hit_rate": float(performance_context.expected_hit_rate),
                "realized_avg_return": float(performance_context.realized_avg_return),
                "expected_avg_return": float(performance_context.expected_avg_return),
            }
        payload = json.dumps(
            {
                "lenses": lens_payload,
                "meta_trust": float(meta_trust),
                "performance_context": perf_payload,
                "portfolio_bias": float(portfolio_bias),
                "regime": regime_str,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _clamp(value) -> float:
        if value is None:
            return 0.0
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    def _fail_safe(
        self,
        start: float,
        lenses: List[LensSignal],
        regime_str,
        meta_trust: float,
        override_status: ConvergenceStatus = "INSUFFICIENT_CONVERGENCE",
    ) -> ConvergenceResult:
        latency = (time.perf_counter() - start) * 1000.0
        symbol = lenses[0].symbol if lenses else ""
        lens_count = len(lenses)
        input_hash = (
            self._compute_hash(lenses, regime_str or "UNDEFINED", meta_trust)
            if lenses
            else ""
        )
        return ConvergenceResult(
            symbol=symbol,
            direction="NONE",
            lens_count=lens_count,
            aligned_lenses=0,
            mean_confidence=0.0,
            meta_trust=meta_trust,
            avg_regime_compatibility=0.0,
            score_dispersion=0.0,
            final_score=0.0,
            conviction_grade="D",
            status=override_status,
            latency_ms=latency,
            input_hash=input_hash,
            base_score=0.0,
            performance_modifier=0.0,
        )

    def _conflict_result(
        self,
        start: float,
        lenses: List[LensSignal],
        regime_str: str,
        meta_trust: float,
    ) -> ConvergenceResult:
        latency = (time.perf_counter() - start) * 1000.0
        symbol = lenses[0].symbol if lenses else ""
        lens_count = len(lenses)
        input_hash = self._compute_hash(lenses, regime_str, meta_trust)
        return ConvergenceResult(
            symbol=symbol,
            direction="CONFLICT",
            lens_count=lens_count,
            aligned_lenses=0,
            mean_confidence=0.0,
            meta_trust=meta_trust,
            avg_regime_compatibility=0.0,
            score_dispersion=0.0,
            final_score=0.0,
            conviction_grade="D",
            status="DIRECTION_CONFLICT",
            latency_ms=latency,
            input_hash=input_hash,
            base_score=0.0,
            performance_modifier=0.0,
        )

    # ── Stability hook ────────────────────────────────────────────────────────

    @staticmethod
    def get_convergence_health() -> dict:
        return {
            "multi_lens_enforced": True,
            "dispersion_logged": True,
            "directional_integrity": True,
        }
