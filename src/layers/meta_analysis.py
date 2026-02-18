"""
Meta-Analysis Layer (L3) — Regime-Aware Cognitive Trust Engine
==============================================================
Does exactly 3 things:
  1. Consume RegimeState (L1)
  2. Apply regime-specific trust adjustment rules
  3. Enforce deterministic trust math with full explainability

Guarantees:
  • Zero randomness — same inputs always produce the same output (Invariant 6)
  • All trust scores bounded to [0.0, 1.0] (Invariant 2)
  • Fail-safe on any missing or invalid input (Invariant 5)
  • Structured log for every trust decision (Invariant 4)
  • Computation latency measured and enforced
  • No external calls, no global state, no datetime.now()
"""
import hashlib
import json
import logging
import os
import time
from typing import Optional

from src.feedback.stability_adapter import StabilityAdapter
from src.models.meta_models import RegimeState, SignalInput, TrustResult

_VALID_REGIMES = frozenset({
    "TRENDING",
    "CHOP",
    "TRANSITION",
    "STRESS",
    "VOLATILE",
    "ACCUMULATION",
    "DISTRIBUTION",
})

_LATENCY_LIMIT_MS = 1000.0


# ── File logger ───────────────────────────────────────────────────────────────────────────────
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


_logger = _build_logger("meta_analysis", "meta_analysis.log")


class MetaAnalysis:

    def __init__(self, stability_score: Optional[float] = None) -> None:
        """
        Parameters
        ----------
        stability_score : float | None
            Default stability score injected for every ``analyze()`` call when no
            per-call value is supplied.  ``None`` defers to ``StabilityAdapter``
            at call time (production default).  Pass an explicit float to pin
            stability for testing or specialised use-cases.
        """
        self._default_stability_score = stability_score

    def analyze(
        self,
        regime: RegimeState,
        signal: SignalInput,
        stability_score: Optional[float] = None,
    ) -> TrustResult:
        start = time.perf_counter()

        # Invariant 1 — Regime must be a known valid value
        regime_str = getattr(regime, "regime", None)
        if regime_str not in _VALID_REGIMES:
            sig_type = getattr(signal, "signal_type", "") if signal is not None else ""
            return self._fail_safe("INVALID_REGIME", start, "STRESS", sig_type, 0.0)

        # Invariant 5 — Signal must exist
        if signal is None:
            return self._fail_safe("INSUFFICIENT_CONTEXT", start, regime_str, "", 0.0)

        # Validate base_confidence is numeric
        try:
            base = self._clamp(signal.base_confidence)
        except (TypeError, ValueError):
            return self._fail_safe(
                "INSUFFICIENT_CONTEXT", start, regime_str, signal.signal_type, 0.0
            )

        adjusted, reason = self._apply_regime_rules(
            regime_str, signal.signal_type, base, signal.factor_alignment
        )
        raw_trust = self._clamp(adjusted)  # Invariant 2 — defensive final boundary

        # ── Stability dampening (Phase C adaptive feedback) ──────────────────────────
        if stability_score is None:
            stability_score = (
                self._default_stability_score
                if self._default_stability_score is not None
                else StabilityAdapter().get_stability("MetaAnalysis")
            )
        stability_score = self._clamp(stability_score)
        effective_trust = self._clamp(raw_trust * stability_score)

        input_hash = self.compute_hash_input(regime, signal, stability_score)

        latency = (time.perf_counter() - start) * 1000.0
        if latency > _LATENCY_LIMIT_MS:
            return self._fail_safe(
                "LATENCY_VIOLATION", start, regime_str, signal.signal_type, base
            )

        structured = {
            "signal_type": signal.signal_type,
            "regime": regime_str,
            "base_confidence": base,
            "adjustment_reason": reason,
            "raw_trust": raw_trust,
            "stability_score": stability_score,
            "effective_trust": effective_trust,
            "final_trust": effective_trust,   # ← kept for backward-compat with existing tests
            "latency_ms": round(latency, 6),
            "input_hash": input_hash,
        }

        _logger.info(json.dumps({
            "component": "MetaAnalysis",
            "regime": regime_str,
            "signal_type": signal.signal_type,
            "raw_trust": round(raw_trust, 6),
            "stability_score": round(stability_score, 6),
            "effective_trust": round(effective_trust, 6),
            "latency_ms": round(latency, 3),
            "input_hash": input_hash,
        }, separators=(",", ":")))

        return TrustResult(
            trust_score=effective_trust,
            status="OK",
            regime_context=regime_str,
            adjustment_reason=reason,
            computation_latency_ms=latency,
            signal_type=signal.signal_type,
            base_confidence=base,
            deterministic_input_hash=input_hash,
            structured_log=json.dumps(structured, separators=(",", ":")),
            raw_trust=raw_trust,
            stability_score=stability_score,
            effective_trust=effective_trust,
        )

    def _apply_regime_rules(
        self, regime: str, signal_type: str, base: float, factor_alignment: bool
    ):
        """Regime-specific trust adjustment.  Every regime has explicit logic — no silent fall-through."""

        # ── CHOP / TRANSITION ────────────────────────────────────────────────
        if regime in ("CHOP", "TRANSITION"):
            if signal_type == "TECHNICAL_BREAKOUT":
                return min(base, 0.50), "Breakout suppressed in CHOP/TRANSITION"
            if signal_type == "MOMENTUM":
                return base * 0.80, "Momentum dampened in CHOP/TRANSITION"
            return base, f"NO_ADJUSTMENT ({regime})"

        # ── TRENDING ─────────────────────────────────────────────────────────
        if regime == "TRENDING":
            if signal_type == "MOMENTUM" and factor_alignment:
                return max(base, 0.60), "Momentum boosted in TRENDING with factor alignment"
            if signal_type == "TECHNICAL_BREAKOUT":
                return max(base, 0.55), "Breakout supported in TRENDING"
            return base, f"NO_ADJUSTMENT ({regime})"

        # ── STRESS ───────────────────────────────────────────────────────────
        if regime == "STRESS":
            return base * 0.60, "All signals dampened in STRESS regime"

        # ── VOLATILE ─────────────────────────────────────────────────────────
        if regime == "VOLATILE":
            if signal_type == "TECHNICAL_BREAKOUT":
                return min(base, 0.45), "Breakout capped in VOLATILE regime"
            return base, f"NO_ADJUSTMENT ({regime})"

        # ── ACCUMULATION ─────────────────────────────────────────────────────
        if regime == "ACCUMULATION":
            if signal_type == "MOMENTUM":
                return max(base, 0.55), "Momentum boosted in ACCUMULATION"
            return base, f"NO_ADJUSTMENT ({regime})"

        # ── DISTRIBUTION ─────────────────────────────────────────────────────
        if regime == "DISTRIBUTION":
            if signal_type == "MOMENTUM":
                return min(base, 0.50), "Momentum suppressed in DISTRIBUTION"
            return base, f"NO_ADJUSTMENT ({regime})"

        return 0.0, "UNKNOWN_REGIME_FAIL_SAFE"  # pragma: no cover

    def compute_hash_input(
        self,
        regime: RegimeState,
        signal: SignalInput,
        stability_score: float = 1.0,
    ) -> str:
        """Deterministic SHA-256 (16-char prefix) over the canonical input tuple."""
        payload = json.dumps(
            {
                "regime": regime.regime,
                "signal_type": signal.signal_type,
                "base_confidence": float(signal.base_confidence),
                "factor_alignment": bool(signal.factor_alignment),
                "stability_score": float(stability_score),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def _clamp(self, value) -> float:
        if value is None:
            return 0.0
        return max(0.0, min(1.0, float(value)))

    def _fail_safe(
        self,
        status: str,
        start: float,
        regime_ctx: str = "STRESS",
        signal_type: str = "",
        base: float = 0.0,
    ) -> TrustResult:
        latency = (time.perf_counter() - start) * 1000.0
        structured = {
            "signal_type": signal_type,
            "regime": regime_ctx,
            "base_confidence": base,
            "adjustment_reason": "FAIL_SAFE",
            "final_trust": 0.0,
            "latency_ms": round(latency, 6),
            "input_hash": "",
        }
        return TrustResult(
            trust_score=0.0,
            status=status,
            regime_context=regime_ctx,
            adjustment_reason="FAIL_SAFE",
            computation_latency_ms=latency,
            signal_type=signal_type,
            base_confidence=base,
            deterministic_input_hash="",
            structured_log=json.dumps(structured, separators=(",", ":")),
            raw_trust=0.0,
            stability_score=1.0,
            effective_trust=0.0,
        )

    def get_health_status(self) -> dict:
        return {
            "deterministic": True,
            "regime_required": True,
            "trust_bounds_enforced": True,
        }
