"""
Test Suite — L10 Advisory Layer (src/layers/advisory_layer.py)
==============================================================
Tests are organised around the required scenarios from the specification,
plus invariant coverage, observability, and edge cases.

Required scenarios:
  A) Regime Conflict → Suggest De-risk
  B) Narrative Decay → Suggest Thesis Review
  C) Concentration Risk → Suggest Diversification
  D) Stability Low → Suggest Risk Tightening + HIGH system risk
  E) Deterministic Replay (10 runs)
  F) Confidence Boundaries [0.0, 1.0]

Additional:
  G) Factor Misalignment → Realignment suggestion
  H) Convergence Decay → Conviction recalibration suggestion
  I) Strategy Misuse → Reclassification suggestion
  J) Drawdown + misalignment → structural de-risk suggestion
  K) Constraint friction → Constraint commentary suggestion
  L) Insufficient diagnostic context → INSUFFICIENT_DIAGNOSTIC_CONTEXT
  M) Latency is positive
  N) Serialisability to JSON
  O) No execution language in suggestions
  P) All suggestions have non-empty rationale and action
  Q) Exposure symmetry → clustering suggestion
  R) System risk escalation logic
"""
from __future__ import annotations

import json
from typing import List, Optional, Tuple

import pytest

from src.layers.advisory_layer import AdvisoryLayer
from src.models.advisory_models import AdvisoryReport, AdvisorySuggestion
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
from src.layers.portfolio_intelligence import PortfolioIntelligenceEngine

# ── Helpers ────────────────────────────────────────────────────────────────────

def make_engine() -> PortfolioIntelligenceEngine:
    return PortfolioIntelligenceEngine()


def make_layer() -> AdvisoryLayer:
    return AdvisoryLayer()


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
    sector_caps=None,
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


def _regime(r: str = "TRENDING", volatility: float = 0.3, stability: float = 1.0) -> RegimeState:
    return RegimeState(regime=r, volatility=volatility, stability_score=stability)


def _l9(
    portfolio=None,
    regime=None,
    narrative=None,
    factor=None,
    convergence=None,
    constraint_activity=None,
) -> PortfolioDiagnosticReport:
    """Convenience: run L9 and return its report."""
    p = portfolio or _portfolio()
    r = regime or _regime()
    return make_engine().evaluate(p, r, narrative, factor, convergence, constraint_activity)


def _suggestion_categories(report: AdvisoryReport) -> set:
    all_s = (
        list(report.portfolio_suggestions)
        + list(report.position_suggestions)
        + list(report.risk_suggestions)
        + list(report.exposure_adjustments)
    )
    return {s.category for s in all_s}


def _all_suggestions(report: AdvisoryReport) -> List[AdvisorySuggestion]:
    return (
        list(report.portfolio_suggestions)
        + list(report.position_suggestions)
        + list(report.risk_suggestions)
        + list(report.exposure_adjustments)
    )


def _find(report: AdvisoryReport, category: str) -> List[AdvisorySuggestion]:
    return [s for s in _all_suggestions(report) if s.category == category]


# ─────────────────────────────────────────────────────────────────────────────
# A) Regime Conflict → Exposure De-risk Suggestion
# ─────────────────────────────────────────────────────────────────────────────

class TestRegimeConflictAdvisory:
    def test_stress_high_long_produces_exposure_suggestion(self):
        l9 = _l9(portfolio=_portfolio(net_exposure_pct=70.0), regime=_regime("STRESS"))
        report = make_layer().advise(l9)
        regime_sugg = _find(report, "REGIME_ADVISORY")
        assert len(regime_sugg) > 0

    def test_regime_suggestion_does_not_contain_buy_sell(self):
        l9 = _l9(portfolio=_portfolio(net_exposure_pct=70.0), regime=_regime("STRESS"))
        report = make_layer().advise(l9)
        for s in _find(report, "REGIME_ADVISORY"):
            assert "BUY" not in s.suggested_action.upper()
            assert "SELL" not in s.suggested_action.upper()

    def test_regime_conflict_suggestion_severity_red(self):
        l9 = _l9(portfolio=_portfolio(net_exposure_pct=70.0), regime=_regime("STRESS"))
        report = make_layer().advise(l9)
        regime_sugg = _find(report, "REGIME_ADVISORY")
        red_sugg = [s for s in regime_sugg if s.severity == "RED"]
        assert len(red_sugg) > 0

    def test_regime_conflict_linked_to_l9_flag(self):
        l9 = _l9(portfolio=_portfolio(net_exposure_pct=70.0), regime=_regime("STRESS"))
        report = make_layer().advise(l9)
        for s in _find(report, "REGIME_ADVISORY"):
            if s.severity == "RED":
                assert s.linked_flag == "REGIME_CONFLICT_STRESS_LONG"

    def test_underexposed_trending_produces_yellow_suggestion(self):
        l9 = _l9(portfolio=_portfolio(net_exposure_pct=10.0), regime=_regime("TRENDING"))
        report = make_layer().advise(l9)
        regime_sugg = _find(report, "REGIME_ADVISORY")
        assert any(s.severity == "YELLOW" for s in regime_sugg)


# ─────────────────────────────────────────────────────────────────────────────
# B) Narrative Decay → Thesis Review Suggestion
# ─────────────────────────────────────────────────────────────────────────────

class TestNarrativeAdvisory:
    def test_resolved_narrative_produces_thesis_review_suggestion(self):
        narrative = NarrativeState(tags=(NarrativeTag("AAPL", "AI_CAPEX_BOOM", "RESOLVED"),))
        l9 = _l9(narrative=narrative)
        report = make_layer().advise(l9)
        narr_sugg = _find(report, "NARRATIVE_ADVISORY")
        assert len(narr_sugg) > 0

    def test_narrative_suggestion_severity_orange_for_resolved(self):
        narrative = NarrativeState(tags=(NarrativeTag("AAPL", "AI_CAPEX_BOOM", "RESOLVED"),))
        l9 = _l9(narrative=narrative)
        report = make_layer().advise(l9)
        narr_sugg = _find(report, "NARRATIVE_ADVISORY")
        assert any(s.severity == "ORANGE" for s in narr_sugg)

    def test_reversed_narrative_produces_red_suggestion(self):
        narrative = NarrativeState(tags=(NarrativeTag("AAPL", "FED_PIVOT", "REVERSED"),))
        l9 = _l9(narrative=narrative)
        report = make_layer().advise(l9)
        narr_sugg = _find(report, "NARRATIVE_ADVISORY")
        assert any(s.severity == "RED" for s in narr_sugg)

    def test_narrative_suggestion_symbol_tagged(self):
        narrative = NarrativeState(tags=(NarrativeTag("AAPL", "AI_CAPEX_BOOM", "RESOLVED"),))
        l9 = _l9(narrative=narrative)
        report = make_layer().advise(l9)
        for s in _find(report, "NARRATIVE_ADVISORY"):
            assert s.affected_symbol == "AAPL"

    def test_active_narrative_no_suggestion(self):
        narrative = NarrativeState(tags=(NarrativeTag("AAPL", "AI_BOOM", "ACTIVE"),))
        l9 = _l9(narrative=narrative)
        report = make_layer().advise(l9)
        assert len(_find(report, "NARRATIVE_ADVISORY")) == 0


# ─────────────────────────────────────────────────────────────────────────────
# C) Concentration Risk → Diversification Suggestion
# ─────────────────────────────────────────────────────────────────────────────

class TestConcentrationAdvisory:
    def test_top3_above_threshold_produces_diversification_suggestion(self):
        holdings = (
            _holding("A", weight_pct=20.0, sector="TECH"),
            _holding("B", weight_pct=16.0, sector="TECH"),
            _holding("C", weight_pct=12.0, sector="FINANCE"),
            _holding("D", weight_pct=5.0, sector="FINANCE"),
        )
        # top-3 = 48% → ORANGE
        l9 = _l9(
            portfolio=_portfolio(
                holdings=holdings,
                sector_caps={"TECH": 50.0, "FINANCE": 30.0},
            )
        )
        report = make_layer().advise(l9)
        conc_sugg = _find(report, "CONCENTRATION_ADVISORY")
        assert len(conc_sugg) > 0

    def test_concentration_suggestion_mentions_diversification(self):
        holdings = (
            _holding("A", weight_pct=22.0, sector="TECH"),
            _holding("B", weight_pct=15.0, sector="TECH"),
            _holding("C", weight_pct=12.0, sector="FINANCE"),
        )
        l9 = _l9(
            portfolio=_portfolio(
                holdings=holdings,
                sector_caps={"TECH": 50.0, "FINANCE": 30.0},
            )
        )
        report = make_layer().advise(l9)
        for s in _find(report, "CONCENTRATION_ADVISORY"):
            assert "diversi" in s.suggested_action.lower() or "concentr" in s.suggested_action.lower()

    def test_sector_cap_breach_produces_suggestion(self):
        holdings = (
            _holding("A", weight_pct=25.0, sector="TECH"),
            _holding("B", weight_pct=25.0, sector="TECH"),
        )
        l9 = _l9(
            portfolio=_portfolio(holdings=holdings, sector_caps={"TECH": 40.0})
        )
        report = make_layer().advise(l9)
        conc_sugg = _find(report, "CONCENTRATION_ADVISORY")
        assert len(conc_sugg) > 0


# ─────────────────────────────────────────────────────────────────────────────
# D) Stability Low → Risk Tightening + HIGH system risk
# ─────────────────────────────────────────────────────────────────────────────

class TestStabilityAdvisory:
    def test_stability_02_produces_systemic_risk_level(self):
        l9 = _l9(regime=_regime(stability=0.15))
        report = make_layer().advise(l9)
        assert report.system_risk_level == "SYSTEMIC_RISK"

    def test_stability_035_produces_high_system_risk(self):
        l9 = _l9(regime=_regime(stability=0.35))
        report = make_layer().advise(l9)
        assert report.system_risk_level in ("HIGH", "SYSTEMIC_RISK")

    def test_stability_low_produces_stability_escalation_suggestion(self):
        l9 = _l9(regime=_regime(stability=0.20))
        report = make_layer().advise(l9)
        stab_sugg = _find(report, "STABILITY_ESCALATION")
        assert len(stab_sugg) > 0

    def test_stability_suggestion_does_not_say_reduce_position(self):
        """Should say 'consider reducing sizing aggressiveness', not 'reduce position X'."""
        l9 = _l9(regime=_regime(stability=0.15))
        report = make_layer().advise(l9)
        for s in _find(report, "STABILITY_ESCALATION"):
            text = s.suggested_action.upper()
            assert "SHARES" not in text
            assert "UNITS" not in text

    def test_stability_full_no_escalation_suggestion(self):
        l9 = _l9(regime=_regime(stability=1.0))
        report = make_layer().advise(l9)
        assert len(_find(report, "STABILITY_ESCALATION")) == 0


# ─────────────────────────────────────────────────────────────────────────────
# E) Deterministic Replay — 10 identical runs → identical report
# ─────────────────────────────────────────────────────────────────────────────

class TestDeterministicReplay:
    def _build_l9(self) -> PortfolioDiagnosticReport:
        holdings = (
            _holding("AAPL", weight_pct=22.0, strategy="SCALP", days_held=5, sector="TECH"),
            _holding("MSFT", weight_pct=18.0, sector="TECH"),
            _holding("TSLA", weight_pct=15.0, sector="AUTO"),
        )
        narrative = NarrativeState(tags=(NarrativeTag("AAPL", "AI_BOOM", "RESOLVED"),))
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={"AAPL": "VALUE", "MSFT": "MOMENTUM", "TSLA": "VALUE"},
        )
        convergence = ConvergenceSnapshot(scores={"AAPL": (0.80, 0.35)})
        activity = ConstraintActivitySummary(approved_count=5, adjusted_count=3, rejected_count=2)
        return make_engine().evaluate(
            portfolio=_portfolio(
                holdings=holdings,
                net_exposure_pct=55.0,
                gross_exposure_pct=70.0,
                drawdown_pct=8.0,
                sector_caps={"TECH": 50.0, "AUTO": 25.0},
            ),
            regime=_regime("STRESS", stability=0.55),
            narrative=narrative,
            factor=factor,
            convergence=convergence,
            constraint_activity=activity,
        )

    def test_ten_runs_identical_input_hash(self):
        layer = make_layer()
        l9 = self._build_l9()
        hashes = {layer.advise(l9).input_hash for _ in range(10)}
        assert len(hashes) == 1

    def test_ten_runs_identical_confidence(self):
        layer = make_layer()
        l9 = self._build_l9()
        confs = {round(layer.advise(l9).confidence_score, 8) for _ in range(10)}
        assert len(confs) == 1

    def test_ten_runs_identical_system_risk_level(self):
        layer = make_layer()
        l9 = self._build_l9()
        levels = {layer.advise(l9).system_risk_level for _ in range(10)}
        assert len(levels) == 1

    def test_ten_runs_identical_suggestion_count(self):
        layer = make_layer()
        l9 = self._build_l9()
        counts = {len(_all_suggestions(layer.advise(l9))) for _ in range(10)}
        assert len(counts) == 1

    def test_ten_runs_identical_suggestion_categories(self):
        layer = make_layer()
        l9 = self._build_l9()
        cat_sets = {
            frozenset(s.category for s in _all_suggestions(layer.advise(l9)))
            for _ in range(10)
        }
        assert len(cat_sets) == 1


# ─────────────────────────────────────────────────────────────────────────────
# F) Confidence Boundaries [0.0, 1.0]
# ─────────────────────────────────────────────────────────────────────────────

class TestConfidenceBoundaries:
    def test_confidence_at_least_zero_clean_portfolio(self):
        l9 = _l9()
        report = make_layer().advise(l9)
        assert report.confidence_score >= 0.0

    def test_confidence_at_most_one_clean_portfolio(self):
        l9 = _l9()
        report = make_layer().advise(l9)
        assert report.confidence_score <= 1.0

    def test_confidence_at_least_zero_stress_portfolio(self):
        l9 = _l9(
            portfolio=_portfolio(net_exposure_pct=80.0, drawdown_pct=20.0),
            regime=_regime("STRESS", stability=0.10),
        )
        report = make_layer().advise(l9)
        assert report.confidence_score >= 0.0

    def test_confidence_at_most_one_stress_portfolio(self):
        l9 = _l9(
            portfolio=_portfolio(net_exposure_pct=80.0, drawdown_pct=20.0),
            regime=_regime("STRESS", stability=0.10),
        )
        report = make_layer().advise(l9)
        assert report.confidence_score <= 1.0

    def test_confidence_lower_under_stress_than_clean(self):
        l9_clean = _l9(regime=_regime("TRENDING", stability=1.0))
        l9_stress = _l9(
            portfolio=_portfolio(net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS", stability=0.15),
        )
        clean_conf = make_layer().advise(l9_clean).confidence_score
        stress_conf = make_layer().advise(l9_stress).confidence_score
        assert stress_conf < clean_conf


# ─────────────────────────────────────────────────────────────────────────────
# G) Factor Misalignment → Realignment Suggestion
# ─────────────────────────────────────────────────────────────────────────────

class TestFactorAdvisory:
    def test_factor_misalignment_produces_suggestion(self):
        holdings = (
            _holding("A", weight_pct=20.0),
            _holding("B", weight_pct=20.0),
            _holding("C", weight_pct=20.0),
            _holding("D", weight_pct=20.0),
            _holding("E", weight_pct=20.0),
        )
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={k: "VALUE" for k in "ABCDE"},
        )
        l9 = _l9(
            portfolio=_portfolio(holdings=holdings),
            factor=factor,
        )
        report = make_layer().advise(l9)
        assert len(_find(report, "FACTOR_REALIGNMENT")) > 0

    def test_perfect_factor_alignment_no_suggestion(self):
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={"AAPL": "MOMENTUM"},
        )
        l9 = _l9(factor=factor)
        report = make_layer().advise(l9)
        assert len(_find(report, "FACTOR_REALIGNMENT")) == 0


# ─────────────────────────────────────────────────────────────────────────────
# H) Convergence Decay → Conviction Recalibration Suggestion
# ─────────────────────────────────────────────────────────────────────────────

class TestConvergenceDecayAdvisory:
    def test_decay_above_50pct_produces_conviction_suggestion(self):
        convergence = ConvergenceSnapshot(scores={"AAPL": (0.80, 0.35)})
        l9 = _l9(convergence=convergence)
        report = make_layer().advise(l9)
        conv_sugg = _find(report, "CONVERGENCE_DECAY")
        assert len(conv_sugg) > 0

    def test_conviction_suggestion_severity_orange(self):
        convergence = ConvergenceSnapshot(scores={"AAPL": (0.80, 0.35)})
        l9 = _l9(convergence=convergence)
        report = make_layer().advise(l9)
        conv_sugg = _find(report, "CONVERGENCE_DECAY")
        assert any(s.severity == "ORANGE" for s in conv_sugg)

    def test_systemic_convergence_decay_produces_red(self):
        holdings = (
            _holding("A", weight_pct=10.0),
            _holding("B", weight_pct=10.0),
            _holding("C", weight_pct=10.0),
        )
        convergence = ConvergenceSnapshot(scores={
            "A": (0.80, 0.30),
            "B": (0.80, 0.30),
            "C": (0.80, 0.30),
        })
        l9 = _l9(
            portfolio=_portfolio(holdings=holdings),
            convergence=convergence,
        )
        report = make_layer().advise(l9)
        conv_sugg = _find(report, "CONVERGENCE_DECAY")
        assert any(s.severity == "RED" for s in conv_sugg)


# ─────────────────────────────────────────────────────────────────────────────
# I) Strategy Misuse → Reclassification Suggestion
# ─────────────────────────────────────────────────────────────────────────────

class TestStrategyMisuseAdvisory:
    def test_scalp_over_days_produces_suggestion(self):
        holdings = (_holding("SPY", strategy="SCALP", days_held=10),)
        l9 = _l9(portfolio=_portfolio(holdings=holdings))
        report = make_layer().advise(l9)
        strat_sugg = _find(report, "STRATEGY_MISUSE")
        assert len(strat_sugg) > 0

    def test_strategy_suggestion_symbol_tagged(self):
        holdings = (_holding("SPY", strategy="SCALP", days_held=10),)
        l9 = _l9(portfolio=_portfolio(holdings=holdings))
        report = make_layer().advise(l9)
        for s in _find(report, "STRATEGY_MISUSE"):
            if s.linked_flag and "HORIZON_VIOLATION" in s.linked_flag:
                assert s.affected_symbol == "SPY"

    def test_normal_strategy_no_misuse_suggestion(self):
        holdings = (_holding("AAPL", strategy="SWING", days_held=5),)
        l9 = _l9(portfolio=_portfolio(holdings=holdings), regime=_regime("TRENDING"))
        report = make_layer().advise(l9)
        horizon_sugg = [
            s for s in _find(report, "STRATEGY_MISUSE")
            if s.linked_flag and "HORIZON_VIOLATION" in s.linked_flag
        ]
        assert len(horizon_sugg) == 0


# ─────────────────────────────────────────────────────────────────────────────
# J) Drawdown + Misalignment → Structural Suggestion
# ─────────────────────────────────────────────────────────────────────────────

class TestDrawdownAdvisory:
    def test_drawdown_regime_conflict_produces_structural_suggestion(self):
        l9 = _l9(
            portfolio=_portfolio(net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS"),
        )
        report = make_layer().advise(l9)
        dd_sugg = _find(report, "DRAWDOWN_ADVISORY")
        assert len(dd_sugg) > 0

    def test_drawdown_misalignment_suggestion_severity_red(self):
        l9 = _l9(
            portfolio=_portfolio(net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS"),
        )
        report = make_layer().advise(l9)
        dd_sugg = _find(report, "DRAWDOWN_ADVISORY")
        assert any(s.severity == "RED" for s in dd_sugg)

    def test_small_drawdown_no_suggestion(self):
        l9 = _l9(portfolio=_portfolio(drawdown_pct=2.0), regime=_regime("TRENDING"))
        report = make_layer().advise(l9)
        assert len(_find(report, "DRAWDOWN_ADVISORY")) == 0


# ─────────────────────────────────────────────────────────────────────────────
# K) Constraint Friction → Advisory
# ─────────────────────────────────────────────────────────────────────────────

class TestConstraintFrictionAdvisory:
    def test_high_friction_produces_suggestion(self):
        activity = ConstraintActivitySummary(approved_count=4, adjusted_count=6, rejected_count=0)
        l9 = _l9(constraint_activity=activity)
        report = make_layer().advise(l9)
        assert len(_find(report, "CONSTRAINT_FRICTION")) > 0

    def test_low_friction_no_suggestion(self):
        activity = ConstraintActivitySummary(approved_count=18, adjusted_count=1, rejected_count=0)
        l9 = _l9(constraint_activity=activity)
        report = make_layer().advise(l9)
        fric_sugg = _find(report, "CONSTRAINT_FRICTION")
        assert all(s.severity not in ("ORANGE", "RED") for s in fric_sugg)


# ─────────────────────────────────────────────────────────────────────────────
# L) Insufficient Diagnostic Context
# ─────────────────────────────────────────────────────────────────────────────

class TestInsufficientContext:
    def test_none_report_returns_insufficient_context(self):
        report = make_layer().advise(None)
        assert report.system_risk_level == "INSUFFICIENT_DIAGNOSTIC_CONTEXT"

    def test_insufficient_context_zero_confidence(self):
        report = make_layer().advise(None)
        assert report.confidence_score == 0.0

    def test_insufficient_context_no_suggestions(self):
        report = make_layer().advise(None)
        assert len(_all_suggestions(report)) == 0

    def test_l9_insufficient_context_report_propagates(self):
        # L9 report that is itself INSUFFICIENT_CONTEXT
        l9 = make_engine().evaluate(portfolio=None, regime=None)
        assert l9.global_status == "INSUFFICIENT_CONTEXT"
        report = make_layer().advise(l9)
        assert report.system_risk_level == "INSUFFICIENT_DIAGNOSTIC_CONTEXT"

    def test_insufficient_context_summary_is_non_empty(self):
        report = make_layer().advise(None)
        assert len(report.recommendation_summary) > 0


# ─────────────────────────────────────────────────────────────────────────────
# M) Latency
# ─────────────────────────────────────────────────────────────────────────────

class TestLatency:
    def test_latency_is_positive(self):
        l9 = _l9()
        report = make_layer().advise(l9)
        assert report.latency_ms > 0

    def test_latency_below_1000ms(self):
        l9 = _l9()
        report = make_layer().advise(l9)
        assert report.latency_ms < 1_000.0


# ─────────────────────────────────────────────────────────────────────────────
# N) Serialisability
# ─────────────────────────────────────────────────────────────────────────────

class TestSerialisability:
    def _to_dict(self, report: AdvisoryReport) -> dict:
        def sugg_list(suggs):
            return [
                {
                    "category": s.category,
                    "severity": s.severity,
                    "rationale": s.rationale,
                    "suggested_action": s.suggested_action,
                    "confidence": s.confidence,
                    "linked_flag": s.linked_flag,
                    "affected_symbol": s.affected_symbol,
                }
                for s in suggs
            ]
        return {
            "timestamp": report.timestamp,
            "input_hash": report.input_hash,
            "confidence_score": report.confidence_score,
            "system_risk_level": report.system_risk_level,
            "recommendation_summary": report.recommendation_summary,
            "latency_ms": report.latency_ms,
            "portfolio_suggestions": sugg_list(report.portfolio_suggestions),
            "position_suggestions": sugg_list(report.position_suggestions),
            "risk_suggestions": sugg_list(report.risk_suggestions),
            "exposure_adjustments": sugg_list(report.exposure_adjustments),
        }

    def test_report_serialises_to_json(self):
        l9 = _l9(
            portfolio=_portfolio(net_exposure_pct=70.0),
            regime=_regime("STRESS"),
        )
        report = make_layer().advise(l9)
        d = self._to_dict(report)
        serialised = json.dumps(d)
        assert isinstance(serialised, str)
        recovered = json.loads(serialised)
        assert recovered["input_hash"] == report.input_hash

    def test_required_keys_present(self):
        l9 = _l9()
        report = make_layer().advise(l9)
        d = self._to_dict(report)
        for key in ("timestamp", "input_hash", "confidence_score",
                    "system_risk_level", "recommendation_summary"):
            assert key in d


# ─────────────────────────────────────────────────────────────────────────────
# O) No Execution Language in Suggestions
# ─────────────────────────────────────────────────────────────────────────────

class TestNoExecutionLanguage:
    _FORBIDDEN_PHRASES = [
        "BUY ", "SELL ", "SELL ALL", "BUY NOW", "EXECUTE",
        "PLACE ORDER", "MARKET ORDER", "LIMIT ORDER",
    ]

    def _check_report(self, report: AdvisoryReport):
        for s in _all_suggestions(report):
            text = (s.suggested_action + " " + s.rationale).upper()
            for phrase in self._FORBIDDEN_PHRASES:
                assert phrase not in text, (
                    f"Forbidden phrase '{phrase}' found in suggestion '{s.category}': {text[:200]}"
                )

    def test_stress_regime_suggestions_no_execution_language(self):
        l9 = _l9(portfolio=_portfolio(net_exposure_pct=70.0), regime=_regime("STRESS"))
        self._check_report(make_layer().advise(l9))

    def test_narrative_decay_suggestions_no_execution_language(self):
        narrative = NarrativeState(tags=(NarrativeTag("AAPL", "N1", "RESOLVED"),))
        l9 = _l9(narrative=narrative)
        self._check_report(make_layer().advise(l9))

    def test_full_stress_scenario_no_execution_language(self):
        holdings = (
            _holding("A", weight_pct=25.0, strategy="SCALP", days_held=5, sector="TECH"),
            _holding("B", weight_pct=20.0, sector="TECH"),
            _holding("C", weight_pct=15.0, sector="TECH"),
        )
        narrative = NarrativeState(tags=(NarrativeTag("A", "N1", "REVERSED"),))
        convergence = ConvergenceSnapshot(scores={"A": (0.80, 0.30)})
        l9 = _l9(
            portfolio=_portfolio(holdings=holdings, net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS", stability=0.15),
            narrative=narrative,
            convergence=convergence,
        )
        self._check_report(make_layer().advise(l9))


# ─────────────────────────────────────────────────────────────────────────────
# P) All Suggestions Have Non-Empty Rationale and Action
# ─────────────────────────────────────────────────────────────────────────────

class TestSuggestionExplainability:
    def test_all_suggestions_have_rationale(self):
        holdings = (
            _holding("A", weight_pct=22.0, strategy="SCALP", days_held=5, sector="TECH"),
            _holding("B", weight_pct=18.0, sector="TECH"),
            _holding("C", weight_pct=15.0, sector="TECH"),
        )
        narrative = NarrativeState(tags=(NarrativeTag("A", "N1", "RESOLVED"),))
        factor = FactorState(
            dominant_factor="MOMENTUM",
            holding_factors={"A": "VALUE", "B": "VALUE", "C": "VALUE"},
        )
        convergence = ConvergenceSnapshot(scores={"A": (0.80, 0.30)})
        l9 = _l9(
            portfolio=_portfolio(holdings=holdings, net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS", stability=0.15),
            narrative=narrative,
            factor=factor,
            convergence=convergence,
        )
        report = make_layer().advise(l9)
        for s in _all_suggestions(report):
            assert s.rationale, f"Empty rationale in suggestion {s.category}"
            assert s.suggested_action, f"Empty suggested_action in suggestion {s.category}"

    def test_all_suggestions_confidence_in_unit_range(self):
        l9 = _l9(
            portfolio=_portfolio(net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS", stability=0.15),
        )
        report = make_layer().advise(l9)
        for s in _all_suggestions(report):
            assert 0.0 <= s.confidence <= 1.0, (
                f"Confidence {s.confidence} out of range for {s.category}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Q) Exposure Symmetry Advisory
# ─────────────────────────────────────────────────────────────────────────────

class TestExposureSymmetryAdvisory:
    def test_high_sector_clustering_produces_exposure_suggestion(self):
        holdings = (
            _holding("A", weight_pct=40.0, sector="TECH"),
            _holding("B", weight_pct=40.0, sector="TECH"),
            _holding("C", weight_pct=10.0, sector="FINANCE"),
        )
        l9 = _l9(
            portfolio=_portfolio(
                holdings=holdings,
                gross_exposure_pct=90.0,
                sector_caps={"TECH": 100.0, "FINANCE": 15.0},
            )
        )
        report = make_layer().advise(l9)
        exp_sugg = _find(report, "EXPOSURE_SYMMETRY")
        assert len(exp_sugg) > 0


# ─────────────────────────────────────────────────────────────────────────────
# R) System Risk Escalation Logic
# ─────────────────────────────────────────────────────────────────────────────

class TestSystemRiskEscalation:
    def test_clean_portfolio_low_or_moderate_risk(self):
        l9 = _l9(regime=_regime("TRENDING", stability=1.0))
        report = make_layer().advise(l9)
        assert report.system_risk_level in ("LOW", "MODERATE", "ELEVATED")

    def test_critical_l9_flags_produce_systemic_risk(self):
        # Multiple RED flags → SYSTEMIC_RISK if stability is also low
        l9 = _l9(
            portfolio=_portfolio(net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS", stability=0.15),
        )
        report = make_layer().advise(l9)
        assert report.system_risk_level in ("HIGH", "SYSTEMIC_RISK")

    def test_recommendation_summary_non_empty_always(self):
        for scenario_l9 in [
            _l9(),
            _l9(regime=_regime("STRESS")),
            _l9(portfolio=_portfolio(net_exposure_pct=70.0), regime=_regime("STRESS", stability=0.15)),
        ]:
            report = make_layer().advise(scenario_l9)
            assert len(report.recommendation_summary) > 20

    def test_recommendation_summary_contains_risk_level_context(self):
        l9 = _l9(
            portfolio=_portfolio(net_exposure_pct=70.0, drawdown_pct=15.0),
            regime=_regime("STRESS", stability=0.15),
        )
        report = make_layer().advise(l9)
        # Should mention a risk-related word
        summary = report.recommendation_summary.lower()
        assert any(word in summary for word in ("risk", "structural", "regime", "alignment"))
