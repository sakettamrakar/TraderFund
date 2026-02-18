"""
Phase A+C Feedback Integration Tests
=====================================
Tests covering:
  Part A — PerformanceFeedbackEngine → L6 ConvergenceEngine modifier
  Part C — StabilityAdapter → L3 MetaAnalysis stability dampening

Coverage:
  1.  Underperforming strategy → modifier < 0
  2.  Outperforming strategy   → modifier > 0
  3.  Stability degradation    → effective_trust < raw_trust
  4.  stability_score=1.0      → effective_trust == raw_trust
  5.  stability_score=0.5      → effective_trust == raw_trust * 0.5
  6.  stability_score=0.0      → effective_trust == 0.0
  7.  Deterministic replay (10 runs, variance < 0.01)
  8.  Modifier strictly clamped to [-0.20, +0.20]
  9.  final_score always in [0.0, 1.0]
  10. StabilityAdapter returns 1.0 when file is missing
  11. StabilityAdapter honours override path for testing
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from src.feedback.performance_feedback import PerformanceContext, PerformanceFeedbackEngine
from src.feedback.stability_adapter import StabilityAdapter
from src.layers.convergence_engine import ConvergenceEngine
from src.layers.meta_analysis import MetaAnalysis
from src.models.convergence_models import LensSignal
from src.models.meta_models import RegimeState, SignalInput

# ── Shared helpers ────────────────────────────────────────────────────────────


def _regime(r: str = "TRENDING") -> RegimeState:
    return RegimeState(regime=r, volatility=0.3)


def _signal(sig: str = "MOMENTUM", conf: float = 0.70, align: bool = True) -> SignalInput:
    return SignalInput(signal_type=sig, base_confidence=conf, factor_alignment=align)


def _lens(direction: str = "LONG", conf: float = 0.70, compat: float = 0.80,
          name: str = "TECHNICAL") -> LensSignal:
    return LensSignal(symbol="SPY", direction=direction, confidence=conf,
                      regime_compatibility=compat, lens_name=name)


def _three_lenses(conf: float = 0.70) -> list[LensSignal]:
    return [_lens("LONG", conf, 0.80, n) for n in ("TECHNICAL", "MOMENTUM", "SENTIMENT")]


def _stability_file(values: dict) -> str:
    """Write a temporary stability_state.json and return its path."""
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(values, f)
    return path


def _meta_with_stability(score: float) -> MetaAnalysis:
    """Build a MetaAnalysis caller that always passes a given stability score."""
    return MetaAnalysis()


def _analyze_with_stability(stability: float, regime: RegimeState,
                             signal: SignalInput):
    """Convenience: run MetaAnalysis.analyze with an explicit stability score."""
    return MetaAnalysis().analyze(regime, signal, stability_score=stability)


# ╔══════════════════════════════════════════════════════════════════════════════
# §1  PerformanceFeedbackEngine — unit tests
# ╚══════════════════════════════════════════════════════════════════════════════

class TestPerformanceFeedbackEngine:

    def _ctx(self, realized_hit=0.60, expected_hit=0.60,
             realized_ret=0.015, expected_ret=0.015) -> PerformanceContext:
        return PerformanceContext(
            strategy_id="STRAT_A",
            realized_hit_rate=realized_hit,
            expected_hit_rate=expected_hit,
            realized_avg_return=realized_ret,
            expected_avg_return=expected_ret,
        )

    # A1 — underperforming
    def test_underperforming_modifier_is_negative(self):
        ctx = self._ctx(realized_hit=0.40, expected_hit=0.60,
                        realized_ret=0.01, expected_ret=0.02)
        mod = PerformanceFeedbackEngine().compute_modifier(ctx)
        assert mod < 0.0

    # A2 — outperforming
    def test_outperforming_modifier_is_positive(self):
        ctx = self._ctx(realized_hit=0.80, expected_hit=0.60,
                        realized_ret=0.03, expected_ret=0.02)
        mod = PerformanceFeedbackEngine().compute_modifier(ctx)
        assert mod > 0.0

    # A3 — at par
    def test_equal_performance_modifier_is_zero(self):
        ctx = self._ctx()
        mod = PerformanceFeedbackEngine().compute_modifier(ctx)
        assert mod == pytest.approx(0.0, abs=1e-9)

    # Invariant 5 — upper clamp
    def test_modifier_clamped_at_plus_0_20(self):
        ctx = self._ctx(realized_hit=1.0, expected_hit=0.0,
                        realized_ret=1.0, expected_ret=0.01)
        mod = PerformanceFeedbackEngine().compute_modifier(ctx)
        assert mod == pytest.approx(0.20, abs=1e-9)

    # Invariant 5 — lower clamp
    def test_modifier_clamped_at_minus_0_20(self):
        ctx = self._ctx(realized_hit=0.0, expected_hit=1.0,
                        realized_ret=-1.0, expected_ret=0.01)
        mod = PerformanceFeedbackEngine().compute_modifier(ctx)
        assert mod == pytest.approx(-0.20, abs=1e-9)

    def test_modifier_always_in_bounds(self):
        """Exhaustive sweep — modifier never leaves [-0.20, +0.20]."""
        engine = PerformanceFeedbackEngine()
        for rh in (0.0, 0.25, 0.50, 0.75, 1.0):
            for eh in (0.0, 0.25, 0.50, 0.75, 1.0):
                for rr in (-0.05, 0.0, 0.02, 0.05):
                    for er in (0.0, 0.01, 0.02, 0.05):
                        ctx = PerformanceContext("X", rh, eh, rr, er)
                        m = engine.compute_modifier(ctx)
                        assert -0.20 <= m <= 0.20, f"Out of bounds: {m}"

    def test_modifier_is_deterministic(self):
        ctx = self._ctx(realized_hit=0.55, expected_hit=0.60,
                        realized_ret=0.012, expected_ret=0.015)
        engine = PerformanceFeedbackEngine()
        values = [engine.compute_modifier(ctx) for _ in range(10)]
        assert len(set(values)) == 1

    def test_describe_matches_compute_modifier(self):
        ctx = self._ctx(realized_hit=0.70, expected_hit=0.60,
                        realized_ret=0.025, expected_ret=0.015)
        engine = PerformanceFeedbackEngine()
        mod = engine.compute_modifier(ctx)
        desc = engine.describe(ctx)
        assert desc["modifier_clamped"] == pytest.approx(mod, abs=1e-9)
        assert desc["strategy_id"] == "STRAT_A"


# ╔══════════════════════════════════════════════════════════════════════════════
# §2  StabilityAdapter — unit tests
# ╚══════════════════════════════════════════════════════════════════════════════

class TestStabilityAdapter:

    def test_missing_file_returns_1_0(self, tmp_path):
        adapter = StabilityAdapter(state_path=str(tmp_path / "nonexistent.json"))
        assert adapter.get_stability("MetaAnalysis") == pytest.approx(1.0)

    def test_known_component_returns_correct_score(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text(json.dumps({"MetaAnalysis": 0.75}))
        adapter = StabilityAdapter(state_path=str(path))
        assert adapter.get_stability("MetaAnalysis") == pytest.approx(0.75)

    def test_unknown_component_defaults_to_1_0(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text(json.dumps({"ConvergenceEngine": 0.80}))
        adapter = StabilityAdapter(state_path=str(path))
        assert adapter.get_stability("MetaAnalysis") == pytest.approx(1.0)

    def test_malformed_json_returns_1_0(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text("{not valid json}")
        adapter = StabilityAdapter(state_path=str(path))
        assert adapter.get_stability("MetaAnalysis") == pytest.approx(1.0)

    def test_value_above_1_clamped(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text(json.dumps({"MetaAnalysis": 2.5}))
        adapter = StabilityAdapter(state_path=str(path))
        assert adapter.get_stability("MetaAnalysis") == pytest.approx(1.0)

    def test_value_below_0_clamped(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text(json.dumps({"MetaAnalysis": -0.5}))
        adapter = StabilityAdapter(state_path=str(path))
        assert adapter.get_stability("MetaAnalysis") == pytest.approx(0.0)

    def test_never_raises_on_any_bad_input(self, tmp_path):
        for content in ("", "null", "[]", "123", '{"a":null}'):
            path = tmp_path / "bad.json"
            path.write_text(content)
            adapter = StabilityAdapter(state_path=str(path))
            result = adapter.get_stability("MetaAnalysis")
            assert result == pytest.approx(1.0)


# ╔══════════════════════════════════════════════════════════════════════════════
# §3  MetaAnalysis — stability dampening invariants
# ╚══════════════════════════════════════════════════════════════════════════════

class TestMetaAnalysisStabilityInvariants:
    """Five required invariants from the spec."""

    # Invariant 1
    def test_stability_1_0_effective_trust_equals_raw_trust(self):
        result = _analyze_with_stability(1.0, _regime("TRENDING"), _signal("MOMENTUM", 0.70, True))
        assert result.effective_trust == pytest.approx(result.raw_trust, abs=1e-9)
        assert result.trust_score == pytest.approx(result.raw_trust, abs=1e-9)

    # Invariant 2
    def test_stability_0_5_effective_trust_is_half(self):
        result = _analyze_with_stability(0.5, _regime("TRENDING"), _signal("MOMENTUM", 0.70, True))
        assert result.effective_trust == pytest.approx(result.raw_trust * 0.5, abs=1e-9)
        assert result.stability_score == pytest.approx(0.5, abs=1e-9)

    # Invariant 3
    def test_stability_0_effective_trust_is_zero(self):
        result = _analyze_with_stability(0.0, _regime("TRENDING"), _signal("MOMENTUM", 0.80, True))
        assert result.effective_trust == pytest.approx(0.0, abs=1e-9)
        assert result.trust_score == pytest.approx(0.0, abs=1e-9)

    # Invariant 4 — deterministic replay
    def test_deterministic_replay_variance_below_0_01(self):
        r, s = _regime("TRENDING"), _signal("MOMENTUM", 0.70, True)
        scores = [_analyze_with_stability(0.85, r, s).effective_trust for _ in range(10)]
        variance = sum((v - scores[0]) ** 2 for v in scores) / len(scores)
        assert variance < 0.01

    def test_raw_trust_unchanged_by_stability(self):
        """raw_trust must be the regime-adjusted score before dampening."""
        r, s = _regime("TRENDING"), _signal("MOMENTUM", 0.70, True)
        r1 = _analyze_with_stability(1.0, r, s)
        r2 = _analyze_with_stability(0.5, r, s)
        assert r1.raw_trust == pytest.approx(r2.raw_trust, abs=1e-9)

    def test_stability_score_reflected_in_result(self):
        result = _analyze_with_stability(0.72, _regime("CHOP"), _signal("MOMENTUM", 0.60))
        assert result.stability_score == pytest.approx(0.72, abs=1e-9)

    def test_effective_trust_bounded(self):
        """effective_trust must always be in [0, 1] for any stability value."""
        for stability in (0.0, 0.25, 0.5, 0.75, 1.0):
            result = _analyze_with_stability(stability, _regime("TRENDING"),
                                             _signal("MOMENTUM", 0.90, True))
            assert 0.0 <= result.effective_trust <= 1.0

    def test_trust_score_equals_effective_trust(self):
        """trust_score exposed to downstream should equal effective_trust."""
        result = _analyze_with_stability(0.6, _regime("STRESS"), _signal("MOMENTUM", 0.70))
        assert result.trust_score == pytest.approx(result.effective_trust, abs=1e-9)

    def test_structured_log_contains_stability_fields(self):
        """Structured log must contain raw_trust, stability_score, effective_trust."""
        result = _analyze_with_stability(0.8, _regime("TRENDING"), _signal("MOMENTUM", 0.70, True))
        log = json.loads(result.structured_log)
        assert "raw_trust" in log
        assert "stability_score" in log
        assert "effective_trust" in log
        assert "final_trust" in log
        assert log["final_trust"] == pytest.approx(result.trust_score, abs=1e-9)


# ╔══════════════════════════════════════════════════════════════════════════════
# §4  ConvergenceEngine — performance modifier integration
# ╚══════════════════════════════════════════════════════════════════════════════

class TestConvergenceEnginePerformanceModifier:

    def _ctx(self, realized_hit: float, expected_hit: float,
             realized_ret: float = 0.015, expected_ret: float = 0.015) -> PerformanceContext:
        return PerformanceContext(
            strategy_id="STRAT_TEST",
            realized_hit_rate=realized_hit,
            expected_hit_rate=expected_hit,
            realized_avg_return=realized_ret,
            expected_avg_return=expected_ret,
        )

    def test_no_context_modifier_is_zero(self):
        engine = ConvergenceEngine()
        result = engine.compute(_three_lenses(), _regime(), 0.80)
        assert result.performance_modifier == pytest.approx(0.0, abs=1e-9)

    def test_no_context_final_equals_base(self):
        engine = ConvergenceEngine()
        result = engine.compute(_three_lenses(0.70), _regime(), 0.80)
        assert result.final_score == pytest.approx(result.base_score, abs=1e-9)

    # Invariant 5 — modifier cap
    def test_convergence_modifier_cannot_exceed_plus_0_20(self):
        ctx = self._ctx(1.0, 0.0, 1.0, 0.01)
        engine = ConvergenceEngine()
        result = engine.compute(_three_lenses(), _regime(), 0.80, ctx)
        assert result.performance_modifier <= 0.20 + 1e-9

    def test_convergence_modifier_cannot_exceed_minus_0_20(self):
        ctx = self._ctx(0.0, 1.0, -1.0, 0.01)
        engine = ConvergenceEngine()
        result = engine.compute(_three_lenses(), _regime(), 0.80, ctx)
        assert result.performance_modifier >= -0.20 - 1e-9

    # A1 — underperforming
    def test_underperforming_lowers_final_score(self):
        ctx = self._ctx(realized_hit=0.30, expected_hit=0.60,
                        realized_ret=0.005, expected_ret=0.02)
        engine = ConvergenceEngine()
        result_no_ctx = engine.compute(_three_lenses(0.70), _regime(), 0.80)
        result_with_ctx = engine.compute(_three_lenses(0.70), _regime(), 0.80, ctx)
        assert result_with_ctx.final_score < result_no_ctx.final_score
        assert result_with_ctx.performance_modifier < 0.0

    # A2 — outperforming
    def test_outperforming_raises_final_score(self):
        ctx = self._ctx(realized_hit=0.85, expected_hit=0.60,
                        realized_ret=0.03, expected_ret=0.015)
        engine = ConvergenceEngine()
        result_no_ctx = engine.compute(_three_lenses(0.70), _regime(), 0.80)
        result_with_ctx = engine.compute(_three_lenses(0.70), _regime(), 0.80, ctx)
        assert result_with_ctx.final_score > result_no_ctx.final_score
        assert result_with_ctx.performance_modifier > 0.0

    def test_final_score_always_bounded(self):
        """final_score ∈ [0, 1] regardless of modifier direction."""
        engine = ConvergenceEngine()
        for rh, eh in ((0.0, 1.0), (1.0, 0.0), (0.5, 0.5)):
            ctx = PerformanceContext("X", rh, eh, 0.01, 0.01)
            result = engine.compute(_three_lenses(0.95), _regime(), 1.0, ctx)
            assert 0.0 <= result.final_score <= 1.0

    def test_no_negative_final_score(self):
        ctx = self._ctx(0.0, 1.0, -0.10, 0.01)
        engine = ConvergenceEngine()
        result = engine.compute(_three_lenses(0.70), _regime(), 0.80, ctx)
        assert result.final_score >= 0.0

    # Invariant 4 — determinism with performance context
    def test_deterministic_replay_with_performance_context(self):
        ctx = self._ctx(0.55, 0.60, 0.012, 0.015)
        engine = ConvergenceEngine()
        scores = [
            engine.compute(_three_lenses(0.70), _regime(), 0.80, ctx).final_score
            for _ in range(10)
        ]
        variance = sum((s - scores[0]) ** 2 for s in scores) / len(scores)
        assert variance < 0.01

    def test_base_score_and_final_score_logged_in_result(self):
        ctx = self._ctx(0.80, 0.60, 0.025, 0.015)
        engine = ConvergenceEngine()
        result = engine.compute(_three_lenses(0.70), _regime(), 0.80, ctx)
        assert hasattr(result, "base_score")
        assert hasattr(result, "performance_modifier")
        assert hasattr(result, "final_score")
        assert result.base_score >= 0.0
        assert result.final_score >= 0.0

    def test_fail_safe_has_zero_modifier_and_base(self):
        engine = ConvergenceEngine()
        ctx = self._ctx(0.80, 0.60)
        result = engine.compute([], _regime(), 0.80, ctx)
        assert result.performance_modifier == pytest.approx(0.0, abs=1e-9)
        assert result.base_score == pytest.approx(0.0, abs=1e-9)
        assert result.final_score == pytest.approx(0.0, abs=1e-9)


# ╔══════════════════════════════════════════════════════════════════════════════
# §5  Full acceptance scenarios
# ╚══════════════════════════════════════════════════════════════════════════════

class TestAcceptanceScenarios:
    """Mirrors the acceptance test scenarios from the spec."""

    def test_scenario_A1_underperforming_modifier_negative(self):
        """Underperforming strategy → modifier < 0 → final_score < base_score."""
        ctx = PerformanceContext(
            strategy_id="UNDERPERFORMER",
            realized_hit_rate=0.35,
            expected_hit_rate=0.60,
            realized_avg_return=0.005,
            expected_avg_return=0.020,
        )
        engine = ConvergenceEngine()
        result = engine.compute(_three_lenses(0.70), _regime("TRENDING"), 0.80, ctx)
        assert result.performance_modifier < 0.0
        assert result.final_score < result.base_score
        assert 0.0 <= result.final_score <= 1.0

    def test_scenario_A2_outperforming_modifier_positive(self):
        """Outperforming strategy → modifier > 0 → final_score > base_score."""
        ctx = PerformanceContext(
            strategy_id="OUTPERFORMER",
            realized_hit_rate=0.85,
            expected_hit_rate=0.60,
            realized_avg_return=0.035,
            expected_avg_return=0.015,
        )
        engine = ConvergenceEngine()
        result = engine.compute(_three_lenses(0.70), _regime("TRENDING"), 0.80, ctx)
        assert result.performance_modifier > 0.0
        assert result.final_score > result.base_score
        assert 0.0 <= result.final_score <= 1.0

    def test_scenario_C1_stability_degradation_lowers_trust(self):
        """Stability < 1.0 → effective_trust < raw_trust."""
        result = _analyze_with_stability(0.5, _regime("TRENDING"), _signal("MOMENTUM", 0.80, True))
        assert result.effective_trust < result.raw_trust
        assert result.effective_trust == pytest.approx(result.raw_trust * 0.5, abs=1e-9)

    def test_scenario_C2_perfect_stability_trust_unchanged(self):
        """stability=1.0 → effective_trust == raw_trust."""
        result = _analyze_with_stability(1.0, _regime("TRENDING"), _signal("MOMENTUM", 0.70, True))
        assert result.effective_trust == pytest.approx(result.raw_trust, abs=1e-9)

    def test_no_silent_failures_convergence(self):
        """ConvergenceEngine must never raise; always return a valid result."""
        engine = ConvergenceEngine()
        ctx = PerformanceContext("X", 0.0, 1.0, -0.05, 0.01)
        for call in [
            lambda: engine.compute(None, None, None),
            lambda: engine.compute([], _regime(), 0.0),
            lambda: engine.compute(_three_lenses(), None, 0.80),
            lambda: engine.compute(_three_lenses(), _regime(), 0.80, ctx),
        ]:
            result = call()
            assert result is not None
            assert 0.0 <= result.final_score <= 1.0

    def test_no_silent_failures_meta_analysis(self):
        """MetaAnalysis must never raise; always return a valid TrustResult."""
        meta = MetaAnalysis()
        for stability in (0.0, 0.5, 1.0):
            for r, s in [
                (_regime(), None),
                (None, _signal()),
                (_regime("TRENDING"), _signal("MOMENTUM", 0.70, True)),
            ]:
                result = meta.analyze(r, s, stability_score=stability)
                assert result is not None
                assert 0.0 <= result.trust_score <= 1.0
                assert 0.0 <= result.effective_trust <= 1.0
