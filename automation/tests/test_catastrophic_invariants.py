"""
Test Suite — Catastrophic Invariant Firewall (Phase CI)
=======================================================
One test per invariant.  Each test verifies:
  - Valid inputs → PASS (no exception)
  - Invalid inputs → FAIL + CatastrophicInvariantError raised
"""

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.invariants.catastrophic_firewall import (
    CatastrophicInvariantError,
    check_convergence_integrity,
    check_factor_integrity,
    check_narrative_grounding,
    check_portfolio_regime_conflict,
    check_regime_validity,
    check_risk_caps,
    check_strategy_regime_alignment,
    check_trust_determinism,
    run_all_invariants,
    run_invariant,
)


# ===================================================================
# 1. Regime undefined — L1
# ===================================================================
class TestRegimeValidity:
    def test_pass_valid_regime(self):
        result = check_regime_validity({"behavior": "RISK_ON"})
        assert result["status"] == "PASS"
        assert result["layer"] == "L1"

    def test_fail_regime_undefined(self):
        result = check_regime_validity({"behavior": None})
        assert result["status"] == "FAIL"
        assert result["layer"] == "L1"
        # Must raise when run through orchestrator
        with pytest.raises(CatastrophicInvariantError):
            run_invariant("check_regime_validity", check_regime_validity, {"behavior": None})

    def test_fail_regime_unknown(self):
        result = check_regime_validity({"behavior": "UNKNOWN"})
        assert result["status"] == "FAIL"

    def test_fail_regime_empty_dict(self):
        result = check_regime_validity({})
        assert result["status"] == "FAIL"


# ===================================================================
# 2. Narrative without source — L2
# ===================================================================
class TestNarrativeGrounding:
    def test_pass_grounded_narrative(self):
        result = check_narrative_grounding({
            "headline": "Fed raises rates",
            "sources": ["Reuters"],
        })
        assert result["status"] == "PASS"
        assert result["layer"] == "L2"

    def test_fail_no_sources(self):
        result = check_narrative_grounding({
            "headline": "Fed raises rates",
            "sources": [],
        })
        assert result["status"] == "FAIL"
        with pytest.raises(CatastrophicInvariantError):
            run_invariant(
                "check_narrative_grounding",
                check_narrative_grounding,
                {"headline": "Fed raises rates", "sources": []},
            )

    def test_fail_empty_headline(self):
        result = check_narrative_grounding({"headline": "", "sources": ["Reuters"]})
        assert result["status"] == "FAIL"


# ===================================================================
# 3. Trust score > 1.0 — L3
# ===================================================================
class TestTrustDeterminism:
    def test_pass_valid_score(self):
        result = check_trust_determinism({"signal": "momentum"}, 0.85)
        assert result["status"] == "PASS"
        assert result["layer"] == "L3"

    def test_fail_score_above_one(self):
        result = check_trust_determinism({"signal": "momentum"}, 1.5)
        assert result["status"] == "FAIL"
        with pytest.raises(CatastrophicInvariantError):
            run_invariant(
                "check_trust_determinism",
                check_trust_determinism,
                {"signal": "momentum"},
                1.5,
            )

    def test_fail_score_negative(self):
        result = check_trust_determinism({"signal": "momentum"}, -0.1)
        assert result["status"] == "FAIL"

    def test_fail_score_none(self):
        result = check_trust_determinism({"signal": "momentum"}, None)
        assert result["status"] == "FAIL"


# ===================================================================
# 4. Factor constant output — L4
# ===================================================================
class TestFactorIntegrity:
    def test_pass_diverse_factors(self):
        result = check_factor_integrity({
            "momentum": {"strength": 0.6, "direction": "long"},
            "value": {"strength": 0.3, "direction": "neutral"},
            "quality": {"strength": 0.8, "direction": "long"},
        })
        assert result["status"] == "PASS"
        assert result["layer"] == "L4"

    def test_fail_all_zero(self):
        result = check_factor_integrity({
            "momentum": {"strength": 0},
            "value": {"strength": 0},
            "quality": {"strength": 0},
        })
        assert result["status"] == "FAIL"
        with pytest.raises(CatastrophicInvariantError):
            run_invariant(
                "check_factor_integrity",
                check_factor_integrity,
                {
                    "momentum": {"strength": 0},
                    "value": {"strength": 0},
                    "quality": {"strength": 0},
                },
            )

    def test_fail_all_identical(self):
        result = check_factor_integrity({
            "momentum": {"strength": 0.5},
            "value": {"strength": 0.5},
            "quality": {"strength": 0.5},
        })
        assert result["status"] == "FAIL"

    def test_fail_empty(self):
        result = check_factor_integrity({})
        assert result["status"] == "FAIL"


# ===================================================================
# 5. Strategy activated in wrong regime — L5
# ===================================================================
class TestStrategyRegimeAlignment:
    def test_pass_compatible(self):
        result = check_strategy_regime_alignment(
            {"name": "Momentum", "compatible_regimes": ["RISK_ON", "TRANSITION"]},
            {"behavior": "RISK_ON"},
        )
        assert result["status"] == "PASS"
        assert result["layer"] == "L5"

    def test_fail_wrong_regime(self):
        result = check_strategy_regime_alignment(
            {"name": "Momentum", "compatible_regimes": ["RISK_ON"]},
            {"behavior": "STRESS"},
        )
        assert result["status"] == "FAIL"
        with pytest.raises(CatastrophicInvariantError):
            run_invariant(
                "check_strategy_regime_alignment",
                check_strategy_regime_alignment,
                {"name": "Momentum", "compatible_regimes": ["RISK_ON"]},
                {"behavior": "STRESS"},
            )

    def test_fail_no_compatible_regimes(self):
        result = check_strategy_regime_alignment(
            {"name": "Broken"},
            {"behavior": "RISK_ON"},
        )
        assert result["status"] == "FAIL"


# ===================================================================
# 6. High conviction with <3 lenses — L7
# ===================================================================
class TestConvergenceIntegrity:
    def test_pass_high_conviction_enough_lenses(self):
        result = check_convergence_integrity({
            "symbol": "AAPL",
            "conviction": "HIGH",
            "contributing_lenses": ["Narrative", "Factor", "Technical"],
        })
        assert result["status"] == "PASS"
        assert result["layer"] == "L7"

    def test_pass_non_high_conviction(self):
        # Watchlist candidates are exempt
        result = check_convergence_integrity({
            "symbol": "AAPL",
            "conviction": "WATCHLIST",
            "contributing_lenses": ["Factor"],
        })
        assert result["status"] == "PASS"

    def test_fail_high_conviction_few_lenses(self):
        result = check_convergence_integrity({
            "symbol": "AAPL",
            "conviction": "HIGH",
            "contributing_lenses": ["Narrative", "Factor"],
        })
        assert result["status"] == "FAIL"
        with pytest.raises(CatastrophicInvariantError):
            run_invariant(
                "check_convergence_integrity",
                check_convergence_integrity,
                {
                    "symbol": "AAPL",
                    "conviction": "HIGH",
                    "contributing_lenses": ["Narrative", "Factor"],
                },
            )


# ===================================================================
# 7. Position > max cap — L8
# ===================================================================
class TestRiskCaps:
    def test_pass_within_cap(self):
        result = check_risk_caps(
            {"symbol": "AAPL", "position_pct": 0.05},
            {"max_position_pct": 0.10},
        )
        assert result["status"] == "PASS"
        assert result["layer"] == "L8"

    def test_fail_exceeds_cap(self):
        result = check_risk_caps(
            {"symbol": "AAPL", "position_pct": 0.15},
            {"max_position_pct": 0.10},
        )
        assert result["status"] == "FAIL"
        with pytest.raises(CatastrophicInvariantError):
            run_invariant(
                "check_risk_caps",
                check_risk_caps,
                {"symbol": "AAPL", "position_pct": 0.15},
                {"max_position_pct": 0.10},
            )


# ===================================================================
# 8. Portfolio regime conflict not flagged — L9
# ===================================================================
class TestPortfolioRegimeConflict:
    def test_pass_conflict_flagged(self):
        result = check_portfolio_regime_conflict(
            {"regime_conflict_detected": True, "flags": ["RegimeConflict", "Other"]},
            {"behavior": "STRESS"},
        )
        assert result["status"] == "PASS"
        assert result["layer"] == "L9"

    def test_pass_no_conflict(self):
        result = check_portfolio_regime_conflict(
            {"regime_conflict_detected": False, "flags": []},
            {"behavior": "RISK_ON"},
        )
        assert result["status"] == "PASS"

    def test_fail_conflict_not_flagged(self):
        result = check_portfolio_regime_conflict(
            {"regime_conflict_detected": True, "flags": ["NarrativeDecay"]},
            {"behavior": "STRESS"},
        )
        assert result["status"] == "FAIL"
        with pytest.raises(CatastrophicInvariantError):
            run_invariant(
                "check_portfolio_regime_conflict",
                check_portfolio_regime_conflict,
                {"regime_conflict_detected": True, "flags": ["NarrativeDecay"]},
                {"behavior": "STRESS"},
            )


# ===================================================================
# Integration: run_all_invariants writes log
# ===================================================================
class TestRunAllInvariants:
    def test_all_pass_writes_log(self, tmp_path):
        run_dir = tmp_path / "test_run"
        run_dir.mkdir()

        log = run_all_invariants(
            run_dir=run_dir,
            regime_state={"behavior": "RISK_ON"},
            narrative_obj={"headline": "Fed holds", "sources": ["Bloomberg"]},
            trust_inputs={"signal": "x"}, trust_score=0.8,
            factor_output={
                "momentum": {"strength": 0.7},
                "value": {"strength": 0.3},
            },
            strategy={"compatible_regimes": ["RISK_ON"]},
            candidate={
                "conviction": "HIGH",
                "contributing_lenses": ["A", "B", "C"],
            },
            position={"position_pct": 0.05},
            portfolio_state={
                "max_position_pct": 0.10,
                "regime_conflict_detected": False,
                "flags": [],
            },
        )
        assert log["overall"] == "PASS"
        log_file = run_dir / "catastrophic_log.json"
        assert log_file.exists()
        data = json.loads(log_file.read_text(encoding="utf-8"))
        assert data["overall"] == "PASS"

    def test_fail_aborts_and_logs(self, tmp_path):
        run_dir = tmp_path / "test_run_fail"
        run_dir.mkdir()

        with pytest.raises(CatastrophicInvariantError):
            run_all_invariants(
                run_dir=run_dir,
                regime_state={"behavior": "UNKNOWN"},
            )

        log_file = run_dir / "catastrophic_log.json"
        assert log_file.exists()
        data = json.loads(log_file.read_text(encoding="utf-8"))
        assert data["overall"] == "FAIL"
