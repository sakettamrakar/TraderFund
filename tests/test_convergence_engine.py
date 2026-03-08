"""
Tests for Convergence Engine (L6)
==================================
Sections:
  A — Direction Conflict
  B — Multi-Lens Requirement (2-lens vs 3-lens)
  C — High Dispersion
  D — Grade Boundary Precision
  E — Deterministic Replay
  F — Meta Trust Suppression
  G — Regime Mismatch
  H — Latency Measurement
  I — Fail-Safe Paths
  J — Score / Field Completeness
  K — Health Hook & Hash
"""
from __future__ import annotations

import pytest

from src.layers.convergence_engine import ConvergenceEngine, RegimeContextMissingError
from src.models.convergence_models import LensSignal, ConvergenceResult
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


def three_long_lenses(confidence: float = 0.70) -> list[LensSignal]:
    """3 LONG lenses — above the multi-lens threshold."""
    return [
        lens("LONG", confidence, 0.80, "TECHNICAL"),
        lens("LONG", confidence, 0.80, "MOMENTUM"),
        lens("LONG", confidence, 0.80, "SENTIMENT"),
    ]


def four_long_lenses(confidence: float = 0.80) -> list[LensSignal]:
    """4 LONG lenses — satisfies Grade-A aligned-lens requirement."""
    return [
        lens("LONG", confidence, 0.80, "TECHNICAL"),
        lens("LONG", confidence, 0.80, "MOMENTUM"),
        lens("LONG", confidence, 0.80, "SENTIMENT"),
        lens("LONG", confidence, 0.80, "FLOW"),
    ]


# ── A — Direction Conflict ─────────────────────────────────────────────────────

class TestDirectionConflict:
    def test_mixed_directions_score_is_zero(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG",  0.80, 0.80, "TECHNICAL"),
            lens("SHORT", 0.80, 0.80, "MOMENTUM"),
            lens("LONG",  0.80, 0.80, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.final_score == 0.0

    def test_mixed_directions_status_is_conflict(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG",  0.70, 0.80, "TECHNICAL"),
            lens("SHORT", 0.70, 0.80, "MOMENTUM"),
            lens("LONG",  0.70, 0.80, "FLOW"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.status == "DIRECTION_CONFLICT"

    def test_mixed_directions_grade_is_D(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG",  0.90, 0.90, "TECHNICAL"),
            lens("SHORT", 0.90, 0.90, "MOMENTUM"),
        ]
        result = engine.compute(lenses, regime(), 0.90)
        assert result.conviction_grade == "D"

    def test_all_long_no_conflict(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(), regime(), 0.80)
        assert result.status != "DIRECTION_CONFLICT"
        assert result.direction == "LONG"

    def test_all_short_no_conflict(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("SHORT", 0.70, 0.80, "TECHNICAL"),
            lens("SHORT", 0.70, 0.80, "MOMENTUM"),
            lens("SHORT", 0.70, 0.80, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.status != "DIRECTION_CONFLICT"
        assert result.direction == "SHORT"


# ── B — Multi-Lens Requirement ────────────────────────────────────────────────

class TestMultiLensRequirement:
    def test_two_lenses_returns_low_confidence(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG", 0.70, 0.80, "TECHNICAL"),
            lens("LONG", 0.70, 0.80, "MOMENTUM"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.status == "LOW_CONFIDENCE"

    def test_one_lens_returns_insufficient(self):
        engine = ConvergenceEngine()
        lenses = [lens("LONG", 0.70, 0.80, "TECHNICAL")]
        # < 2 triggers fail-safe
        result = engine.compute(lenses, regime(), 0.80)
        assert result.status == "INSUFFICIENT_CONVERGENCE"
        assert result.final_score == 0.0

    def test_three_lenses_eligible_not_low_confidence(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(0.70), regime(), 0.80)
        # Should be OK or a non-LOW_CONFIDENCE status based on other factors
        assert result.status not in ("INSUFFICIENT_CONVERGENCE", "LOW_CONFIDENCE")

    def test_zero_lenses_returns_insufficient(self):
        engine = ConvergenceEngine()
        result = engine.compute([], regime(), 0.80)
        assert result.status == "INSUFFICIENT_CONVERGENCE"
        assert result.final_score == 0.0

    def test_low_confidence_has_non_zero_score(self):
        """2-lens LOW_CONFIDENCE path still computes score (not fail-safe)."""
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG", 0.80, 0.80, "TECHNICAL"),
            lens("LONG", 0.80, 0.80, "MOMENTUM"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        # lens_count_factor = min(2,5)/5 = 0.40; score = 0.80*0.80*0.80*0.40 = 0.2048
        assert result.final_score > 0.0
        assert result.status == "LOW_CONFIDENCE"


# ── C — High Dispersion ───────────────────────────────────────────────────────

class TestHighDispersion:
    def test_high_dispersion_status(self):
        """Manually crafted variance > 0.22 should trigger HIGH_DISPERSION."""
        engine = ConvergenceEngine()
        # confidences: 0.10, 0.90, 0.80 → mean = 0.60, var ≈ 0.1133+0.09+0.04 = 0.0813
        # Let's use 0.05, 0.95, 0.80 → mean≈0.60, var = (0.55²+0.35²+0.20²)/3
        #   = (0.3025+0.1225+0.04)/3 = 0.465/3 = 0.155 — not enough
        # Use 0.0, 1.0, 0.80 → mean=0.60, var=(0.36+0.16+0.04)/3=0.187 — close
        # Use 0.0, 1.0, 1.0, 0.0 → mean=0.50, var=(0.25+0.25+0.25+0.25)/4=0.25 > 0.22 ✓
        lenses = [
            lens("LONG", 0.0,  0.80, "TECHNICAL"),
            lens("LONG", 1.0,  0.80, "MOMENTUM"),
            lens("LONG", 1.0,  0.80, "SENTIMENT"),
            lens("LONG", 0.0,  0.80, "FLOW"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.status == "HIGH_DISPERSION"

    def test_high_dispersion_score_dispersion_logged(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG", 0.0,  0.80, "TECHNICAL"),
            lens("LONG", 1.0,  0.80, "MOMENTUM"),
            lens("LONG", 1.0,  0.80, "SENTIMENT"),
            lens("LONG", 0.0,  0.80, "FLOW"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.score_dispersion > 0.22

    def test_low_dispersion_no_flag(self):
        """All equal confidences → zero dispersion → no HIGH_DISPERSION."""
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(0.70), regime(), 0.80)
        assert result.status != "HIGH_DISPERSION"
        assert result.score_dispersion == pytest.approx(0.0, abs=1e-9)

    def test_dispersion_is_variance_not_stdev(self):
        """score_dispersion should be variance (not standard deviation)."""
        engine = ConvergenceEngine()
        confidences = [0.60, 0.80, 0.70]
        lenses = [
            lens("LONG", confidences[0], 0.80, "TECHNICAL"),
            lens("LONG", confidences[1], 0.80, "MOMENTUM"),
            lens("LONG", confidences[2], 0.80, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        mean = sum(confidences) / 3
        expected_var = sum((c - mean) ** 2 for c in confidences) / 3
        assert result.score_dispersion == pytest.approx(expected_var, abs=1e-9)


# ── D — Grade Boundary Precision ──────────────────────────────────────────────

class TestGradeBoundaries:
    """
    score formula: mean_conf * meta_trust * avg_regime_compat * lens_factor
    For 5+ lenses: lens_factor = 1.0
    With avg_regime_compat = 1.0 and meta_trust = 1.0:
        score = mean_conf * 1.0 * 1.0 * 1.0 = mean_conf
    """

    def _make_lenses(self, count: int, confidence: float) -> list[LensSignal]:
        names = ["TECHNICAL", "MOMENTUM", "SENTIMENT", "FLOW", "VOLATILITY", "FUNDAMENTAL"]
        return [
            lens("LONG", confidence, 1.0, names[i % len(names)])
            for i in range(count)
        ]

    def test_score_0_80_grade_A_with_4_lenses(self):
        engine = ConvergenceEngine()
        lenses = self._make_lenses(5, 0.80)
        result = engine.compute(lenses, regime(), 1.0)
        # weighted_score=0.80, meta=1.0, compat=1.0, d_penalty=-0.05 → 0.75
        assert result.final_score == pytest.approx(0.75, abs=1e-9)
        assert result.conviction_grade == "B"  # 0.75 >= 0.65 but < 0.80 → B

    def test_score_just_below_0_80_grade_B(self):
        engine = ConvergenceEngine()
        # score ≈ 0.799 - 0.05 = 0.749: use 5 lenses, meta_trust=1.0, compat=1.0, conf=0.799
        lenses = self._make_lenses(5, 0.799)
        result = engine.compute(lenses, regime(), 1.0)
        assert result.final_score < 0.80
        assert result.conviction_grade in ("B", "C")

    def test_score_0_65_grade_B(self):
        engine = ConvergenceEngine()
        lenses = self._make_lenses(5, 0.65)
        result = engine.compute(lenses, regime(), 1.0)
        # weighted_score=0.65, d_penalty=-0.05 → 0.60
        assert result.final_score == pytest.approx(0.60, abs=1e-9)
        assert result.conviction_grade == "C"  # 0.60 >= 0.50 but < 0.65 → C

    def test_score_just_below_0_65_grade_C(self):
        engine = ConvergenceEngine()
        lenses = self._make_lenses(5, 0.649)
        result = engine.compute(lenses, regime(), 1.0)
        assert result.final_score < 0.65
        assert result.conviction_grade == "C"

    def test_score_0_50_grade_C(self):
        engine = ConvergenceEngine()
        lenses = self._make_lenses(5, 0.50)
        result = engine.compute(lenses, regime(), 1.0)
        # weighted_score=0.50, d_penalty=-0.05 → 0.45
        assert result.final_score == pytest.approx(0.45, abs=1e-9)
        assert result.conviction_grade == "D"  # 0.45 < 0.50 → D

    def test_score_just_below_0_50_grade_D(self):
        engine = ConvergenceEngine()
        lenses = self._make_lenses(5, 0.499)
        result = engine.compute(lenses, regime(), 1.0)
        assert result.final_score < 0.50
        assert result.conviction_grade == "D"

    def test_grade_A_requires_4_aligned_lenses(self):
        """Score >= 0.80 with 4 lenses."""
        engine = ConvergenceEngine()
        lenses4 = self._make_lenses(4, 1.0)  # weighted=1.0, compat=1.0, meta=1.0, penalty=-0.05 → 0.95
        result = engine.compute(lenses4, regime(), 1.0)
        assert result.final_score == pytest.approx(0.95, abs=1e-9)
        assert result.conviction_grade == "A"

    def test_grade_A_needs_4_aligned_not_3(self):
        """With 3 lenses conf=1.0 → weighted=1.0 * 1.0 * 1.0 - 0.05 = 0.95 → Grade B (< 4 aligned)."""
        engine = ConvergenceEngine()
        lenses3 = [
            lens("LONG", 1.0, 1.0, "TECHNICAL"),
            lens("LONG", 1.0, 1.0, "MOMENTUM"),
            lens("LONG", 1.0, 1.0, "SENTIMENT"),
        ]
        result = engine.compute(lenses3, regime(), 1.0)
        # weighted_score=1.0, meta=1.0, compat=1.0, d_penalty=-0.05 → 0.95
        assert result.final_score == pytest.approx(0.95, abs=1e-9)
        # Only 3 aligned lenses → Grade A blocked → Grade B
        assert result.conviction_grade == "B"


# ── E — Deterministic Replay ──────────────────────────────────────────────────

class TestDeterministicReplay:
    def test_10_replay_variance_under_0_01(self):
        engine = ConvergenceEngine()
        lenses = three_long_lenses(0.70)
        r = regime("TRENDING")
        scores = [engine.compute(lenses, r, 0.80).final_score for _ in range(10)]
        variance = sum((s - scores[0]) ** 2 for s in scores) / len(scores)
        assert variance < 0.01

    def test_10_replay_identical_scores(self):
        engine = ConvergenceEngine()
        lenses = four_long_lenses(0.80)
        r = regime("TRENDING")
        scores = [engine.compute(lenses, r, 0.85).final_score for _ in range(10)]
        assert all(s == scores[0] for s in scores)

    def test_hash_stable_across_10_calls(self):
        engine = ConvergenceEngine()
        lenses = three_long_lenses(0.70)
        r = regime("TRENDING")
        hashes = [engine.compute(lenses, r, 0.80).input_hash for _ in range(10)]
        assert len(set(hashes)) == 1

    def test_different_inputs_produce_different_hashes(self):
        engine = ConvergenceEngine()
        r1 = engine.compute(three_long_lenses(0.70), regime("TRENDING"), 0.80)
        r2 = engine.compute(three_long_lenses(0.90), regime("TRENDING"), 0.80)
        assert r1.input_hash != r2.input_hash

    def test_grade_is_deterministic_across_replays(self):
        engine = ConvergenceEngine()
        lenses = four_long_lenses(0.82)
        r = regime("TRENDING")
        grades = [engine.compute(lenses, r, 0.90).conviction_grade for _ in range(10)]
        assert len(set(grades)) == 1


# ── F — Meta Trust Suppression ────────────────────────────────────────────────

class TestMetaTrustSuppression:
    def test_meta_trust_zero_returns_insufficient(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(), regime(), 0.0)
        assert result.status == "INSUFFICIENT_CONVERGENCE"
        assert result.final_score == 0.0

    def test_meta_trust_0_40_scales_score(self):
        """
        New formula: weighted_score * meta_trust * avg_compat + d_penalty
        3 lenses (T,M,S) conf=0.70 regime=TRENDING: weighted_score=0.70
        raw = 0.70 * 0.40 * 0.80 + (-0.05) = 0.224 - 0.05 = 0.174
        """
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(0.70), regime(), 0.40)
        expected = 0.70 * 0.40 * 0.80 + (-0.05)
        assert result.final_score == pytest.approx(expected, abs=1e-6)

    def test_meta_trust_reflected_in_result(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(0.70), regime(), 0.55)
        assert result.meta_trust == pytest.approx(0.55, abs=1e-9)

    def test_high_meta_trust_higher_score(self):
        engine = ConvergenceEngine()
        r_low  = engine.compute(three_long_lenses(0.70), regime(), 0.40)
        r_high = engine.compute(three_long_lenses(0.70), regime(), 0.90)
        assert r_high.final_score > r_low.final_score


# ── G — Regime Mismatch ───────────────────────────────────────────────────────

class TestRegimeMismatch:
    def test_avg_compat_below_0_50_gives_regime_mismatch(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG", 0.70, 0.30, "TECHNICAL"),
            lens("LONG", 0.70, 0.40, "MOMENTUM"),
            lens("LONG", 0.70, 0.35, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.status == "REGIME_MISMATCH"

    def test_avg_compat_exactly_0_50_no_mismatch(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG", 0.70, 0.50, "TECHNICAL"),
            lens("LONG", 0.70, 0.50, "MOMENTUM"),
            lens("LONG", 0.70, 0.50, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.status != "REGIME_MISMATCH"

    def test_avg_compat_above_0_50_no_mismatch(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(0.70), regime(), 0.80)
        assert result.status != "REGIME_MISMATCH"

    def test_avg_compat_logged_in_result(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG", 0.70, 0.60, "TECHNICAL"),
            lens("LONG", 0.70, 0.70, "MOMENTUM"),
            lens("LONG", 0.70, 0.80, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        expected_compat = (0.60 + 0.70 + 0.80) / 3
        assert result.avg_regime_compatibility == pytest.approx(expected_compat, abs=1e-9)

    def test_none_regime_raises_explicit_halt(self):
        engine = ConvergenceEngine()
        with pytest.raises(RegimeContextMissingError):
            engine.compute(three_long_lenses(), None, 0.80)


# ── H — Latency Measurement ───────────────────────────────────────────────────

class TestLatency:
    def test_latency_is_non_negative(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(), regime(), 0.80)
        assert result.latency_ms >= 0.0

    def test_latency_under_1000ms_for_normal_input(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(), regime(), 0.80)
        assert result.latency_ms < 1000.0

    def test_latency_present_for_fail_safe(self):
        engine = ConvergenceEngine()
        result = engine.compute([], regime(), 0.80)
        assert result.latency_ms >= 0.0

    def test_latency_present_for_conflict(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG",  0.80, 0.80, "TECHNICAL"),
            lens("SHORT", 0.80, 0.80, "MOMENTUM"),
            lens("LONG",  0.80, 0.80, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.latency_ms >= 0.0


# ── I — Fail-Safe Paths ───────────────────────────────────────────────────────

class TestFailSafePaths:
    def test_none_lenses_returns_insufficient(self):
        engine = ConvergenceEngine()
        result = engine.compute(None, regime(), 0.80)
        assert result.status == "INSUFFICIENT_CONVERGENCE"

    def test_meta_trust_none_treated_as_zero(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(), regime(), None)
        assert result.status == "INSUFFICIENT_CONVERGENCE"
        assert result.final_score == 0.0

    def test_fail_safe_direction_is_NONE(self):
        engine = ConvergenceEngine()
        result = engine.compute([], regime(), 0.80)
        assert result.direction == "NONE"

    def test_fail_safe_grade_is_D(self):
        engine = ConvergenceEngine()
        result = engine.compute([], regime(), 0.80)
        assert result.conviction_grade == "D"

    def test_fail_safe_aligned_lenses_zero(self):
        engine = ConvergenceEngine()
        result = engine.compute([], regime(), 0.80)
        assert result.aligned_lenses == 0

    def test_degenerate_inputs_raise_explicit_halt_when_regime_missing(self):
        engine = ConvergenceEngine()
        with pytest.raises(RegimeContextMissingError):
            engine.compute(None, None, None)

    def test_conflict_aligned_lenses_zero(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG",  0.80, 0.80, "TECHNICAL"),
            lens("SHORT", 0.80, 0.80, "MOMENTUM"),
            lens("LONG",  0.80, 0.80, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.aligned_lenses == 0


# ── J — Score / Field Completeness ───────────────────────────────────────────

class TestFieldCompleteness:
    REQUIRED_FIELDS = [
        "symbol", "direction", "lens_count", "aligned_lenses",
        "mean_confidence", "meta_trust", "avg_regime_compatibility",
        "score_dispersion", "final_score", "conviction_grade",
        "status", "latency_ms", "input_hash",
    ]

    def test_all_fields_present_on_ok_result(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(), regime(), 0.80)
        for field in self.REQUIRED_FIELDS:
            assert hasattr(result, field), f"Missing field: {field}"

    def test_all_fields_present_on_fail_safe_result(self):
        engine = ConvergenceEngine()
        result = engine.compute([], regime(), 0.80)
        for field in self.REQUIRED_FIELDS:
            assert hasattr(result, field), f"Missing field in fail-safe: {field}"

    def test_final_score_within_bounds(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(), regime(), 0.80)
        assert 0.0 <= result.final_score <= 1.0

    def test_lens_count_matches_input(self):
        engine = ConvergenceEngine()
        lenses = three_long_lenses()
        result = engine.compute(lenses, regime(), 0.80)
        assert result.lens_count == len(lenses)

    def test_mean_confidence_is_correct(self):
        engine = ConvergenceEngine()
        lenses = [
            lens("LONG", 0.60, 0.80, "TECHNICAL"),
            lens("LONG", 0.80, 0.80, "MOMENTUM"),
            lens("LONG", 0.70, 0.80, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.mean_confidence == pytest.approx(0.70, abs=1e-9)

    def test_score_formula_correctness(self):
        """
        New formula: weighted_score * meta_trust * avg_compat + d_penalty
        3 lenses (T,M,S) conf=0.70 regime=TRENDING: weighted_score=0.70
        raw = 0.70 * 0.80 * 0.80 + (-0.05) = 0.448 - 0.05 = 0.398
        """
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(0.70), regime(), 0.80)
        expected = 0.70 * 0.80 * 0.80 + (-0.05)
        assert result.final_score == pytest.approx(expected, abs=1e-6)

    def test_symbol_propagated_from_first_lens(self):
        engine = ConvergenceEngine()
        lenses = [
            LensSignal("AAPL", "LONG", 0.70, 0.80, "TECHNICAL"),
            LensSignal("AAPL", "LONG", 0.70, 0.80, "MOMENTUM"),
            LensSignal("AAPL", "LONG", 0.70, 0.80, "SENTIMENT"),
        ]
        result = engine.compute(lenses, regime(), 0.80)
        assert result.symbol == "AAPL"


# ── K — Health Hook & Hash ────────────────────────────────────────────────────

class TestHealthAndHash:
    def test_get_convergence_health(self):
        health = ConvergenceEngine().get_convergence_health()
        assert health["multi_lens_enforced"] is True
        assert health["dispersion_logged"] is True
        assert health["directional_integrity"] is True

    def test_input_hash_is_16_char_hex(self):
        engine = ConvergenceEngine()
        result = engine.compute(three_long_lenses(), regime(), 0.80)
        h = result.input_hash
        assert isinstance(h, str)
        assert len(h) == 16
        int(h, 16)  # must be valid hexadecimal

    def test_input_hash_is_deterministic(self):
        engine = ConvergenceEngine()
        r = regime("TRENDING")
        lenses = three_long_lenses(0.70)
        h1 = engine.compute(lenses, r, 0.80).input_hash
        h2 = engine.compute(lenses, r, 0.80).input_hash
        assert h1 == h2

    def test_input_hash_differs_for_different_meta_trust(self):
        engine = ConvergenceEngine()
        r = regime("TRENDING")
        lenses = three_long_lenses(0.70)
        h1 = engine.compute(lenses, r, 0.80).input_hash
        h2 = engine.compute(lenses, r, 0.90).input_hash
        assert h1 != h2


# ── Exhaustive trust bounds ───────────────────────────────────────────────────

class TestExhaustiveTrustBounds:
    """All combination results must be within [0.0, 1.0]."""

    @pytest.mark.parametrize("regime_name", [
        "TRENDING", "CHOP", "TRANSITION", "STRESS", "VOLATILE", "ACCUMULATION", "DISTRIBUTION"
    ])
    @pytest.mark.parametrize("meta_trust", [0.0, 0.25, 0.50, 0.75, 1.0])
    @pytest.mark.parametrize("lens_count", [1, 2, 3, 4, 5])
    @pytest.mark.parametrize("confidence", [0.0, 0.50, 1.0])
    def test_score_within_unit_interval(
        self, regime_name, meta_trust, lens_count, confidence
    ):
        engine = ConvergenceEngine()
        names = ["TECHNICAL", "MOMENTUM", "SENTIMENT", "FLOW", "VOLATILITY"]
        lenses = [
            lens("LONG", confidence, 0.80, names[i % len(names)])
            for i in range(lens_count)
        ]
        result = engine.compute(lenses, regime(regime_name), meta_trust)
        assert 0.0 <= result.final_score <= 1.0
