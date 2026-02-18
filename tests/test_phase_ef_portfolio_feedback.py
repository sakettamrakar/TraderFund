"""
Tests for Phase E — Portfolio Feedback Engine
==============================================
Covers:
  1. Exposure pressure thresholds (ratio > 0.40 → -0.15, ratio > 0.55 → -0.30)
  2. Drawdown guard (drawdown > 0.08 → -0.10, drawdown > 0.15 → -0.20)
  3. Strategy health dampener (health < 0.50 → -0.10)
  4. Bias always in [-0.40, 0.0], never positive
  5. Deterministic replay
  6. Portfolio concentration scenario
  7. describe() breakdown consistency
"""
from __future__ import annotations

import pytest

from src.feedback.portfolio_feedback import PortfolioContext, PortfolioFeedbackEngine


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ctx(
    exposures: dict[str, float] | None = None,
    health: dict[str, float] | None = None,
    drawdown: float = 0.0,
    regime: str = "TRENDING",
) -> PortfolioContext:
    exposures = exposures or {"alpha": 500.0, "beta": 500.0}
    health = health or {"alpha": 0.80, "beta": 0.80}
    return PortfolioContext(
        strategy_exposures=exposures,
        strategy_health_scores=health,
        current_drawdown=drawdown,
        regime=regime,
    )


ENGINE = PortfolioFeedbackEngine()


# ── 1  Exposure Pressure ─────────────────────────────────────────────────────

class TestExposurePressure:

    def test_equal_split_no_penalty(self):
        """Two strategies at 50/50 → neither exceeds 0.55 or 0.40? 50% > 40% → -0.15."""
        ctx = _ctx(exposures={"a": 500, "b": 500})
        biases = ENGINE.compute_bias(ctx)
        # 500/1000 = 0.50 > 0.40 → -0.15 each
        assert biases["a"] == pytest.approx(-0.15)
        assert biases["b"] == pytest.approx(-0.15)

    def test_below_40_no_exposure_penalty(self):
        """Strategy at 30% of total → no exposure penalty."""
        ctx = _ctx(exposures={"a": 300, "b": 400, "c": 300})
        biases = ENGINE.compute_bias(ctx)
        # a: 300/1000 = 0.30 → 0.0; b: 0.40 → 0.0 (not > 0.40); c: 0.30 → 0.0
        assert biases["a"] == 0.0
        assert biases["b"] == 0.0
        assert biases["c"] == 0.0

    def test_ratio_exactly_0_40_no_penalty(self):
        """Ratio == 0.40 exactly → no penalty (threshold is > 0.40, not >=)."""
        ctx = _ctx(exposures={"a": 400, "b": 600})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == 0.0  # exactly 0.40 → not > 0.40

    def test_ratio_above_0_40_penalty(self):
        """Ratio = 0.45 → -0.15."""
        ctx = _ctx(exposures={"a": 450, "b": 550})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == pytest.approx(-0.15)

    def test_ratio_exactly_0_55_no_severe_penalty(self):
        """Ratio == 0.55 exactly → still at -0.15 tier (threshold is > 0.55, not >=)."""
        ctx = _ctx(exposures={"a": 550, "b": 450})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == pytest.approx(-0.15)

    def test_ratio_above_0_55_severe_penalty(self):
        """Ratio = 0.60 → -0.30."""
        ctx = _ctx(exposures={"a": 600, "b": 400})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == pytest.approx(-0.30)

    def test_dominant_strategy_heavy_penalty(self):
        """Single strategy at 80% of exposure → -0.30."""
        ctx = _ctx(exposures={"a": 800, "b": 200})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == pytest.approx(-0.30)  # 0.80 > 0.55
        assert biases["b"] == 0.0                     # 0.20 ≤ 0.40


# ── 2  Drawdown Guard ────────────────────────────────────────────────────────

class TestDrawdownGuard:

    def test_no_drawdown_no_penalty(self):
        ctx = _ctx(drawdown=0.0)
        biases = ENGINE.compute_bias(ctx)
        for v in biases.values():
            # Only exposure-based penalties remain; drawdown contribution = 0
            assert v >= -0.30  # max from exposure only

    def test_drawdown_below_8_percent(self):
        ctx = _ctx(drawdown=0.05, exposures={"a": 300, "b": 700})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == 0.0  # no drawdown, no exposure penalty (0.30 ≤ 0.40)

    def test_drawdown_above_8_percent(self):
        """Drawdown 10% → -0.10 global bias on all strategies."""
        ctx = _ctx(drawdown=0.10, exposures={"a": 300, "b": 300, "c": 400})
        biases = ENGINE.compute_bias(ctx)
        for v in biases.values():
            assert v <= -0.10  # at least -0.10 from drawdown

    def test_drawdown_exactly_8_percent(self):
        """Drawdown == 0.08 → no penalty (threshold is > 0.08)."""
        ctx = _ctx(drawdown=0.08, exposures={"a": 300, "b": 700})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == 0.0

    def test_drawdown_above_15_percent(self):
        """Drawdown 20% → -0.20 global bias."""
        ctx = _ctx(drawdown=0.20, exposures={"a": 300, "b": 300, "c": 400})
        biases = ENGINE.compute_bias(ctx)
        for v in biases.values():
            assert v <= -0.20

    def test_drawdown_exactly_15_percent(self):
        """Drawdown == 0.15 → still at -0.10 tier (> 0.15 for severe)."""
        ctx = _ctx(drawdown=0.15, exposures={"a": 300, "b": 700})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == pytest.approx(-0.10)  # 0.30 ratio → no exposure; drawdown tier-1

    def test_negative_drawdown_treated_as_zero(self):
        ctx = _ctx(drawdown=-0.05, exposures={"a": 300, "b": 700})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == 0.0


# ── 3  Strategy Health Dampener ───────────────────────────────────────────────

class TestHealthDampener:

    def test_healthy_strategy_no_penalty(self):
        ctx = _ctx(health={"alpha": 0.80, "beta": 0.70})
        biases = ENGINE.compute_bias(ctx)
        # No health penalty for health >= 0.50
        # Only exposure penalty from 50/50 split → -0.15 each
        assert biases["alpha"] == pytest.approx(-0.15)
        assert biases["beta"] == pytest.approx(-0.15)

    def test_health_exactly_0_50_no_penalty(self):
        """Health == 0.50 exactly → no penalty (threshold is < 0.50)."""
        ctx = _ctx(health={"alpha": 0.50, "beta": 0.80})
        biases = ENGINE.compute_bias(ctx)
        # Only exposure penalty (-0.15 from 50/50)
        assert biases["alpha"] == pytest.approx(-0.15)

    def test_health_below_0_50_penalty(self):
        """Health = 0.40 → -0.10 additional."""
        ctx = _ctx(health={"alpha": 0.40, "beta": 0.80})
        biases = ENGINE.compute_bias(ctx)
        # alpha: exposure -0.15 + health -0.10 = -0.25
        assert biases["alpha"] == pytest.approx(-0.25)
        # beta: exposure -0.15 only
        assert biases["beta"] == pytest.approx(-0.15)

    def test_missing_health_defaults_to_1(self):
        """Strategy not in health_scores → default 1.0 → no penalty."""
        ctx = PortfolioContext(
            strategy_exposures={"a": 300, "b": 700},
            strategy_health_scores={},  # empty
            current_drawdown=0.0,
            regime="TRENDING",
        )
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == 0.0  # 0.30 ratio → no exposure; no drawdown; health=1.0 → 0


# ── 4  Bias Bounds [-0.40, 0.0] ──────────────────────────────────────────────

class TestBiasBounds:

    def test_bias_never_positive(self):
        """Even with zero drawdown, perfect health, and low exposure."""
        ctx = _ctx(
            exposures={"a": 100, "b": 100, "c": 100, "d": 100, "e": 100},
            health={"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0, "e": 1.0},
            drawdown=0.0,
        )
        biases = ENGINE.compute_bias(ctx)
        for v in biases.values():
            assert v <= 0.0

    def test_bias_floor_minus_0_40(self):
        """Worst case: high exposure + high drawdown + low health → clamped to -0.40."""
        ctx = _ctx(
            exposures={"a": 900, "b": 100},
            health={"a": 0.10, "b": 0.80},
            drawdown=0.25,
        )
        biases = ENGINE.compute_bias(ctx)
        # a: exposure -0.30 (90% > 55%) + drawdown -0.20 (25% > 15%) + health -0.10 = -0.60 → clamped -0.40
        assert biases["a"] == pytest.approx(-0.40)
        assert biases["a"] >= -0.40

    def test_all_components_summed_then_clamped(self):
        """exercise clamping: -0.30 + -0.20 + -0.10 = -0.60 → -0.40."""
        ctx = _ctx(
            exposures={"x": 800, "y": 200},
            health={"x": 0.30, "y": 0.80},
            drawdown=0.20,
        )
        biases = ENGINE.compute_bias(ctx)
        assert biases["x"] == pytest.approx(-0.40)

    def test_single_strategy_portfolio(self):
        """Single strategy → exposure ratio = 1.0 → -0.30 from exposure alone."""
        ctx = _ctx(
            exposures={"only": 1000},
            health={"only": 0.80},
            drawdown=0.0,
        )
        biases = ENGINE.compute_bias(ctx)
        assert biases["only"] == pytest.approx(-0.30)


# ── 5  Deterministic Replay ──────────────────────────────────────────────────

class TestDeterministicReplay:

    def test_ten_identical_runs(self):
        ctx = _ctx(
            exposures={"a": 600, "b": 400},
            health={"a": 0.45, "b": 0.90},
            drawdown=0.12,
        )
        results = [ENGINE.compute_bias(ctx) for _ in range(10)]
        first = results[0]
        for r in results[1:]:
            assert r == first

    def test_deterministic_with_many_strategies(self):
        ctx = _ctx(
            exposures={"s1": 200, "s2": 300, "s3": 400, "s4": 100},
            health={"s1": 0.90, "s2": 0.45, "s3": 0.30, "s4": 0.80},
            drawdown=0.09,
        )
        results = [ENGINE.compute_bias(ctx) for _ in range(10)]
        for r in results[1:]:
            assert r == results[0]


# ── 6  Portfolio Concentration Scenario ───────────────────────────────────────

class TestConcentrationScenario:

    def test_highly_concentrated_portfolio(self):
        """One dominant strategy should get heaviest bias."""
        ctx = _ctx(
            exposures={"dom": 7000, "small1": 1000, "small2": 1000, "small3": 1000},
            health={"dom": 0.40, "small1": 0.80, "small2": 0.80, "small3": 0.80},
            drawdown=0.18,
        )
        biases = ENGINE.compute_bias(ctx)
        # dom: 70% > 55% → -0.30 exposure; 18% > 15% → -0.20 drawdown; health < 0.50 → -0.10 → -0.60 → -0.40
        assert biases["dom"] == pytest.approx(-0.40)
        # small1: 10% ≤ 40% → 0 exposure; -0.20 drawdown; health OK → -0.20
        assert biases["small1"] == pytest.approx(-0.20)

    def test_equal_distribution_low_stress(self):
        """5 equal strategies, no drawdown, healthy → minimal bias."""
        ctx = _ctx(
            exposures={"s1": 200, "s2": 200, "s3": 200, "s4": 200, "s5": 200},
            health={"s1": 0.90, "s2": 0.85, "s3": 0.92, "s4": 0.80, "s5": 0.88},
            drawdown=0.0,
        )
        biases = ENGINE.compute_bias(ctx)
        # 20% each → no exposure penalty; no drawdown; all healthy → 0.0 each
        for v in biases.values():
            assert v == 0.0


# ── 7  describe() Consistency ─────────────────────────────────────────────────

class TestDescribeConsistency:

    def test_describe_keys_present(self):
        ctx = _ctx()
        desc = ENGINE.describe(ctx)
        for strat, detail in desc.items():
            assert "exposure_ratio" in detail
            assert "exposure_bias" in detail
            assert "drawdown_bias" in detail
            assert "health_score" in detail
            assert "health_bias" in detail
            assert "raw_bias" in detail
            assert "clamped_bias" in detail

    def test_clamped_bias_matches_compute(self):
        ctx = _ctx(
            exposures={"a": 800, "b": 200},
            health={"a": 0.30, "b": 0.80},
            drawdown=0.20,
        )
        biases = ENGINE.compute_bias(ctx)
        desc = ENGINE.describe(ctx)
        for strat in biases:
            assert biases[strat] == pytest.approx(desc[strat]["clamped_bias"])

    def test_component_sum_equals_raw(self):
        ctx = _ctx(
            exposures={"a": 600, "b": 400},
            health={"a": 0.40, "b": 0.90},
            drawdown=0.12,
        )
        desc = ENGINE.describe(ctx)
        for strat, detail in desc.items():
            expected_raw = detail["exposure_bias"] + detail["drawdown_bias"] + detail["health_bias"]
            assert detail["raw_bias"] == pytest.approx(expected_raw, abs=1e-6)

    def test_describe_exposure_ratio_sums_to_1(self):
        ctx = _ctx(
            exposures={"a": 300, "b": 400, "c": 300},
            health={"a": 0.80, "b": 0.80, "c": 0.80},
        )
        desc = ENGINE.describe(ctx)
        total = sum(d["exposure_ratio"] for d in desc.values())
        assert total == pytest.approx(1.0, abs=1e-5)


# ── 8  Edge Cases ─────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_zero_total_exposure(self):
        """All exposures zero → total set to 1.0, no division error."""
        ctx = _ctx(exposures={"a": 0, "b": 0}, health={"a": 0.80, "b": 0.80})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == 0.0
        assert biases["b"] == 0.0

    def test_single_strategy_zero_exposure(self):
        ctx = _ctx(exposures={"a": 0}, health={"a": 0.80})
        biases = ENGINE.compute_bias(ctx)
        assert biases["a"] == 0.0

    def test_large_drawdown(self):
        """Drawdown = 0.90 → -0.20 from drawdown, still clamped properly."""
        ctx = _ctx(
            exposures={"a": 300, "b": 700},
            health={"a": 0.80, "b": 0.80},
            drawdown=0.90,
        )
        biases = ENGINE.compute_bias(ctx)
        assert all(-0.40 <= v <= 0.0 for v in biases.values())
