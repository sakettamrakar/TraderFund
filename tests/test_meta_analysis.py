"""
Comprehensive test suite — L3 Meta-Analysis (src/layers/meta_analysis.py).
Covers invariants 1–6 + regime matrix + explainability completeness.
"""
import json
import time

import pytest

from src.layers.meta_analysis import MetaAnalysis
from src.models.meta_models import RegimeState, SignalInput


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def regime(r="TRENDING", vol=0.3):
    return RegimeState(regime=r, volatility=vol)


def signal(sig_type="MOMENTUM", confidence=0.75, alignment=True):
    return SignalInput(signal_type=sig_type, base_confidence=confidence, factor_alignment=alignment)


# ---------------------------------------------------------------------------
# A) Boundary Precision
# ---------------------------------------------------------------------------
class TestBoundaryPrecision:
    def test_breakout_clamp_at_0_50_in_chop(self):
        result = MetaAnalysis().analyze(regime("CHOP"), signal("TECHNICAL_BREAKOUT", 0.90))
        assert result.trust_score == 0.50

    def test_breakout_clamp_at_0_50_in_transition(self):
        result = MetaAnalysis().analyze(regime("TRANSITION"), signal("TECHNICAL_BREAKOUT", 0.90))
        assert result.trust_score == 0.50

    def test_momentum_floor_at_0_60_in_trending(self):
        result = MetaAnalysis().analyze(regime("TRENDING"), signal("MOMENTUM", 0.40, True))
        assert result.trust_score == 0.60

    def test_volatile_breakout_cap_at_0_45(self):
        result = MetaAnalysis().analyze(regime("VOLATILE"), signal("TECHNICAL_BREAKOUT", 0.80))
        assert result.trust_score == 0.45

    def test_max_clamp_at_1_0(self):
        result = MetaAnalysis().analyze(regime("TRENDING"), signal("MOMENTUM", 2.0, True))
        assert result.trust_score == 1.0

    def test_min_clamp_at_0_0_from_negative_base(self):
        result = MetaAnalysis().analyze(regime("TRENDING"), signal("MOMENTUM", -1.0, False))
        assert result.trust_score == 0.0

    def test_fail_safe_always_returns_0_0(self):
        result = MetaAnalysis().analyze(regime("TRENDING"), signal=None)
        assert result.trust_score == 0.0

    def test_accumulation_momentum_floor_at_0_55(self):
        result = MetaAnalysis().analyze(regime("ACCUMULATION"), signal("MOMENTUM", 0.20))
        assert result.trust_score == 0.55

    def test_distribution_momentum_cap_at_0_50(self):
        result = MetaAnalysis().analyze(regime("DISTRIBUTION"), signal("MOMENTUM", 0.90))
        assert result.trust_score == 0.50

    def test_trending_breakout_floor_at_0_55(self):
        result = MetaAnalysis().analyze(regime("TRENDING"), signal("TECHNICAL_BREAKOUT", 0.30))
        assert result.trust_score == 0.55


# ---------------------------------------------------------------------------
# B) Determinism Replay (Invariant 6)
# ---------------------------------------------------------------------------
class TestDeterminism:
    def test_10_replay_variance_below_threshold(self):
        meta = MetaAnalysis()
        r, s = regime("TRENDING"), signal("MOMENTUM", 0.70, True)
        scores = [meta.analyze(r, s).trust_score for _ in range(10)]
        assert max(scores) - min(scores) < 0.01

    def test_hash_identical_for_same_inputs(self):
        meta = MetaAnalysis()
        r, s = regime("CHOP"), signal("TECHNICAL_BREAKOUT", 0.80, False)
        hashes = [meta.analyze(r, s).deterministic_input_hash for _ in range(5)]
        assert len(set(hashes)) == 1

    def test_hash_differs_for_different_regimes(self):
        meta = MetaAnalysis()
        h1 = meta.compute_hash_input(regime("TRENDING"), signal("MOMENTUM", 0.7, True))
        h2 = meta.compute_hash_input(regime("CHOP"), signal("MOMENTUM", 0.7, True))
        assert h1 != h2

    def test_hash_differs_for_different_signals(self):
        meta = MetaAnalysis()
        h1 = meta.compute_hash_input(regime("TRENDING"), signal("MOMENTUM", 0.7, True))
        h2 = meta.compute_hash_input(regime("TRENDING"), signal("TECHNICAL_BREAKOUT", 0.7, True))
        assert h1 != h2


# ---------------------------------------------------------------------------
# C) Regime Matrix Coverage (all 7 regimes × signal variants)
# ---------------------------------------------------------------------------
# Columns: regime, signal_type, alignment, base, assert_le, assert_ge, reason_substr
_REGIME_MATRIX = [
    # ── CHOP ──────────────────────────────────────────────────────────────
    ("CHOP", "TECHNICAL_BREAKOUT", False, 0.90, 0.50, None, "suppressed"),
    ("CHOP", "MOMENTUM",           False, 0.80, None, None, "dampened"),
    ("CHOP", "MOMENTUM",           True,  0.80, None, None, "dampened"),
    ("CHOP", "OTHER",              False, 0.70, None, None, "NO_ADJUSTMENT"),
    # ── TRANSITION ────────────────────────────────────────────────────────
    ("TRANSITION", "TECHNICAL_BREAKOUT", False, 0.90, 0.50, None, "suppressed"),
    ("TRANSITION", "MOMENTUM",           False, 0.80, None, None, "dampened"),
    ("TRANSITION", "MOMENTUM",           True,  0.80, None, None, "dampened"),
    ("TRANSITION", "OTHER",              False, 0.70, None, None, "NO_ADJUSTMENT"),
    # ── TRENDING ──────────────────────────────────────────────────────────
    ("TRENDING", "MOMENTUM",           True,  0.40, None, 0.60, "boosted"),
    ("TRENDING", "MOMENTUM",           False, 0.40, None, None, "NO_ADJUSTMENT"),
    ("TRENDING", "TECHNICAL_BREAKOUT", False, 0.30, None, 0.55, "supported"),
    ("TRENDING", "TECHNICAL_BREAKOUT", False, 0.80, None, None, "supported"),
    ("TRENDING", "OTHER",              False, 0.60, None, None, "NO_ADJUSTMENT"),
    # ── STRESS ────────────────────────────────────────────────────────────
    ("STRESS", "TECHNICAL_BREAKOUT", False, 0.80, None, None, "dampened"),
    ("STRESS", "MOMENTUM",           False, 0.80, None, None, "dampened"),
    ("STRESS", "MOMENTUM",           True,  0.80, None, None, "dampened"),
    ("STRESS", "OTHER",              False, 0.80, None, None, "dampened"),
    # ── VOLATILE ──────────────────────────────────────────────────────────
    ("VOLATILE", "TECHNICAL_BREAKOUT", False, 0.80, 0.45, None, "capped"),
    ("VOLATILE", "MOMENTUM",           True,  0.70, None, None, "NO_ADJUSTMENT"),
    ("VOLATILE", "MOMENTUM",           False, 0.70, None, None, "NO_ADJUSTMENT"),
    ("VOLATILE", "OTHER",              False, 0.70, None, None, "NO_ADJUSTMENT"),
    # ── ACCUMULATION ──────────────────────────────────────────────────────
    ("ACCUMULATION", "MOMENTUM",           True,  0.30, None, 0.55, "boosted"),
    ("ACCUMULATION", "MOMENTUM",           False, 0.30, None, 0.55, "boosted"),
    ("ACCUMULATION", "TECHNICAL_BREAKOUT", False, 0.70, None, None, "NO_ADJUSTMENT"),
    ("ACCUMULATION", "OTHER",              False, 0.60, None, None, "NO_ADJUSTMENT"),
    # ── DISTRIBUTION ──────────────────────────────────────────────────────
    ("DISTRIBUTION", "MOMENTUM",           False, 0.80, 0.50, None, "suppressed"),
    ("DISTRIBUTION", "MOMENTUM",           True,  0.80, 0.50, None, "suppressed"),
    ("DISTRIBUTION", "TECHNICAL_BREAKOUT", False, 0.70, None, None, "NO_ADJUSTMENT"),
    ("DISTRIBUTION", "OTHER",              False, 0.60, None, None, "NO_ADJUSTMENT"),
]


@pytest.mark.parametrize(
    "regime_type,sig_type,alignment,base,assert_le,assert_ge,reason_substr",
    _REGIME_MATRIX,
)
def test_regime_matrix(regime_type, sig_type, alignment, base, assert_le, assert_ge, reason_substr):
    result = MetaAnalysis().analyze(
        RegimeState(regime=regime_type, volatility=0.3),
        SignalInput(signal_type=sig_type, base_confidence=base, factor_alignment=alignment),
    )
    assert result.status == "OK"
    assert 0.0 <= result.trust_score <= 1.0
    if assert_le is not None:
        assert result.trust_score <= assert_le, (
            f"{regime_type}/{sig_type}: expected ≤ {assert_le}, got {result.trust_score}"
        )
    if assert_ge is not None:
        assert result.trust_score >= assert_ge, (
            f"{regime_type}/{sig_type}: expected ≥ {assert_ge}, got {result.trust_score}"
        )
    assert reason_substr.lower() in result.adjustment_reason.lower(), (
        f"{regime_type}/{sig_type}: expected '{reason_substr}' in '{result.adjustment_reason}'"
    )


# ---------------------------------------------------------------------------
# D) Fail-Safe Path (Invariant 5)
# ---------------------------------------------------------------------------
class TestFailSafe:
    def test_none_signal_returns_insufficient_context(self):
        result = MetaAnalysis().analyze(regime("TRENDING"), signal=None)
        assert result.trust_score == 0.0
        assert result.status == "INSUFFICIENT_CONTEXT"

    def test_none_regime_returns_invalid_regime(self):
        result = MetaAnalysis().analyze(regime=None, signal=signal())
        assert result.trust_score == 0.0
        assert result.status == "INVALID_REGIME"

    def test_invalid_regime_string_returns_invalid_regime(self):
        result = MetaAnalysis().analyze(
            RegimeState(regime="FAKE_REGIME", volatility=0.0),  # type: ignore[arg-type]
            signal(),
        )
        assert result.trust_score == 0.0
        assert result.status == "INVALID_REGIME"

    def test_both_none_returns_invalid_regime(self):
        result = MetaAnalysis().analyze(regime=None, signal=None)
        assert result.trust_score == 0.0
        assert result.status == "INVALID_REGIME"

    def test_invalid_base_confidence_returns_insufficient_context(self):
        bad_sig = SignalInput(
            signal_type="MOMENTUM",
            base_confidence="not_a_number",  # type: ignore[arg-type]
            factor_alignment=True,
        )
        result = MetaAnalysis().analyze(regime("TRENDING"), bad_sig)
        assert result.trust_score == 0.0
        assert result.status == "INSUFFICIENT_CONTEXT"

    def test_no_unhandled_exception_on_any_bad_input(self):
        meta = MetaAnalysis()
        for r, s in [(None, None), (regime("TRENDING"), None), (None, signal())]:
            result = meta.analyze(r, s)
            assert result.trust_score == 0.0

    def test_latency_violation_fail_safe_structure(self):
        """Verify LATENCY_VIOLATION path returns correct structure (exercises _fail_safe directly)."""
        result = MetaAnalysis()._fail_safe(
            "LATENCY_VIOLATION", time.perf_counter(), "TRENDING", "MOMENTUM", 0.7
        )
        assert result.status == "LATENCY_VIOLATION"
        assert result.trust_score == 0.0
        log = json.loads(result.structured_log)
        assert log["adjustment_reason"] == "FAIL_SAFE"


# ---------------------------------------------------------------------------
# E) Latency Sanity
# ---------------------------------------------------------------------------
class TestLatency:
    def test_latency_in_valid_range(self):
        result = MetaAnalysis().analyze(regime("TRENDING"), signal("MOMENTUM"))
        assert result.computation_latency_ms >= 0
        assert result.computation_latency_ms < 1000

    def test_latency_present_in_structured_log(self):
        result = MetaAnalysis().analyze(regime("STRESS"), signal("OTHER", 0.5, False))
        log = json.loads(result.structured_log)
        assert "latency_ms" in log
        assert log["latency_ms"] >= 0

    def test_latency_present_on_fail_safe_path(self):
        result = MetaAnalysis().analyze(regime=None, signal=signal())
        assert result.computation_latency_ms >= 0
        log = json.loads(result.structured_log)
        assert "latency_ms" in log


# ---------------------------------------------------------------------------
# F) Explainability Completeness (Invariant 4)
# ---------------------------------------------------------------------------
class TestExplainability:
    _REQUIRED_RESULT_FIELDS = {
        "trust_score",
        "status",
        "regime_context",
        "adjustment_reason",
        "computation_latency_ms",
        "signal_type",
        "base_confidence",
        "deterministic_input_hash",
        "structured_log",
    }
    _REQUIRED_LOG_KEYS = {
        "signal_type",
        "regime",
        "base_confidence",
        "adjustment_reason",
        "final_trust",
        "latency_ms",
        "input_hash",
    }

    def test_all_trust_result_fields_present(self):
        result = MetaAnalysis().analyze(regime("TRENDING"), signal("MOMENTUM", 0.70, True))
        for f in self._REQUIRED_RESULT_FIELDS:
            assert hasattr(result, f), f"TrustResult missing field: {f}"

    def test_structured_log_is_valid_json(self):
        result = MetaAnalysis().analyze(regime("CHOP"), signal("TECHNICAL_BREAKOUT", 0.80))
        log = json.loads(result.structured_log)  # raises on invalid JSON
        assert isinstance(log, dict)

    def test_structured_log_has_all_required_keys(self):
        result = MetaAnalysis().analyze(regime("ACCUMULATION"), signal("MOMENTUM", 0.50, True))
        log = json.loads(result.structured_log)
        for k in self._REQUIRED_LOG_KEYS:
            assert k in log, f"structured_log missing key: {k}"

    def test_structured_log_values_match_trust_result(self):
        r = regime("TRENDING")
        s = signal("MOMENTUM", 0.70, True)
        result = MetaAnalysis().analyze(r, s)
        log = json.loads(result.structured_log)
        assert log["signal_type"] == result.signal_type
        assert log["regime"] == result.regime_context
        assert log["base_confidence"] == result.base_confidence
        assert log["adjustment_reason"] == result.adjustment_reason
        assert log["final_trust"] == result.trust_score
        assert log["input_hash"] == result.deterministic_input_hash

    def test_fail_safe_result_has_all_fields(self):
        result = MetaAnalysis().analyze(regime=None, signal=signal())
        for f in self._REQUIRED_RESULT_FIELDS:
            assert hasattr(result, f), f"Fail-safe TrustResult missing field: {f}"
        log = json.loads(result.structured_log)
        for k in self._REQUIRED_LOG_KEYS:
            assert k in log, f"Fail-safe structured_log missing key: {k}"

    def test_signal_type_in_result_matches_input(self):
        s = signal("TECHNICAL_BREAKOUT", 0.60, False)
        result = MetaAnalysis().analyze(regime("VOLATILE"), s)
        assert result.signal_type == "TECHNICAL_BREAKOUT"

    def test_base_confidence_in_result_matches_clamped_input(self):
        # base_confidence is stored after _clamp(), so 2.0 → 1.0
        result = MetaAnalysis().analyze(regime("TRENDING"), signal("MOMENTUM", 2.0, True))
        assert result.base_confidence == 1.0


# ---------------------------------------------------------------------------
# Trust Bounds — Exhaustive (Invariant 2)
# ---------------------------------------------------------------------------
class TestTrustBounds:
    def test_trust_always_in_range_across_full_matrix(self):
        meta = MetaAnalysis()
        for r in ("TRENDING", "CHOP", "TRANSITION", "STRESS", "VOLATILE", "ACCUMULATION", "DISTRIBUTION"):
            for s_type in ("TECHNICAL_BREAKOUT", "MOMENTUM", "OTHER"):
                for alignment in (True, False):
                    for base in (0.0, 0.25, 0.50, 0.75, 1.0):
                        result = meta.analyze(
                            RegimeState(regime=r, volatility=0.3),
                            SignalInput(signal_type=s_type, base_confidence=base, factor_alignment=alignment),
                        )
                        assert 0.0 <= result.trust_score <= 1.0, (
                            f"Invariant 2 violated: {r}/{s_type}/{alignment}/{base} → {result.trust_score}"
                        )


# ---------------------------------------------------------------------------
# Health Status + compute_hash_input
# ---------------------------------------------------------------------------
class TestHealthAndHash:
    def test_get_health_status(self):
        health = MetaAnalysis().get_health_status()
        assert health["deterministic"] is True
        assert health["regime_required"] is True
        assert health["trust_bounds_enforced"] is True

    def test_compute_hash_input_returns_16_char_hex(self):
        h = MetaAnalysis().compute_hash_input(regime("TRENDING"), signal("MOMENTUM", 0.7, True))
        assert isinstance(h, str)
        assert len(h) == 16
        int(h, 16)  # must be valid hexadecimal

    def test_compute_hash_input_is_deterministic(self):
        meta = MetaAnalysis()
        r, s = regime("STRESS"), signal("TECHNICAL_BREAKOUT", 0.55, False)
        assert meta.compute_hash_input(r, s) == meta.compute_hash_input(r, s)
