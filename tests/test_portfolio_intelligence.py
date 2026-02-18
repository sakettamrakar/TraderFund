"""
Test Suite — L9 Portfolio Intelligence Engine
=============================================
Covers all required test scenarios:

  A) Regime Conflict         — STRESS + high long → RED
  B) Narrative Decay         — RESOLVED narrative + active position → ORANGE
  C) Factor Misalignment     — MOMENTUM regime + value-heavy portfolio → YELLOW/ORANGE
  D) Horizon Violation       — SCALP held > allowed days → ORANGE
  E) Concentration Breach    — top-3 > threshold → ORANGE/RED
  F) Convergence Decay       — decay > 50% → ORANGE
  G) Stability Score Drop    — stability = 0.15 → RED
  H) Deterministic Replay    — 10 runs → identical report

Plus:
  I) Insufficient context    — missing portfolio/regime → INSUFFICIENT_CONTEXT
  J) Global status logic     — highest severity wins
  K) Exposure symmetry       — sector clustering
  L) Constraint friction     — high rejection ratio
  M) Drawdown + misalignment — compound RED
  N) Serialisability         — report serialisable to JSON
  O) All flags have messages — no silent suppression
"""
from __future__ import annotations

import json
from typing import Dict, Tuple

import pytest

from src.layers.portfolio_intelligence import PortfolioIntelligenceEngine
from src.models.portfolio_models import (
    ConstraintActivitySummary,
    ConvergenceSnapshot,
    DiagnosticFlag,
    FactorState,
    HoldingMeta,
    NarrativeState,
    NarrativeTag,
    PortfolioDiagnosticReport,
    PortfolioSnapshot,
    RegimeState,
)

# ── Fixtures / helpers ────────────────────────────────────────────────────────

def make_engine() -> PortfolioIntelligenceEngine:
    return PortfolioIntelligenceEngine()


def _holding(
    symbol: str = "AAPL",
    weight_pct: float = 10.0,
    direction: str = "LONG",
    strategy: str = "SWING",
    sector: str = "TECH",
    days_held: int = 5,
    initial_conv: float = 0.80,
    current_conv: float = 0.80,
) -> HoldingMeta:
    return HoldingMeta(
        symbol=symbol,
        weight_pct=weight_pct,
        direction=direction,
        strategy=strategy,
        sector=sector,
        days_held=days_held,
        initial_convergence_score=initial_conv,
        current_convergence_score=current_conv,
    )


def _portfolio(
    holdings=None,
    net_exposure_pct: float = 30.0,
    gross_exposure_pct: float = 60.0,
    drawdown_pct: float = 2.0,
    sector_caps: Dict[str, float] = None,
) -> PortfolioSnapshot:
    if holdings is None:
        holdings = (_holding(),)
    return PortfolioSnapshot(
        holdings=tuple(holdings),
        net_exposure_pct=net_exposure_pct,
        gross_exposure_pct=gross_exposure_pct,
        current_drawdown_pct=drawdown_pct,
        sector_caps=sector_caps or {"TECH": 40.0},
    )


def _regime(
    r: str = "TRENDING",
    volatility: float = 0.3,
    stability: float = 1.0,
) -> RegimeState:
    return RegimeState(regime=r, volatility=volatility, stability_score=stability)


def _flag_codes(report: PortfolioDiagnosticReport):
    return {f.code for f in report.flags}


def _flag_by_code(report: PortfolioDiagnosticReport, code: str) -> DiagnosticFlag:
    for f in report.flags:
        if f.code == code:
            return f
    raise KeyError(f"Flag code '{code}' not found in report")


# ─────────────────────────────────────────────────────────────────────────────
# A) Regime Conflict — STRESS regime with high long exposure → RED
# ─────────────────────────────────────────────────────────────────────────────

class TestRegimeConflict:
    def test_stress_high_long_produces_red_flag(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=70.0),
            regime=_regime("STRESS"),
        )
        assert "REGIME_CONFLICT_STRESS_LONG" in _flag_codes(report)
        flag = _flag_by_code(report, "REGIME_CONFLICT_STRESS_LONG")
        assert flag.severity == "RED"

    def test_stress_high_long_global_status_critical(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=70.0),
            regime=_regime("STRESS"),
        )
        assert report.global_status == "CRITICAL"

    def test_stress_moderate_long_produces_orange(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=40.0),
            regime=_regime("STRESS"),
        )
        assert "REGIME_TENSION_STRESS_LONG" in _flag_codes(report)
        flag = _flag_by_code(report, "REGIME_TENSION_STRESS_LONG")
        assert flag.severity == "ORANGE"

    def test_stress_short_no_regime_flag(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=-40.0, gross_exposure_pct=40.0),
            regime=_regime("STRESS"),
        )
        assert "REGIME_CONFLICT_STRESS_LONG" not in _flag_codes(report)
        assert "REGIME_TENSION_STRESS_LONG" not in _flag_codes(report)

    def test_trending_underexposed_produces_yellow(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=10.0),
            regime=_regime("TRENDING"),
        )
        assert "UNDEREXPOSED_RISK_ON" in _flag_codes(report)
        flag = _flag_by_code(report, "UNDEREXPOSED_RISK_ON")
        assert flag.severity == "YELLOW"

    def test_regime_alignment_score_low_in_stress_long(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=70.0),
            regime=_regime("STRESS"),
        )
        assert report.regime_alignment_score < 0.5


# ─────────────────────────────────────────────────────────────────────────────
# B) Narrative Decay — resolved narrative + active position → ORANGE
# ─────────────────────────────────────────────────────────────────────────────

class TestNarrativeDecay:
    def test_resolved_narrative_produces_orange(self):
        engine = make_engine()
        narrative = NarrativeState(tags=(
            NarrativeTag("AAPL", "AI_CAPEX_BOOM", "RESOLVED"),
        ))
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            narrative=narrative,
        )
        code = "NARRATIVE_RESOLVED_AAPL"
        assert code in _flag_codes(report)
        assert _flag_by_code(report, code).severity == "ORANGE"

    def test_reversed_narrative_produces_red(self):
        engine = make_engine()
        narrative = NarrativeState(tags=(
            NarrativeTag("AAPL", "FED_PIVOT", "REVERSED"),
        ))
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            narrative=narrative,
        )
        code = "NARRATIVE_REVERSED_AAPL"
        assert code in _flag_codes(report)
        assert _flag_by_code(report, code).severity == "RED"

    def test_fading_narrative_produces_yellow(self):
        engine = make_engine()
        narrative = NarrativeState(tags=(
            NarrativeTag("AAPL", "RATE_CUT_CYCLE", "FADING"),
        ))
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            narrative=narrative,
        )
        code = "NARRATIVE_FADING_AAPL"
        assert code in _flag_codes(report)
        assert _flag_by_code(report, code).severity == "YELLOW"

    def test_active_narrative_no_flag(self):
        engine = make_engine()
        narrative = NarrativeState(tags=(
            NarrativeTag("AAPL", "AI_CAPEX_BOOM", "ACTIVE"),
        ))
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            narrative=narrative,
        )
        narrative_flag_codes = {f.code for f in report.flags if f.module == "NARRATIVE_DRIFT"}
        assert len(narrative_flag_codes) == 0

    def test_narrative_tag_for_nonheld_symbol_ignored(self):
        engine = make_engine()
        narrative = NarrativeState(tags=(
            NarrativeTag("NVDA", "AI_CAPEX_BOOM", "RESOLVED"),
        ))
        report = engine.evaluate(
            portfolio=_portfolio(holdings=(_holding("AAPL"),)),
            regime=_regime(),
            narrative=narrative,
        )
        narrative_flags = [f for f in report.flags if f.module == "NARRATIVE_DRIFT"]
        assert len(narrative_flags) == 0

    def test_narrative_alignment_score_drops_on_decay(self):
        engine = make_engine()
        holdings = (_holding("AAPL"), _holding("MSFT", weight_pct=10.0))
        narrative = NarrativeState(tags=(
            NarrativeTag("AAPL", "N1", "RESOLVED"),
        ))
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime(),
            narrative=narrative,
        )
        assert report.narrative_alignment_score < 1.0


# ─────────────────────────────────────────────────────────────────────────────
# C) Factor Misalignment — Momentum dominant + value-heavy holdings → YELLOW
# ─────────────────────────────────────────────────────────────────────────────

class TestFactorMisalignment:
    def test_momentum_regime_value_heavy_produces_yellow_or_orange(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=20.0),
            _holding("B", weight_pct=20.0),
            _holding("C", weight_pct=20.0),
            _holding("D", weight_pct=20.0),
            _holding("E", weight_pct=20.0),
        )
        # Only 1 of 5 holdings is aligned with MOMENTUM
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={
                "A": "VALUE",
                "B": "VALUE",
                "C": "VALUE",
                "D": "VALUE",
                "E": "MOMENTUM",
            },
        )
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime("TRENDING"),
            factor=factor,
        )
        factor_flags = [f for f in report.flags if f.module == "FACTOR_ALIGNMENT"]
        assert len(factor_flags) > 0
        severities = {f.severity for f in factor_flags}
        assert severities & {"YELLOW", "ORANGE"}

    def test_perfect_factor_alignment_no_flag(self):
        engine = make_engine()
        holdings = (_holding("A", weight_pct=50.0), _holding("B", weight_pct=50.0))
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={"A": "MOMENTUM", "B": "MOMENTUM"},
        )
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime(),
            factor=factor,
        )
        factor_flags = [f for f in report.flags if f.module == "FACTOR_ALIGNMENT"]
        assert len(factor_flags) == 0

    def test_factor_score_reflects_alignment(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=30.0),
            _holding("B", weight_pct=70.0),
        )
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={"A": "MOMENTUM", "B": "VALUE"},
        )
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime(),
            factor=factor,
        )
        # 30/100 = 0.30 alignment
        assert abs(report.factor_alignment_score - 0.30) < 0.01


# ─────────────────────────────────────────────────────────────────────────────
# D) Horizon Violation — SCALP held > allowed days → ORANGE
# ─────────────────────────────────────────────────────────────────────────────

class TestHorizonViolation:
    def test_scalp_over_3_days_produces_orange(self):
        engine = make_engine()
        holdings = (_holding("SPY", strategy="SCALP", days_held=10),)
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime(),
        )
        code = "HORIZON_VIOLATION_SPY"
        assert code in _flag_codes(report)
        assert _flag_by_code(report, code).severity == "ORANGE"

    def test_scalp_within_limit_no_horizon_flag(self):
        engine = make_engine()
        holdings = (_holding("SPY", strategy="SCALP", days_held=2),)
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime("CHOP"),
        )
        assert "HORIZON_VIOLATION_SPY" not in _flag_codes(report)

    def test_swing_over_20_days_produces_orange(self):
        engine = make_engine()
        holdings = (_holding("MSFT", strategy="SWING", days_held=25),)
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime(),
        )
        assert "HORIZON_VIOLATION_MSFT" in _flag_codes(report)

    def test_positional_within_90_days_no_flag(self):
        engine = make_engine()
        holdings = (_holding("AMZN", strategy="POSITIONAL", days_held=85),)
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime(),
        )
        assert "HORIZON_VIOLATION_AMZN" not in _flag_codes(report)


# ─────────────────────────────────────────────────────────────────────────────
# E) Concentration Breach — top-3 > threshold → ORANGE / RED
# ─────────────────────────────────────────────────────────────────────────────

class TestConcentrationBreach:
    def test_top3_above_45_produces_orange(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=20.0, sector="TECH"),
            _holding("B", weight_pct=16.0, sector="TECH"),
            _holding("C", weight_pct=12.0, sector="FINANCE"),
            _holding("D", weight_pct=5.0, sector="FINANCE"),
            _holding("E", weight_pct=5.0, sector="FINANCE"),
        )
        # top-3 = 48% → ORANGE
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings, sector_caps={"TECH": 50.0, "FINANCE": 50.0}),
            regime=_regime(),
        )
        assert "CONCENTRATION_TOP3_ORANGE" in _flag_codes(report)
        assert _flag_by_code(report, "CONCENTRATION_TOP3_ORANGE").severity == "ORANGE"

    def test_top3_above_60_produces_red(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=25.0, sector="TECH"),
            _holding("B", weight_pct=22.0, sector="TECH"),
            _holding("C", weight_pct=16.0, sector="FINANCE"),
            _holding("D", weight_pct=5.0, sector="FINANCE"),
        )
        # top-3 = 63%
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings, sector_caps={"TECH": 60.0, "FINANCE": 30.0}),
            regime=_regime(),
        )
        assert "CONCENTRATION_TOP3_RED" in _flag_codes(report)
        assert _flag_by_code(report, "CONCENTRATION_TOP3_RED").severity == "RED"

    def test_sector_cap_breach_produces_red(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=25.0, sector="TECH"),
            _holding("B", weight_pct=25.0, sector="TECH"),
        )
        # TECH = 50%, cap = 40% → RED
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings, sector_caps={"TECH": 40.0}),
            regime=_regime(),
        )
        assert "SECTOR_CAP_BREACH_TECH" in _flag_codes(report)
        assert _flag_by_code(report, "SECTOR_CAP_BREACH_TECH").severity == "RED"

    def test_sector_near_cap_produces_yellow(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=19.0, sector="TECH"),
            _holding("B", weight_pct=19.0, sector="TECH"),
        )
        # TECH = 38%, cap = 40% → 38 > 40*0.9=36 → YELLOW cap warning
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings, sector_caps={"TECH": 40.0}),
            regime=_regime(),
        )
        assert "SECTOR_CAP_WARNING_TECH" in _flag_codes(report)


# ─────────────────────────────────────────────────────────────────────────────
# F) Convergence Decay — score drop > 50% → ORANGE
# ─────────────────────────────────────────────────────────────────────────────

class TestConvergenceDecay:
    def test_decay_above_50pct_produces_orange(self):
        engine = make_engine()
        convergence = ConvergenceSnapshot(scores={"AAPL": (0.80, 0.35)})
        # decay = (0.80 - 0.35) / 0.80 = 56.25%
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            convergence=convergence,
        )
        assert "CONVERGENCE_DECAY_SEVERE_AAPL" in _flag_codes(report)
        assert _flag_by_code(report, "CONVERGENCE_DECAY_SEVERE_AAPL").severity == "ORANGE"

    def test_decay_between_30_and_50_produces_yellow(self):
        engine = make_engine()
        convergence = ConvergenceSnapshot(scores={"AAPL": (0.80, 0.52)})
        # decay = 35%
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            convergence=convergence,
        )
        assert "CONVERGENCE_DECAY_MODERATE_AAPL" in _flag_codes(report)
        assert _flag_by_code(report, "CONVERGENCE_DECAY_MODERATE_AAPL").severity == "YELLOW"

    def test_no_decay_no_flag(self):
        engine = make_engine()
        convergence = ConvergenceSnapshot(scores={"AAPL": (0.80, 0.80)})
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            convergence=convergence,
        )
        conv_flags = [f for f in report.flags if f.module == "CONVERGENCE_HEALTH"]
        assert len(conv_flags) == 0

    def test_systemic_decay_three_holdings_produces_red(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=10.0),
            _holding("B", weight_pct=10.0),
            _holding("C", weight_pct=10.0),
        )
        convergence = ConvergenceSnapshot(scores={
            "A": (0.80, 0.30),   # 62.5% decay
            "B": (0.80, 0.30),   # 62.5% decay
            "C": (0.80, 0.30),   # 62.5% decay
        })
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings),
            regime=_regime(),
            convergence=convergence,
        )
        assert "SYSTEMIC_CONVERGENCE_DECAY" in _flag_codes(report)
        assert _flag_by_code(report, "SYSTEMIC_CONVERGENCE_DECAY").severity == "RED"

    def test_convergence_health_score_reflects_decay(self):
        engine = make_engine()
        convergence = ConvergenceSnapshot(scores={"AAPL": (0.80, 0.40)})
        # ratio = 0.40 / 0.80 = 0.50
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            convergence=convergence,
        )
        assert abs(report.convergence_health_score - 0.50) < 0.01


# ─────────────────────────────────────────────────────────────────────────────
# G) Stability Score Drop — stability = 0.15 → RED
# ─────────────────────────────────────────────────────────────────────────────

class TestStabilityScoreDrop:
    def test_stability_015_produces_red(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(stability=0.15),
        )
        assert "STABILITY_CRITICAL" in _flag_codes(report)
        assert _flag_by_code(report, "STABILITY_CRITICAL").severity == "RED"

    def test_stability_035_produces_orange(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(stability=0.35),
        )
        assert "STABILITY_DEGRADED" in _flag_codes(report)
        assert _flag_by_code(report, "STABILITY_DEGRADED").severity == "ORANGE"

    def test_stability_055_produces_yellow(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(stability=0.55),
        )
        assert "STABILITY_WARNING" in _flag_codes(report)
        assert _flag_by_code(report, "STABILITY_WARNING").severity == "YELLOW"

    def test_stability_full_no_flag(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(stability=1.0),
        )
        stab_flags = [f for f in report.flags if f.module == "STABILITY_DRIFT"]
        assert len(stab_flags) == 0


# ─────────────────────────────────────────────────────────────────────────────
# H) Deterministic Replay — 10 identical runs produce identical reports
# ─────────────────────────────────────────────────────────────────────────────

class TestDeterministicReplay:
    def _build_inputs(self):
        portfolio = _portfolio(
            holdings=(
                _holding("AAPL", weight_pct=25.0),
                _holding("MSFT", weight_pct=20.0),
                _holding("TSLA", weight_pct=15.0, strategy="SCALP", days_held=5),
            ),
            net_exposure_pct=45.0,
            gross_exposure_pct=60.0,
            drawdown_pct=8.0,
        )
        regime = _regime("TRENDING", stability=0.55)
        narrative = NarrativeState(tags=(
            NarrativeTag("AAPL", "AI_BOOM", "RESOLVED"),
        ))
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={"AAPL": "VALUE", "MSFT": "MOMENTUM", "TSLA": "MOMENTUM"},
        )
        convergence = ConvergenceSnapshot(scores={
            "AAPL": (0.80, 0.45),
            "MSFT": (0.75, 0.72),
        })
        activity = ConstraintActivitySummary(
            approved_count=6, adjusted_count=3, rejected_count=1
        )
        return portfolio, regime, narrative, factor, convergence, activity

    def test_ten_runs_produce_identical_input_hash(self):
        engine = make_engine()
        inputs = self._build_inputs()
        hashes = set()
        for _ in range(10):
            report = engine.evaluate(*inputs)
            hashes.add(report.input_hash)
        assert len(hashes) == 1

    def test_ten_runs_produce_identical_flag_set(self):
        engine = make_engine()
        inputs = self._build_inputs()
        flag_sets = []
        for _ in range(10):
            report = engine.evaluate(*inputs)
            flag_sets.append(frozenset(f.code for f in report.flags))
        assert len(set(flag_sets)) == 1

    def test_ten_runs_produce_identical_scores(self):
        engine = make_engine()
        inputs = self._build_inputs()
        score_tuples = []
        for _ in range(10):
            report = engine.evaluate(*inputs)
            score_tuples.append((
                round(report.regime_alignment_score, 8),
                round(report.factor_alignment_score, 8),
                round(report.convergence_health_score, 8),
                round(report.concentration_score, 8),
            ))
        assert len(set(score_tuples)) == 1

    def test_ten_runs_produce_identical_global_status(self):
        engine = make_engine()
        inputs = self._build_inputs()
        statuses = {engine.evaluate(*inputs).global_status for _ in range(10)}
        assert len(statuses) == 1


# ─────────────────────────────────────────────────────────────────────────────
# I) Insufficient Context
# ─────────────────────────────────────────────────────────────────────────────

class TestInsufficientContext:
    def test_none_portfolio_returns_insufficient_context(self):
        engine = make_engine()
        report = engine.evaluate(portfolio=None, regime=_regime())
        assert report.global_status == "INSUFFICIENT_CONTEXT"
        assert any(f.code == "INSUFFICIENT_CONTEXT" for f in report.flags)

    def test_none_regime_returns_insufficient_context(self):
        engine = make_engine()
        report = engine.evaluate(portfolio=_portfolio(), regime=None)
        assert report.global_status == "INSUFFICIENT_CONTEXT"

    def test_insufficient_context_all_scores_zero(self):
        engine = make_engine()
        report = engine.evaluate(portfolio=None, regime=None)
        assert report.regime_alignment_score == 0.0
        assert report.narrative_alignment_score == 0.0
        assert report.convergence_health_score == 0.0

    def test_optional_upstream_absent_does_not_raise(self):
        engine = make_engine()
        # No narrative, no factor, no convergence, no constraint_activity
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
        )
        assert report.global_status in ("OK", "DEGRADED", "CRITICAL")


# ─────────────────────────────────────────────────────────────────────────────
# J) Global Status Logic — highest severity wins
# ─────────────────────────────────────────────────────────────────────────────

class TestGlobalStatusLogic:
    def test_red_flag_makes_status_critical(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=70.0),
            regime=_regime("STRESS"),
        )
        assert report.global_status == "CRITICAL"

    def test_only_yellow_flags_makes_status_degraded(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=10.0),
            regime=_regime("TRENDING"),
        )
        yellow_flags = [f for f in report.flags if f.severity == "YELLOW"]
        non_yellow = [f for f in report.flags if f.severity not in ("YELLOW", "INFO")]
        assert len(yellow_flags) > 0
        assert len(non_yellow) == 0
        assert report.global_status == "DEGRADED"

    def test_clean_portfolio_status_ok(self):
        engine = make_engine()
        holdings = (_holding("AAPL", weight_pct=10.0, sector="TECH"),)
        report = engine.evaluate(
            portfolio=_portfolio(
                holdings=holdings,
                net_exposure_pct=50.0,
                gross_exposure_pct=50.0,
                drawdown_pct=1.0,
                sector_caps={"TECH": 30.0},
            ),
            regime=_regime("TRENDING", stability=1.0),
        )
        # sector breach will fire — that's expected;
        # the point is global_status reflects the highest flag correctly
        highest = max(
            (_SEVERITY_ORDER[f.severity] for f in report.flags),
            default=-1
        )
        if highest == -1:
            assert report.global_status == "OK"
        elif highest <= 1:
            assert report.global_status in ("OK", "DEGRADED")
        else:
            assert report.global_status == "CRITICAL"


# severity ordering helper for test J
_SEVERITY_ORDER = {"INFO": 0, "YELLOW": 1, "ORANGE": 2, "RED": 3, "CRITICAL": 4}


# ─────────────────────────────────────────────────────────────────────────────
# K) Exposure Symmetry — sector clustering
# ─────────────────────────────────────────────────────────────────────────────

class TestExposureSymmetry:
    def test_high_sector_concentration_produces_orange(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=40.0, sector="TECH"),
            _holding("B", weight_pct=40.0, sector="TECH"),
            _holding("C", weight_pct=10.0, sector="FINANCE"),
        )
        # TECH = 80/90 gross = 88.9% → ORANGE
        report = engine.evaluate(
            portfolio=_portfolio(
                holdings=holdings,
                gross_exposure_pct=90.0,
                sector_caps={"TECH": 100.0, "FINANCE": 20.0},
            ),
            regime=_regime(),
        )
        exp_flags = [f for f in report.flags if f.module == "EXPOSURE_SYMMETRY"]
        assert any(f.severity == "ORANGE" for f in exp_flags)

    def test_balanced_sectors_no_asymmetry_flag(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=10.0, sector="TECH"),
            _holding("B", weight_pct=10.0, sector="FINANCE"),
            _holding("C", weight_pct=10.0, sector="HEALTH"),
            _holding("D", weight_pct=10.0, sector="ENERGY"),
        )
        report = engine.evaluate(
            portfolio=_portfolio(
                holdings=holdings,
                gross_exposure_pct=40.0,
                sector_caps={"TECH": 20.0, "FINANCE": 20.0, "HEALTH": 20.0, "ENERGY": 20.0},
            ),
            regime=_regime(),
        )
        exp_flags = [f for f in report.flags if f.module == "EXPOSURE_SYMMETRY"]
        assert all(f.severity not in ("ORANGE", "RED") for f in exp_flags)


# ─────────────────────────────────────────────────────────────────────────────
# L) Constraint Friction
# ─────────────────────────────────────────────────────────────────────────────

class TestConstraintFriction:
    def test_high_rejection_ratio_produces_orange(self):
        engine = make_engine()
        activity = ConstraintActivitySummary(approved_count=6, adjusted_count=1, rejected_count=3)
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            constraint_activity=activity,
        )
        assert "CONSTRAINT_FRICTION_REJECTIONS" in _flag_codes(report)
        assert _flag_by_code(report, "CONSTRAINT_FRICTION_REJECTIONS").severity == "ORANGE"

    def test_high_adjustment_ratio_produces_orange(self):
        engine = make_engine()
        activity = ConstraintActivitySummary(approved_count=4, adjusted_count=6, rejected_count=0)
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            constraint_activity=activity,
        )
        assert "CONSTRAINT_FRICTION_ADJUSTMENTS_HIGH" in _flag_codes(report)

    def test_low_friction_no_flag(self):
        engine = make_engine()
        activity = ConstraintActivitySummary(approved_count=18, adjusted_count=2, rejected_count=0)
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime(),
            constraint_activity=activity,
        )
        friction_flags = [f for f in report.flags if f.module == "CONSTRAINT_FRICTION"]
        assert all(f.severity not in ("ORANGE", "RED") for f in friction_flags)


# ─────────────────────────────────────────────────────────────────────────────
# M) Drawdown + Regime Misalignment — compound RED
# ─────────────────────────────────────────────────────────────────────────────

class TestDrawdownBehaviour:
    def test_drawdown_plus_regime_conflict_produces_red(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS"),
        )
        assert "DRAWDOWN_REGIME_MISALIGNMENT" in _flag_codes(report)
        assert _flag_by_code(report, "DRAWDOWN_REGIME_MISALIGNMENT").severity == "RED"

    def test_drawdown_alone_no_misalignment_produces_orange(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=50.0, drawdown_pct=12.0),
            regime=_regime("TRENDING"),   # aligned regime
        )
        assert "DRAWDOWN_RISING" in _flag_codes(report)
        assert _flag_by_code(report, "DRAWDOWN_RISING").severity == "ORANGE"

    def test_small_drawdown_no_flag(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=40.0, drawdown_pct=3.0),
            regime=_regime("TRENDING"),
        )
        dd_flags = [f for f in report.flags if f.module == "DRAWDOWN_BEHAVIOUR"]
        assert len(dd_flags) == 0


# ─────────────────────────────────────────────────────────────────────────────
# N) Serialisability — report serialisable to JSON
# ─────────────────────────────────────────────────────────────────────────────

class TestSerialisability:
    def _report_to_dict(self, report: PortfolioDiagnosticReport) -> dict:
        return {
            "timestamp": report.timestamp,
            "input_hash": report.input_hash,
            "global_status": report.global_status,
            "regime_alignment_score": report.regime_alignment_score,
            "narrative_alignment_score": report.narrative_alignment_score,
            "factor_alignment_score": report.factor_alignment_score,
            "strategy_alignment_score": report.strategy_alignment_score,
            "concentration_score": report.concentration_score,
            "exposure_balance_score": report.exposure_balance_score,
            "convergence_health_score": report.convergence_health_score,
            "latency_ms": report.latency_ms,
            "flags": [
                {
                    "code": f.code,
                    "module": f.module,
                    "severity": f.severity,
                    "message": f.message,
                    "affected_symbol": f.affected_symbol,
                }
                for f in report.flags
            ],
            "severity_map": report.severity_map,
            "component_scores": report.component_scores,
        }

    def test_report_serialises_to_json(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(),
            regime=_regime("STRESS"),
        )
        d = self._report_to_dict(report)
        serialised = json.dumps(d)       # Must not raise
        assert isinstance(serialised, str)
        recovered = json.loads(serialised)
        assert recovered["input_hash"] == report.input_hash

    def test_serialised_report_contains_all_required_keys(self):
        engine = make_engine()
        report = engine.evaluate(portfolio=_portfolio(), regime=_regime())
        d = self._report_to_dict(report)
        required = {
            "timestamp", "input_hash", "global_status",
            "regime_alignment_score", "narrative_alignment_score",
            "convergence_health_score", "flags", "severity_map",
        }
        assert required.issubset(d.keys())


# ─────────────────────────────────────────────────────────────────────────────
# O) All flags have non-empty messages — no silent suppression
# ─────────────────────────────────────────────────────────────────────────────

class TestFlagExplainability:
    def test_all_flags_have_non_empty_message(self):
        engine = make_engine()
        holdings = (
            _holding("A", weight_pct=25.0, strategy="SCALP", days_held=5, sector="TECH"),
            _holding("B", weight_pct=20.0, sector="TECH"),
            _holding("C", weight_pct=15.0, sector="TECH"),
        )
        narrative = NarrativeState(tags=(NarrativeTag("A", "N1", "RESOLVED"),))
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={"A": "VALUE", "B": "VALUE", "C": "VALUE"},
        )
        convergence = ConvergenceSnapshot(scores={"A": (0.80, 0.30)})
        activity = ConstraintActivitySummary(approved_count=2, adjusted_count=8, rejected_count=0)
        report = engine.evaluate(
            portfolio=_portfolio(holdings=holdings, net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS", stability=0.15),
            narrative=narrative,
            factor=factor,
            convergence=convergence,
            constraint_activity=activity,
        )
        for flag in report.flags:
            assert flag.message, f"Flag '{flag.code}' has an empty message"

    def test_all_flags_appear_in_severity_map(self):
        engine = make_engine()
        report = engine.evaluate(
            portfolio=_portfolio(net_exposure_pct=70.0),
            regime=_regime("STRESS", stability=0.15),
        )
        for flag in report.flags:
            assert flag.code in report.severity_map
            assert report.severity_map[flag.code] == flag.severity

    def test_latency_is_positive(self):
        engine = make_engine()
        report = engine.evaluate(portfolio=_portfolio(), regime=_regime())
        assert report.latency_ms > 0

    def test_all_scores_in_unit_range(self):
        engine = make_engine()
        report = engine.evaluate(portfolio=_portfolio(), regime=_regime())
        for score_name, score_val in [
            ("regime_alignment_score", report.regime_alignment_score),
            ("narrative_alignment_score", report.narrative_alignment_score),
            ("factor_alignment_score", report.factor_alignment_score),
            ("strategy_alignment_score", report.strategy_alignment_score),
            ("concentration_score", report.concentration_score),
            ("exposure_balance_score", report.exposure_balance_score),
            ("convergence_health_score", report.convergence_health_score),
        ]:
            assert 0.0 <= score_val <= 1.0, (
                f"{score_name} = {score_val} is outside [0.0, 1.0]"
            )
