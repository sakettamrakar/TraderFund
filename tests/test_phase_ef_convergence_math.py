"""
Tests for Phase F — Convergence Math (Weighted Vector Model)
=============================================================
Covers:
  1.  High variance penalty (-0.10)
  2.  Low variance penalty (-0.05)
  3.  Regime weight shifting (TRENDING, CHOP, STRESS)
  4.  Weight normalization (sum == 1.0)
  5.  Portfolio bias applied correctly
  6.  No score > 1.0
  7.  Confluence downgrade logic (WATCHLIST when < 3 lenses >= 0.60)
  8.  Deterministic replay
  9.  5 invariants under TRENDING
  10. 5 invariants under STRESS
  11. High-drawdown scenario (portfolio bias)
  12. Portfolio concentration scenario
"""
from __future__ import annotations

import json
import pytest

from src.layers.convergence_engine import ConvergenceEngine
from src.models.convergence_models import LensSignal
from src.models.meta_models import RegimeState


# ── Helpers ───────────────────────────────────────────────────────────────────

def regime(r: str = "TRENDING", vol: float = 0.4) -> RegimeState:
    return RegimeState(regime=r, volatility=vol)


def lens(
    direction: str = "LONG",
    confidence: float = 0.70,
    regime_compat: float = 0.80,
    lens_name: str = "TECHNICAL",
    symbol: str = "SPY",
) -> LensSignal:
    return LensSignal(
        symbol=symbol,
        direction=direction,
        confidence=confidence,
        regime_compatibility=regime_compat,
        lens_name=lens_name,
    )


def five_lens_set(conf: float = 0.70, compat: float = 0.80) -> list[LensSignal]:
    """Canonical 5-lens set."""
    return [
        lens("LONG", conf, compat, "TECHNICAL"),
        lens("LONG", conf, compat, "MOMENTUM"),
        lens("LONG", conf, compat, "SENTIMENT"),
        lens("LONG", conf, compat, "FLOW"),
        lens("LONG", conf, compat, "FUNDAMENTAL"),
    ]


def three_lens_set(conf: float = 0.70, compat: float = 0.80) -> list[LensSignal]:
    return [
        lens("LONG", conf, compat, "TECHNICAL"),
        lens("LONG", conf, compat, "MOMENTUM"),
        lens("LONG", conf, compat, "SENTIMENT"),
    ]


ENGINE = ConvergenceEngine()


# ── 1  High Variance Penalty (-0.10) ─────────────────────────────────────────

class TestHighVariancePenalty:

    def test_high_dispersion_scores_minus_0_10(self):
        """When variance > 0.20 → d_penalty = -0.10."""
        # conf=[0.05, 0.95, 0.05] → mean=0.35, var=0.18 — not enough
        # conf=[0.01, 0.99, 0.01] → mean=0.3367, var≈0.2134 > 0.20
        lenses = [
            lens("LONG", 0.01, 0.80, "TECHNICAL"),
            lens("LONG", 0.99, 0.80, "MOMENTUM"),
            lens("LONG", 0.01, 0.80, "SENTIMENT"),
        ]
        result = ENGINE.compute(lenses, regime(), 1.0)
        assert result.dispersion_penalty == pytest.approx(-0.10)

    def test_extreme_spread(self):
        """conf=[0.01, 0.99, 0.01, 0.99, 0.01] → var > 0.20."""
        lenses = [
            lens("LONG", 0.01, 0.80, "TECHNICAL"),
            lens("LONG", 0.99, 0.80, "MOMENTUM"),
            lens("LONG", 0.01, 0.80, "SENTIMENT"),
            lens("LONG", 0.99, 0.80, "FLOW"),
            lens("LONG", 0.01, 0.80, "FUNDAMENTAL"),
        ]
        result = ENGINE.compute(lenses, regime(), 1.0)
        assert result.dispersion_penalty == pytest.approx(-0.10)


# ── 2  Low Variance Penalty (-0.05) ──────────────────────────────────────────

class TestLowVariancePenalty:

    def test_identical_confidences(self):
        """All equal → variance == 0 < 0.02 → -0.05."""
        result = ENGINE.compute(five_lens_set(0.70), regime(), 1.0)
        assert result.dispersion_penalty == pytest.approx(-0.05)

    def test_very_close_confidences(self):
        """Tiny variance < 0.02 → -0.05."""
        lenses = [
            lens("LONG", 0.70, 0.80, "TECHNICAL"),
            lens("LONG", 0.71, 0.80, "MOMENTUM"),
            lens("LONG", 0.69, 0.80, "SENTIMENT"),
        ]
        result = ENGINE.compute(lenses, regime(), 1.0)
        assert result.dispersion_penalty == pytest.approx(-0.05)

    def test_moderate_variance_no_penalty(self):
        """Variance in (0.02, 0.20) → 0.0."""
        # conf=[0.40, 0.90, 0.60] → mean=0.6333, var≈0.0422 → in (0.02, 0.20)
        lenses = [
            lens("LONG", 0.40, 0.80, "TECHNICAL"),
            lens("LONG", 0.90, 0.80, "MOMENTUM"),
            lens("LONG", 0.60, 0.80, "SENTIMENT"),
        ]
        result = ENGINE.compute(lenses, regime(), 1.0)
        assert result.dispersion_penalty == pytest.approx(0.0)


# ── 3  Regime Weight Shifting ────────────────────────────────────────────────

class TestRegimeWeightShifting:

    def test_trending_boosts_technical_and_flow(self):
        """TRENDING: TECHNICAL +0.05, FLOW +0.05."""
        lenses = five_lens_set(0.70)
        result = ENGINE.compute(lenses, regime("TRENDING"), 1.0)
        weights = json.loads(result.lens_weights)
        # TECHNICAL base 0.20 + 0.05 = 0.25
        # FLOW base 0.25 + 0.05 = 0.30
        # Total raw: 0.25 + 0.30 + 0.20 + 0.20 + 0.15 = 1.10
        assert weights["TECHNICAL"] == pytest.approx(0.25 / 1.10, abs=1e-6)
        assert weights["FLOW"] == pytest.approx(0.30 / 1.10, abs=1e-6)

    def test_chop_boosts_sentiment_fundamental_reduces_technical(self):
        """CHOP: SENTIMENT +0.05, FUNDAMENTAL +0.05, TECHNICAL -0.05."""
        lenses = five_lens_set(0.70)
        result = ENGINE.compute(lenses, regime("CHOP"), 1.0)
        weights = json.loads(result.lens_weights)
        # T: 0.20-0.05=0.15, S: 0.20+0.05=0.25, F: 0.25 (no adj), U: 0.20+0.05=0.25, M: 0.15
        total = 0.15 + 0.25 + 0.25 + 0.25 + 0.15
        assert weights["TECHNICAL"] == pytest.approx(0.15 / total, abs=1e-6)
        assert weights["SENTIMENT"] == pytest.approx(0.25 / total, abs=1e-6)
        assert weights["FUNDAMENTAL"] == pytest.approx(0.25 / total, abs=1e-6)

    def test_stress_boosts_fundamental_reduces_technical(self):
        """STRESS: FUNDAMENTAL +0.10, TECHNICAL -0.10."""
        lenses = five_lens_set(0.70)
        result = ENGINE.compute(lenses, regime("STRESS"), 1.0)
        weights = json.loads(result.lens_weights)
        # T: 0.20-0.10=0.10, U: 0.20+0.10=0.30, S: 0.20, F: 0.25, M: 0.15
        total = 0.10 + 0.30 + 0.20 + 0.25 + 0.15
        assert weights["TECHNICAL"] == pytest.approx(0.10 / total, abs=1e-6)
        assert weights["FUNDAMENTAL"] == pytest.approx(0.30 / total, abs=1e-6)

    def test_unknown_regime_uses_base_weights(self):
        """Unknown regime → no adjustments, base weights normalised."""
        lenses = five_lens_set(0.70)
        result = ENGINE.compute(lenses, regime("TRANSITION"), 1.0)
        weights = json.loads(result.lens_weights)
        # base: T=0.20, M=0.15, S=0.20, F=0.25, U=0.20  total=1.00
        assert weights["TECHNICAL"] == pytest.approx(0.20, abs=1e-6)
        assert weights["FLOW"] == pytest.approx(0.25, abs=1e-6)
        assert weights["MOMENTUM"] == pytest.approx(0.15, abs=1e-6)


# ── 4  Weight Normalization ──────────────────────────────────────────────────

class TestWeightNormalization:

    @pytest.mark.parametrize("r", ["TRENDING", "CHOP", "STRESS", "TRANSITION", "VOLATILE"])
    def test_weights_sum_to_one(self, r):
        lenses = five_lens_set()
        result = ENGINE.compute(lenses, regime(r), 1.0)
        weights = json.loads(result.lens_weights)
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-8)

    def test_3_lens_weights_sum_to_one(self):
        lenses = three_lens_set()
        result = ENGINE.compute(lenses, regime("TRENDING"), 1.0)
        weights = json.loads(result.lens_weights)
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-8)

    def test_all_weights_non_negative(self):
        """STRESS reduces TECHNICAL by 0.10 → T=0.10 which is still ≥ 0."""
        lenses = five_lens_set()
        result = ENGINE.compute(lenses, regime("STRESS"), 1.0)
        weights = json.loads(result.lens_weights)
        for w in weights.values():
            assert w >= 0.0


# ── 5  Portfolio Bias Applied Correctly ──────────────────────────────────────

class TestPortfolioBias:

    def test_zero_bias_no_effect(self):
        result_no_bias = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=0.0)
        result_default = ENGINE.compute(five_lens_set(0.80), regime(), 1.0)
        assert result_no_bias.final_score == result_default.final_score

    def test_negative_bias_reduces_score(self):
        base = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=0.0)
        biased = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=-0.20)
        assert biased.final_score < base.final_score

    def test_bias_formula(self):
        """final = clamp(base * (1 + perf_mod) * (1 + portfolio_bias))."""
        result = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=-0.20)
        # base_score = 0.80 * 1.0 * 0.80 + (-0.05) = 0.59
        base = result.base_score
        expected = max(0.0, min(1.0, base * (1.0 + 0.0) * (1.0 + (-0.20))))
        assert result.final_score == pytest.approx(expected, abs=1e-9)

    def test_positive_bias_clamped_to_zero(self):
        """Positive portfolio_bias should be clamped to 0.0."""
        result = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=0.50)
        no_bias = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=0.0)
        assert result.final_score == no_bias.final_score

    def test_extreme_negative_bias_clamped(self):
        """portfolio_bias = -1.0 → clamped to -0.40."""
        extreme = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=-1.0)
        capped = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=-0.40)
        assert extreme.final_score == capped.final_score

    def test_portfolio_bias_stored_in_result(self):
        result = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=-0.15)
        assert result.portfolio_bias == pytest.approx(-0.15)


# ── 6  No Score > 1.0 ────────────────────────────────────────────────────────

class TestScoreCeiling:

    def test_max_confidence_max_trust_max_compat(self):
        lenses = five_lens_set(1.0, 1.0)
        result = ENGINE.compute(lenses, regime(), 1.0)
        assert result.final_score <= 1.0

    def test_score_non_negative(self):
        lenses = five_lens_set(0.01, 0.01)
        result = ENGINE.compute(lenses, regime(), 0.01, portfolio_bias=-0.40)
        assert result.final_score >= 0.0

    @pytest.mark.parametrize("conf", [0.0, 0.1, 0.5, 0.9, 1.0])
    def test_score_in_unit_interval(self, conf):
        lenses = five_lens_set(conf)
        result = ENGINE.compute(lenses, regime(), 1.0, portfolio_bias=-0.40)
        assert 0.0 <= result.final_score <= 1.0


# ── 7  Confluence Downgrade (WATCHLIST) ───────────────────────────────────────

class TestConfluenceDowngrade:

    def test_low_confidence_triggers_watchlist(self):
        """All lenses conf < 0.60 → 0 lenses above 0.60 → WATCHLIST."""
        lenses = five_lens_set(0.55)
        result = ENGINE.compute(lenses, regime(), 1.0)
        assert result.status == "WATCHLIST"

    def test_exactly_3_lenses_at_0_60_is_ok(self):
        """3 lenses >= 0.60 → enough for confluence rule."""
        lenses = [
            lens("LONG", 0.60, 0.80, "TECHNICAL"),
            lens("LONG", 0.60, 0.80, "MOMENTUM"),
            lens("LONG", 0.60, 0.80, "SENTIMENT"),
            lens("LONG", 0.40, 0.80, "FLOW"),
            lens("LONG", 0.40, 0.80, "FUNDAMENTAL"),
        ]
        result = ENGINE.compute(lenses, regime(), 1.0)
        # status may be OK or LOW_CONFIDENCE but NOT WATCHLIST
        assert result.status != "WATCHLIST"

    def test_2_lenses_at_0_60_triggers_watchlist(self):
        """Only 2 lenses >= 0.60 → WATCHLIST."""
        lenses = [
            lens("LONG", 0.60, 0.80, "TECHNICAL"),
            lens("LONG", 0.60, 0.80, "MOMENTUM"),
            lens("LONG", 0.50, 0.80, "SENTIMENT"),
            lens("LONG", 0.50, 0.80, "FLOW"),
            lens("LONG", 0.50, 0.80, "FUNDAMENTAL"),
        ]
        result = ENGINE.compute(lenses, regime(), 1.0)
        assert result.status == "WATCHLIST"

    def test_watchlist_does_not_override_regime_mismatch(self):
        """If status is already REGIME_MISMATCH, WATCHLIST won't override."""
        lenses = [
            lens("LONG", 0.55, 0.30, "TECHNICAL"),
            lens("LONG", 0.55, 0.30, "MOMENTUM"),
            lens("LONG", 0.55, 0.30, "SENTIMENT"),
        ]
        result = ENGINE.compute(lenses, regime(), 1.0)
        # compat avg = 0.30 < 0.50 → REGIME_MISMATCH (set before confluence check)
        assert result.status == "REGIME_MISMATCH"


# ── 8  Deterministic Replay ──────────────────────────────────────────────────

class TestDeterministicReplay:

    def test_10_runs_identical(self):
        lenses = five_lens_set(0.75)
        results = [ENGINE.compute(lenses, regime(), 0.85) for _ in range(10)]
        scores = [r.final_score for r in results]
        assert max(scores) - min(scores) < 0.01

    def test_hash_invariant(self):
        lenses = five_lens_set(0.75)
        results = [ENGINE.compute(lenses, regime(), 0.85) for _ in range(10)]
        hashes = {r.input_hash for r in results}
        assert len(hashes) == 1

    def test_replay_with_portfolio_bias(self):
        lenses = five_lens_set(0.75)
        results = [ENGINE.compute(lenses, regime(), 0.85, portfolio_bias=-0.10) for _ in range(10)]
        scores = [r.final_score for r in results]
        assert max(scores) - min(scores) < 0.001


# ── 9  5 Invariants Under TRENDING ────────────────────────────────────────────

class TestTrendingInvariants:

    def test_higher_confidence_higher_score(self):
        low = ENGINE.compute(five_lens_set(0.50), regime("TRENDING"), 1.0)
        high = ENGINE.compute(five_lens_set(0.80), regime("TRENDING"), 1.0)
        assert high.final_score > low.final_score

    def test_higher_trust_higher_score(self):
        low_t = ENGINE.compute(five_lens_set(0.70), regime("TRENDING"), 0.50)
        high_t = ENGINE.compute(five_lens_set(0.70), regime("TRENDING"), 0.90)
        assert high_t.final_score > low_t.final_score

    def test_score_within_unit(self):
        result = ENGINE.compute(five_lens_set(0.90), regime("TRENDING"), 1.0)
        assert 0.0 <= result.final_score <= 1.0

    def test_technical_weight_boosted(self):
        result = ENGINE.compute(five_lens_set(0.70), regime("TRENDING"), 1.0)
        weights = json.loads(result.lens_weights)
        # TRENDING boosts TECHNICAL +0.05 → higher than base 0.20 normalised
        # Compare with MOMENTUM which gets no boost
        assert weights["TECHNICAL"] > weights["MOMENTUM"]

    def test_negative_bias_reduces_score(self):
        base = ENGINE.compute(five_lens_set(0.70), regime("TRENDING"), 1.0)
        biased = ENGINE.compute(five_lens_set(0.70), regime("TRENDING"), 1.0, portfolio_bias=-0.30)
        assert biased.final_score < base.final_score


# ── 10  5 Invariants Under STRESS ─────────────────────────────────────────────

class TestStressInvariants:

    def test_fundamental_weight_highest(self):
        result = ENGINE.compute(five_lens_set(0.70), regime("STRESS"), 1.0)
        weights = json.loads(result.lens_weights)
        assert weights["FUNDAMENTAL"] == max(weights.values())

    def test_technical_weight_lowest(self):
        result = ENGINE.compute(five_lens_set(0.70), regime("STRESS"), 1.0)
        weights = json.loads(result.lens_weights)
        assert weights["TECHNICAL"] == min(weights.values())

    def test_score_bounded(self):
        result = ENGINE.compute(five_lens_set(0.70), regime("STRESS"), 1.0, portfolio_bias=-0.40)
        assert 0.0 <= result.final_score <= 1.0

    def test_more_trust_more_score(self):
        low = ENGINE.compute(five_lens_set(0.70), regime("STRESS"), 0.30)
        high = ENGINE.compute(five_lens_set(0.70), regime("STRESS"), 0.90)
        assert high.final_score > low.final_score

    def test_stress_score_deterministic(self):
        results = [ENGINE.compute(five_lens_set(0.70), regime("STRESS"), 0.80) for _ in range(5)]
        assert all(r.final_score == results[0].final_score for r in results)


# ── 11  High-Drawdown Scenario (Portfolio Bias) ──────────────────────────────

class TestHighDrawdownScenario:

    def test_max_bias_at_high_drawdown(self):
        """portfolio_bias = -0.40 → significant score reduction."""
        no_dd = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=0.0)
        high_dd = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=-0.40)
        # final = base * (1 + 0) * (1 - 0.40) = 0.60 * base
        assert high_dd.final_score == pytest.approx(no_dd.base_score * 0.60, abs=1e-9)

    def test_portfolio_bias_field_recorded(self):
        result = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=-0.25)
        assert result.portfolio_bias == pytest.approx(-0.25)

    def test_bias_does_not_make_score_negative(self):
        result = ENGINE.compute(five_lens_set(0.10), regime(), 0.20, portfolio_bias=-0.40)
        assert result.final_score >= 0.0


# ── 12  Portfolio Concentration Scenario ──────────────────────────────────────

class TestPortfolioConcentrationScenario:

    def test_heavy_bias_depresses_grade(self):
        """With -0.40 bias, a B-grade signal could drop to C or D."""
        # 5-lens, conf=0.85, compat=0.80, trust=1.0 → base ≈ 0.85*1.0*0.80 - 0.05 = 0.63
        no_bias = ENGINE.compute(five_lens_set(0.85, 0.80), regime(), 1.0)
        biased = ENGINE.compute(five_lens_set(0.85, 0.80), regime(), 1.0, portfolio_bias=-0.40)
        # biased.final_score ≈ 0.63 * 0.60 ≈ 0.378 → Grade D
        assert biased.conviction_grade in ("C", "D")
        assert biased.final_score < no_bias.final_score

    def test_moderate_bias_still_tradeable(self):
        """With -0.10 bias, high-confidence signal still viable."""
        result = ENGINE.compute(five_lens_set(0.95, 0.95), regime(), 1.0, portfolio_bias=-0.10)
        # base ≈ 0.95*1.0*0.95 - 0.05 = 0.8525; final ≈ 0.8525 * 0.90 ≈ 0.7673
        assert result.final_score > 0.50
        assert result.conviction_grade in ("A", "B")

    def test_bias_in_result_matches_input(self):
        result = ENGINE.compute(five_lens_set(0.80), regime(), 1.0, portfolio_bias=-0.10)
        assert result.portfolio_bias == pytest.approx(-0.10)
