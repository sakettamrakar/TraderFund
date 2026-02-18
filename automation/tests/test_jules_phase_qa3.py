"""
PHASE QA-3 — Precision Hardening
==================================
Covers:
  1. Semantic Scoring Precision    — MEDIUM penalty, mismatch penalty,
                                     stacking order, floor at 0.0
  2. Drift Analyzer Integration    — real DriftAnalyzer (no LLM mock for
                                     JSON extraction; MOCK_GEMINI for LLM)
  3. Stability Persistent Penalty  — regression, 2-clean no recovery,
                                     3-clean recovery, cap at 1.0, stacking
  4. Variance Stability (L3 Inv 6) — 10 identical runs, variance < 0.01
  5. Cross-Run Regression Detection — pre/post score tolerance logic

All tests are deterministic.  LLM calls are intercepted via MOCK_GEMINI env,
never hit the network.
"""

from __future__ import annotations

import os
import json
import statistics
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AUTOMATION_DIR = PROJECT_ROOT / "automation"

for p in (str(PROJECT_ROOT), str(AUTOMATION_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Ensure MOCK_GEMINI is set before importing DriftAnalyzer
os.environ.setdefault("MOCK_GEMINI", "1")

from automation.semantic.scoring import compute_score, ScoringResult
from automation.semantic.drift_analyzer import DriftAnalyzer, DEFAULT_ALIGNMENT, DEFAULT_DRIFT
import automation.history.drift_tracker as dt
from automation.automation_config import config


# ──────────────────────────────────────────────────────────────────────────────
# Test helpers / fixtures
# ──────────────────────────────────────────────────────────────────────────────

def _clean_alignment(intent_match: float = 1.0, plan_match: float = 1.0) -> dict:
    return {
        "intent_match": intent_match,
        "plan_match": plan_match,
        "component_scope_respected": True,
    }


def _clean_drift() -> dict:
    return {
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    }


def _set_ledger_paths(monkeypatch, tmp_path: Path) -> Path:
    history_dir = tmp_path / "automation" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(dt, "DRIFT_LEDGER_PATH", history_dir / "drift_ledger.json")
    monkeypatch.setattr(dt, "STABILITY_REPORT_PATH", history_dir / "stability_report.json")
    monkeypatch.setattr(dt, "STABILITY_STATE_PATH", history_dir / "stability_state.json")
    dt.DRIFT_LEDGER_PATH.write_text("[]", encoding="utf-8")
    return history_dir


def _push_record(
    run_id: str,
    component: str,
    semantic_score: float,
    regression_detected: bool = False,
    clean_run: bool = False,
    overreach: bool = False,
):
    dt.append_run_record(
        run_id=run_id,
        component=component,
        alignment_score=semantic_score,
        semantic_score=semantic_score,
        overreach_detected=overreach,
        missing_steps=0,
        drift_flags=["overreach"] if overreach else [],
        plan_hash=dt.compute_plan_hash({"comp": component}),
        memory_hash=dt.compute_memory_hash({"run": run_id}),
        recommendation="ACCEPT",
        regression_detected=regression_detected,
        target_components=[component],
        regression_score_drop=0.05 if regression_detected else 0.0,
        clean_run=clean_run,
        event_type="QA3_TEST",
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1. Semantic Scoring Precision
# ══════════════════════════════════════════════════════════════════════════════

class TestScoringPrecision:
    """
    Exercises compute_score() with exact penalty arithmetic.
    All assertions verify numeric values, not just recommendation strings.
    """

    # ── MEDIUM contract violation penalty ────────────────────────────────

    def test_medium_violation_applies_010_penalty(self):
        """-0.10 per MEDIUM violation, exactly."""
        violations = [{"severity": "MEDIUM", "type": "LAYER_SKIP", "description": "lens imports exec"}]
        result = compute_score(_clean_alignment(), _clean_drift(), violations)
        # base = (1.0 + 1.0) / 2 = 1.0; penalty = 0.10; final = 0.90
        assert result.final_score == pytest.approx(0.90, abs=1e-4)

    def test_two_medium_violations_stack_to_020(self):
        """Two MEDIUM violations → -0.20 total."""
        violations = [
            {"severity": "MEDIUM", "type": "LAYER_SKIP", "description": "x"},
            {"severity": "MEDIUM", "type": "LAYER_SKIP", "description": "y"},
        ]
        result = compute_score(_clean_alignment(), _clean_drift(), violations)
        assert result.final_score == pytest.approx(0.80, abs=1e-4)

    def test_medium_violation_breakdown_contains_penalty_line(self):
        """MEDIUM penalty appears in the breakdown list."""
        violations = [{"severity": "MEDIUM", "type": "LAYER_SKIP", "description": "z"}]
        result = compute_score(_clean_alignment(), _clean_drift(), violations)
        assert any("MEDIUM" in line for line in result.breakdown)

    def test_medium_violation_still_accept_when_score_high(self):
        """MEDIUM -0.10 on 1.0 base → 0.90 → no drift flags → ACCEPT."""
        violations = [{"severity": "MEDIUM", "type": "LAYER_SKIP", "description": "z"}]
        result = compute_score(_clean_alignment(), _clean_drift(), violations)
        assert result.recommendation == "ACCEPT"

    def test_high_violation_applies_025_penalty(self):
        """-0.25 per HIGH violation, exactly."""
        violations = [{"severity": "HIGH", "type": "CONFIG_TAMPER", "description": "tamper"}]
        result = compute_score(_clean_alignment(), _clean_drift(), violations)
        assert result.final_score == pytest.approx(0.75, abs=1e-4)

    def test_high_violation_causes_review_not_accept(self):
        """HIGH violation blocks ACCEPT even at high score."""
        violations = [{"severity": "HIGH", "type": "CONFIG_TAMPER", "description": "tamper"}]
        result = compute_score(_clean_alignment(), _clean_drift(), violations)
        # final=0.75 would be ACCEPT if no violations; HIGH blocks it
        assert result.recommendation == "REVIEW"

    # ── Semantic mismatch penalty ─────────────────────────────────────────

    def test_single_mismatch_applies_005_penalty(self):
        """-0.05 per semantic_mismatch item, exactly."""
        drift = {**_clean_drift(), "semantic_mismatch": ["trust logic inverted"]}
        result = compute_score(_clean_alignment(), drift, [])
        assert result.final_score == pytest.approx(0.95, abs=1e-4)

    def test_three_mismatches_apply_015_penalty(self):
        """3 mismatches → -0.15."""
        drift = {**_clean_drift(), "semantic_mismatch": ["m1", "m2", "m3"]}
        result = compute_score(_clean_alignment(), drift, [])
        assert result.final_score == pytest.approx(0.85, abs=1e-4)

    def test_mismatch_makes_recommendation_review(self):
        """Any mismatch → drift_flags_present=True → REVIEW even at 0.95."""
        drift = {**_clean_drift(), "semantic_mismatch": ["off by one"]}
        result = compute_score(_clean_alignment(), drift, [])
        assert result.recommendation == "REVIEW"

    def test_mismatch_penalty_breakdown_visible(self):
        """Breakdown contains the mismatch penalty line."""
        drift = {**_clean_drift(), "semantic_mismatch": ["bad"]}
        result = compute_score(_clean_alignment(), drift, [])
        assert any("Semantic mismatch" in line for line in result.breakdown)

    # ── Penalty stacking order ────────────────────────────────────────────

    def test_mismatch_and_medium_violation_stack(self):
        """semantic_mismatch -0.05 + MEDIUM -0.10 = -0.15 total from 1.0 base → 0.85."""
        drift = {**_clean_drift(), "semantic_mismatch": ["conflict"]}
        violations = [{"severity": "MEDIUM", "type": "LAYER_SKIP", "description": "x"}]
        result = compute_score(_clean_alignment(), drift, violations)
        assert result.final_score == pytest.approx(0.85, abs=1e-4)

    def test_missing_requirement_and_high_violation_stack(self):
        """-0.10 (missing) + -0.25 (HIGH) = -0.35 from 1.0 → 0.65. Also REVIEW due to drift & HIGH."""
        drift = {**_clean_drift(), "missing_requirements": ["boundary check"]}
        violations = [{"severity": "HIGH", "type": "CONFIG_TAMPER", "description": "t"}]
        result = compute_score(_clean_alignment(), drift, violations)
        assert result.final_score == pytest.approx(0.65, abs=1e-4)
        assert result.recommendation == "REVIEW"

    def test_scope_plus_overreach_plus_missing_stack(self):
        """scope -0.30 + overreach -0.20 + 2 missing -0.20 = -0.70 from 1.0 → 0.30 → REJECT."""
        alignment = {**_clean_alignment(), "component_scope_respected": False}
        drift = {
            "overreach_detected": True,
            "missing_requirements": ["req_A", "req_B"],
            "unintended_modifications": [],
            "semantic_mismatch": [],
        }
        result = compute_score(alignment, drift, [])
        assert result.final_score == pytest.approx(0.30, abs=1e-4)
        assert result.recommendation == "REJECT"

    def test_all_penalties_combined_clamp_at_zero(self):
        """All penalties at once cannot push score below 0."""
        alignment = {
            "intent_match": 0.0,
            "plan_match": 0.0,
            "component_scope_respected": False,
        }
        drift = {
            "overreach_detected": True,
            "missing_requirements": ["r1", "r2", "r3", "r4"],
            "unintended_modifications": ["u1", "u2", "u3"],
            "semantic_mismatch": ["s1", "s2"],
        }
        violations = [
            {"severity": "HIGH", "type": "CONFIG_TAMPER", "description": "x"},
            {"severity": "HIGH", "type": "CONSTRAINT_BREAK", "description": "y"},
            {"severity": "MEDIUM", "type": "LAYER_SKIP", "description": "z"},
        ]
        result = compute_score(alignment, drift, violations)
        assert result.final_score == 0.0
        assert result.recommendation == "REJECT"

    # ── Floor always 0.0, never negative ─────────────────────────────────

    def test_floor_never_negative_with_zero_base(self):
        """base=0.0 minus any penalty → final_score always 0.0."""
        drift = {**_clean_drift(), "missing_requirements": ["a", "b", "c"]}
        result = compute_score(
            {"intent_match": 0.0, "plan_match": 0.0, "component_scope_respected": True},
            drift, []
        )
        assert result.final_score == 0.0

    def test_floor_holds_with_aggressive_medium_penalties(self):
        """Many MEDIUM violations still floor at 0.0."""
        violations = [{"severity": "MEDIUM", "type": "LAYER_SKIP", "description": str(i)} for i in range(20)]
        result = compute_score(
            {"intent_match": 0.3, "plan_match": 0.3, "component_scope_respected": True},
            _clean_drift(), violations
        )
        assert result.final_score >= 0.0

    def test_base_score_is_mean_of_intent_and_plan(self):
        """base_score = (intent_match + plan_match) / 2.0 — exactly."""
        result = compute_score(
            {"intent_match": 0.80, "plan_match": 0.60, "component_scope_respected": True},
            _clean_drift(), []
        )
        assert result.base_score == pytest.approx(0.70, abs=1e-4)

    def test_scoring_result_is_dataclass_with_all_fields(self):
        """ScoringResult contains all expected attributes."""
        result = compute_score(_clean_alignment(), _clean_drift(), [])
        for attr in ("base_score", "scope_penalty", "overreach_penalty",
                     "missing_penalty", "unintended_penalty", "final_score",
                     "recommendation", "breakdown"):
            assert hasattr(result, attr)


# ══════════════════════════════════════════════════════════════════════════════
# 2. Drift Analyzer Integration Tests (MOCK_GEMINI, no real network)
# ══════════════════════════════════════════════════════════════════════════════

class TestDriftAnalyzerIntegration:
    """
    Integration tests against real DriftAnalyzer code paths.

    MOCK_GEMINI is active at module load, so all LLM calls return
    "MOCK_RESPONSE: ..." strings — which are NOT valid JSON.
    This is intentional: we test the JSON-extraction failure path that
    triggers the fail-safe DEFAULT_ALIGNMENT / DEFAULT_DRIFT.

    Non-JSON LLM output → worst-case penalty guaranteed.
    """

    _INTENT = "Add regime-aware trust boundary enforcement to MetaAnalysis."
    _PLAN = {
        "objective": "Implement Invariant 3",
        "target_files": ["src/intelligence/meta_analysis.py"],
        "steps": ["Check regime", "Apply trust cap", "Log decision"],
    }
    _DIFF = (
        "diff --git a/src/intelligence/meta_analysis.py b/src/intelligence/meta_analysis.py\n"
        "index abc1234..def5678 100644\n"
        "--- a/src/intelligence/meta_analysis.py\n"
        "+++ b/src/intelligence/meta_analysis.py\n"
        "@@ -30,6 +30,12 @@ class MetaAnalysis:\n"
        "+        if regime_category in ['CHOP', 'TRANSITION']:\n"
        "+            if technical_breakout_trust > 0.50:\n"
        "+                self.trust_score = 0.0\n"
        "+                self.status = 'REJECTED'\n"
        "+                return {'trust_score': 0.0, 'status': 'REJECTED'}\n"
    )

    def test_valid_diff_returns_aligned_structure(self):
        """run_dual_pass returns dict with required keys."""
        da = DriftAnalyzer()
        result = da.run_dual_pass(
            intent=self._INTENT,
            plan=self._PLAN,
            diff=self._DIFF,
        )
        for key in ("alignment", "drift", "explanation_tree", "passes_completed"):
            assert key in result, f"Missing key: {key}"

    def test_alignment_judge_executed_returns_dict(self):
        """alignment is a dict with the three expected fields."""
        da = DriftAnalyzer()
        result = da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff=self._DIFF)
        alignment = result["alignment"]
        assert isinstance(alignment, dict)
        for field in ("intent_match", "plan_match", "component_scope_respected"):
            assert field in alignment, f"alignment missing: {field}"

    def test_drift_prosecutor_executed_returns_dict(self):
        """drift is a dict with the four expected fields."""
        da = DriftAnalyzer()
        result = da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff=self._DIFF)
        drift = result["drift"]
        for field in ("overreach_detected", "missing_requirements",
                      "unintended_modifications", "semantic_mismatch"):
            assert field in drift, f"drift missing: {field}"

    def test_non_json_llm_output_triggers_worst_case_penalty(self):
        """
        MOCK_GEMINI returns non-JSON strings, so both passes fall back to
        DEFAULT_ALIGNMENT and DEFAULT_DRIFT — worst-case penalty path.
        scoring then produces a REJECT or REVIEW (never a silent ACCEPT).
        """
        da = DriftAnalyzer()
        result = da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff=self._DIFF)
        alignment = result["alignment"]
        drift = result["drift"]

        # With DEFAULT_ALIGNMENT: intent_match=0.0, plan_match=0.0 → base=0.0
        # compute_score must produce REJECT
        scoring = compute_score(alignment, drift, [])
        assert scoring.recommendation == "REJECT"
        assert scoring.final_score == 0.0

    def test_empty_diff_short_circuits_passes(self):
        """Empty diff → passes_completed=0, trivially aligned, no LLM call needed."""
        da = DriftAnalyzer()
        result = da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff="")
        assert result["passes_completed"] == 0
        # Trivially aligned
        assert result["alignment"]["intent_match"] == 1.0
        assert result["alignment"]["plan_match"] == 1.0
        assert result["drift"]["overreach_detected"] is False

    def test_whitespace_only_diff_treated_as_empty(self):
        """Whitespace-only diff counts as empty (no changes to analyze)."""
        da = DriftAnalyzer()
        result = da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff="   \n\t\n  ")
        assert result["passes_completed"] == 0

    def test_explanation_tree_is_non_empty_list(self):
        """explanation_tree always populated for non-empty diff."""
        da = DriftAnalyzer()
        result = da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff=self._DIFF)
        assert isinstance(result["explanation_tree"], list)
        assert len(result["explanation_tree"]) > 0

    def test_json_extraction_works_from_markdown_fenced_response(self):
        """_extract_json handles ```json ... ``` wrappers correctly."""
        da = DriftAnalyzer()
        fenced = '```json\n{"key": "value", "num": 42}\n```'
        parsed = da._extract_json(fenced)
        assert parsed == {"key": "value", "num": 42}

    def test_json_extraction_works_bare_json(self):
        """_extract_json handles plain JSON without fences."""
        da = DriftAnalyzer()
        parsed = da._extract_json('{"a": 1, "b": true}')
        assert parsed == {"a": 1, "b": True}

    def test_json_extraction_returns_none_for_plain_text(self):
        """_extract_json returns None for pure prose (no JSON braces)."""
        da = DriftAnalyzer()
        result = da._extract_json("This is not JSON at all.")
        assert result is None

    def test_token_truncation_logged_when_diff_over_12000(self, caplog):
        """Diff > 12000 chars logs DIFF_TRUNCATED=true at WARNING level."""
        import logging as stdlib_logging
        da = DriftAnalyzer()
        long_diff = "+" + ("x" * 11999) + "\n" + "+" + ("y" * 2000)  # > 12000
        with caplog.at_level(stdlib_logging.WARNING, logger="automation.semantic.drift_analyzer"):
            da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff=long_diff)
        assert any("DIFF_TRUNCATED=true" in r.message for r in caplog.records)

    def test_short_diff_does_not_log_truncation(self, caplog):
        """Diff <= 12000 chars must NOT log DIFF_TRUNCATED."""
        import logging as stdlib_logging
        da = DriftAnalyzer()
        with caplog.at_level(stdlib_logging.WARNING, logger="automation.semantic.drift_analyzer"):
            da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff=self._DIFF)
        assert not any("DIFF_TRUNCATED" in r.message for r in caplog.records)

    def test_scoring_deterministic_for_identical_mock_inputs(self):
        """Two identical calls produce identical results (deterministic defaults)."""
        da = DriftAnalyzer()
        r1 = da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff=self._DIFF)
        r2 = da.run_dual_pass(intent=self._INTENT, plan=self._PLAN, diff=self._DIFF)
        s1 = compute_score(r1["alignment"], r1["drift"], [])
        s2 = compute_score(r2["alignment"], r2["drift"], [])
        assert s1.final_score == s2.final_score
        assert s1.recommendation == s2.recommendation

    def test_file_overreach_detection_deterministic(self):
        """Changed file outside target_files → overreach flagged deterministically."""
        da = DriftAnalyzer()
        overreach = da._detect_file_overreach(
            target_files=["src/intelligence/meta_analysis.py"],
            changed_files=["src/intelligence/meta_analysis.py", "docs/memory/UNRELATED.md"],
        )
        assert len(overreach) == 1
        assert "UNRELATED.md" in overreach[0]

    def test_no_overreach_when_all_files_match_targets(self):
        """No overreach when every changed file is in the target list."""
        da = DriftAnalyzer()
        overreach = da._detect_file_overreach(
            target_files=["src/analysis.py", "tests/test_analysis.py"],
            changed_files=["src/analysis.py", "tests/test_analysis.py"],
        )
        assert overreach == []

    def test_empty_target_files_suppresses_deterministic_overreach(self):
        """No target_files → overreach detection skipped (returns empty list)."""
        da = DriftAnalyzer()
        overreach = da._detect_file_overreach(target_files=[], changed_files=["some/file.py"])
        assert overreach == []


# ══════════════════════════════════════════════════════════════════════════════
# 3. Stability Persistent Penalty Validation
# ══════════════════════════════════════════════════════════════════════════════

class TestStabilityPersistentPenalty:
    """
    Deterministic replay of the persistent penalty state machine.
    Uses isolated tmp_path ledger so tests never affect each other.
    """

    _CONFIG_SNAP: dict = {}

    @pytest.fixture(autouse=True)
    def _isolate_config(self, monkeypatch, tmp_path):
        _set_ledger_paths(monkeypatch, tmp_path)
        # Pin config knobs for determinism
        monkeypatch.setattr(config, "REGRESSION_PENALTY_WEIGHT", 0.15)
        monkeypatch.setattr(config, "CLEAN_RECOVERY_THRESHOLD", 3)
        monkeypatch.setattr(config, "RECOVERY_WEIGHT", 0.05)
        yield

    # ── Regression → immediate penalty ───────────────────────────────────

    def test_regression_applies_immediate_penalty(self):
        """First regression immediately lowers penalty_model_score by 0.15."""
        comp = "ComponentPenalty"
        _push_record("r0", comp, 0.95)
        dt.generate_stability_report()
        before = dt.compute_component_stability(comp)["penalty_model_score"]

        _push_record("r1", comp, 0.70, regression_detected=True, overreach=True)
        dt.generate_stability_report()
        after = dt.compute_component_stability(comp)["penalty_model_score"]

        assert after < before
        assert pytest.approx(after, abs=1e-4) == before - 0.15

    def test_regression_count_increments(self):
        """regression_count goes from 0 → 1 after one regression."""
        comp = "ComponentRCount"
        _push_record("rc0", comp, 0.90)
        _push_record("rc1", comp, 0.65, regression_detected=True)
        dt.generate_stability_report()
        state = dt.compute_component_stability(comp)
        assert state["regression_count"] >= 1

    def test_regression_resets_consecutive_clean_counter(self):
        """A regression clears consecutive_clean_runs to 0."""
        comp = "ComponentCleanReset"
        _push_record("ccr0", comp, 0.95, clean_run=True)
        _push_record("ccr1", comp, 0.95, clean_run=True)
        _push_record("ccr2", comp, 0.70, regression_detected=True)
        dt.generate_stability_report()
        state = dt.compute_component_stability(comp)
        assert state["consecutive_clean_runs"] == 0

    # ── 2 clean runs → NO recovery ────────────────────────────────────────

    def test_two_clean_runs_do_not_recover_penalty(self):
        """2 clean runs < threshold(3) → penalty_model_score unchanged after regression."""
        comp = "ComponentNoRecover"
        _push_record("nr0", comp, 0.95, regression_detected=True)
        dt.generate_stability_report()
        after_reg = dt.compute_component_stability(comp)["penalty_model_score"]

        _push_record("nr1", comp, 0.95, clean_run=True)
        dt.generate_stability_report()
        after_1 = dt.compute_component_stability(comp)["penalty_model_score"]

        _push_record("nr2", comp, 0.95, clean_run=True)
        dt.generate_stability_report()
        after_2 = dt.compute_component_stability(comp)["penalty_model_score"]

        assert after_1 == pytest.approx(after_reg, abs=1e-6)
        assert after_2 == pytest.approx(after_reg, abs=1e-6)

    def test_non_clean_run_breaks_clean_streak(self):
        """A neutral run (clean_run=False, not regression) resets consecutive counter."""
        comp = "ComponentNeutralBreak"
        _push_record("nb0", comp, 0.90, regression_detected=True)
        dt.generate_stability_report()
        after_reg = dt.compute_component_stability(comp)["penalty_model_score"]

        _push_record("nb1", comp, 0.90, clean_run=True)
        _push_record("nb2", comp, 0.90, clean_run=False)  # breaks streak
        _push_record("nb3", comp, 0.90, clean_run=True)   # only 1 clean since break
        dt.generate_stability_report()
        after = dt.compute_component_stability(comp)["penalty_model_score"]

        assert after == pytest.approx(after_reg, abs=1e-6)

    # ── 3 clean runs → recovery ────────────────────────────────────────────

    def test_three_clean_runs_trigger_recovery(self):
        """Exactly 3 consecutive clean runs triggers recovery (+0.05)."""
        comp = "ComponentRecover3"
        _push_record("r3_0", comp, 0.80, regression_detected=True)
        dt.generate_stability_report()
        after_reg = dt.compute_component_stability(comp)["penalty_model_score"]

        for i in range(3):
            _push_record(f"r3_c{i}", comp, 0.90, clean_run=True)
        dt.generate_stability_report()
        after_recovery = dt.compute_component_stability(comp)["penalty_model_score"]

        assert after_recovery > after_reg
        assert pytest.approx(after_recovery, abs=1e-4) == after_reg + 0.05

    def test_recovery_resets_clean_streak_counter(self):
        """consecutive_clean_runs resets to 0 after recovery fires."""
        comp = "ComponentStreakReset"
        _push_record("sr0", comp, 0.80, regression_detected=True)
        for i in range(3):
            _push_record(f"sr_c{i}", comp, 0.90, clean_run=True)
        dt.generate_stability_report()
        state = dt.compute_component_stability(comp)
        assert state["consecutive_clean_runs"] == 0

    # ── Recovery never exceeds 1.0 ────────────────────────────────────────

    def test_recovery_never_exceeds_1_0(self):
        """penalty_model_score is clamped to 1.0 even with many clean runs."""
        comp = "ComponentCap"
        # Start clean (no regression), then burn many clean runs
        for i in range(9):
            _push_record(f"cap_{i}", comp, 0.99, clean_run=True)
        dt.generate_stability_report()
        state = dt.compute_component_stability(comp)
        assert state["penalty_model_score"] <= 1.0

    def test_stability_score_never_exceeds_1_0(self):
        """The composite stability_score is also bounded to 1.0."""
        comp = "ComponentStabilityCap"
        for i in range(15):
            _push_record(f"sc_{i}", comp, 1.0, clean_run=True)
        dt.generate_stability_report()
        state = dt.compute_component_stability(comp)
        assert state["stability_score"] <= 1.0
        assert state["stability_score"] >= 0.0

    # ── Multiple regressions stack ────────────────────────────────────────

    def test_two_regressions_stack_penalties(self):
        """Two regressions → penalty_model_score = 1.0 - (2 × 0.15) = 0.70."""
        comp = "ComponentDoubleReg"
        _push_record("dr0", comp, 0.90, regression_detected=True)
        _push_record("dr1", comp, 0.75, regression_detected=True)
        dt.generate_stability_report()
        state = dt.compute_component_stability(comp)
        assert state["penalty_model_score"] == pytest.approx(0.70, abs=1e-4)
        assert state["regression_count"] == 2

    def test_three_regressions_clamped_to_zero(self):
        """Seven regressions at -0.15 each: score clamps at 0.0, not negative."""
        comp = "ComponentManyReg"
        for i in range(7):
            _push_record(f"mr_{i}", comp, 0.50, regression_detected=True)
        dt.generate_stability_report()
        state = dt.compute_component_stability(comp)
        assert state["penalty_model_score"] >= 0.0


# ══════════════════════════════════════════════════════════════════════════════
# 4. Variance Stability Test (L3 Invariant 6)
# ══════════════════════════════════════════════════════════════════════════════

class TestVarianceStabilityInvariant:
    """
    L3 Invariant 6 — identical inputs replayed N times must produce
    variance(scores) < 0.01 in the deterministic scoring layer.

    We test at the compute_score() layer (pure math, no LLM) and at the
    DriftAnalyzer DEFAULT path (MOCK_GEMINI, deterministic fallback).
    """

    def test_scoring_variance_zero_for_identical_inputs(self):
        """compute_score with identical inputs 10 times → variance == 0.0."""
        alignment = {"intent_match": 0.75, "plan_match": 0.85, "component_scope_respected": True}
        drift = {
            "overreach_detected": False,
            "missing_requirements": ["req_1"],
            "unintended_modifications": [],
            "semantic_mismatch": ["slight mismatch"],
        }
        violations = [{"severity": "MEDIUM", "type": "LAYER_SKIP", "description": "x"}]

        scores = [compute_score(alignment, drift, violations).final_score for _ in range(10)]

        assert len(scores) == 10
        var = statistics.variance(scores)
        assert var < 0.01, f"Scoring variance {var} >= 0.01 — non-deterministic!"

    def test_drift_analyzer_default_path_variance_zero(self):
        """DriftAnalyzer under MOCK_GEMINI 10 times → identical results → variance == 0."""
        da = DriftAnalyzer()
        intent = "Enforce Invariant 3 trust boundaries."
        plan = {"objective": "Invariant3", "target_files": ["src/meta.py"]}
        diff = "+trust = 0.0 if breakout > 0.5 else trust\n"

        scores = []
        for _ in range(10):
            r = da.run_dual_pass(intent=intent, plan=plan, diff=diff)
            s = compute_score(r["alignment"], r["drift"], [])
            scores.append(s.final_score)

        var = statistics.variance(scores)
        assert var < 0.01, f"DriftAnalyzer variance {var} >= 0.01 — non-deterministic!"

    def test_stability_state_replays_deterministically(self, monkeypatch, tmp_path):
        """
        Replaying the same ledger sequence 10 times produces identical
        penalty_model_score on each replay — variance == 0.0.
        """
        comp = "ComponentVariance"
        scores = []

        for trial in range(10):
            _set_ledger_paths(monkeypatch, tmp_path)
            monkeypatch.setattr(config, "REGRESSION_PENALTY_WEIGHT", 0.15)
            monkeypatch.setattr(config, "CLEAN_RECOVERY_THRESHOLD", 3)
            monkeypatch.setattr(config, "RECOVERY_WEIGHT", 0.05)

            _push_record("v0", comp, 0.95)
            _push_record("v1", comp, 0.70, regression_detected=True)
            _push_record("v2", comp, 0.90, clean_run=True)
            _push_record("v3", comp, 0.91, clean_run=True)
            dt.generate_stability_report()

            state = dt.compute_component_stability(comp)
            scores.append(state["penalty_model_score"])

        var = statistics.variance(scores)
        assert var < 0.01, f"State replay variance {var} >= 0.01 — non-deterministic!"

    def test_recommendation_invariant_across_10_runs(self):
        """Same inputs → recommendation must be identical on all 10 runs."""
        alignment = {"intent_match": 0.70, "plan_match": 0.70, "component_scope_respected": True}
        drift = {**_clean_drift(), "missing_requirements": ["req_x"]}
        recommendations = [compute_score(alignment, drift, []).recommendation for _ in range(10)]
        assert len(set(recommendations)) == 1, f"Non-deterministic recommendations: {set(recommendations)}"


# ══════════════════════════════════════════════════════════════════════════════
# 5. Cross-Run Semantic Regression Detection
# ══════════════════════════════════════════════════════════════════════════════

class TestCrossRunRegressionDetection:
    """
    Validates regression detection logic using the SEMANTIC_REGRESSION_TOLERANCE
    config threshold.  Pure math — no LLM, no HTTP.
    """

    @staticmethod
    def _is_regression(pre: float, post: float, tolerance: float) -> bool:
        """Mirror the regression detection logic used by the build loop."""
        return (pre - post) > tolerance

    @staticmethod
    def _score_drop(pre: float, post: float) -> float:
        return round(max(0.0, pre - post), 6)

    # ── Regression triggered ──────────────────────────────────────────────

    def test_regression_triggered_when_drop_exceeds_tolerance(self):
        """(0.95 - 0.90) = 0.05 > tolerance(0.03) → regression."""
        assert self._is_regression(pre=0.95, post=0.90, tolerance=0.03) is True

    def test_regression_record_has_correct_score_drop(self, monkeypatch, tmp_path):
        """record_regression_event stores the exact pre-post score_drop."""
        _set_ledger_paths(monkeypatch, tmp_path)
        dt.record_regression_event(
            run_id="reg-exact",
            component="CompReg",
            reason="Score dropped below tolerance",
            details={"pre_score": 0.95, "post_score": 0.90},
        )
        ledger = json.loads(dt.DRIFT_LEDGER_PATH.read_text())
        assert len(ledger) == 1
        rec = ledger[0]
        assert rec["regression_detected"] is True
        assert rec["regression_score_drop"] == pytest.approx(0.05, abs=1e-5)

    def test_regression_event_increments_regression_count(self, monkeypatch, tmp_path):
        """After a regression event, regression_count is 1."""
        _set_ledger_paths(monkeypatch, tmp_path)
        monkeypatch.setattr(config, "REGRESSION_PENALTY_WEIGHT", 0.15)
        monkeypatch.setattr(config, "CLEAN_RECOVERY_THRESHOLD", 3)
        monkeypatch.setattr(config, "RECOVERY_WEIGHT", 0.05)

        dt.record_regression_event(
            run_id="ri1",
            component="CompReg2",
            reason="drift",
            details={"pre_score": 0.95, "post_score": 0.90},
        )
        dt.generate_stability_report()
        state = dt.compute_component_stability("CompReg2")
        assert state["regression_count"] == 1

    # ── Within tolerance → no regression ─────────────────────────────────

    def test_no_regression_when_drop_within_tolerance(self):
        """(0.95 - 0.92) = 0.03 == tolerance → NOT a regression (> not >=)."""
        assert self._is_regression(pre=0.95, post=0.92, tolerance=0.03) is False

    def test_no_regression_when_score_improves(self):
        """Score improvement (post > pre) → never a regression."""
        assert self._is_regression(pre=0.85, post=0.92, tolerance=0.03) is False

    def test_no_regression_when_scores_identical(self):
        """Same score on both runs → not a regression."""
        assert self._is_regression(pre=0.90, post=0.90, tolerance=0.03) is False

    # ── Tolerance boundary precision ──────────────────────────────────────

    def test_regression_boundary_just_above_tolerance(self):
        """Drop = 0.031 > tolerance(0.03) → regression (strict >)."""
        assert self._is_regression(pre=1.00, post=0.969, tolerance=0.03) is True

    def test_no_regression_boundary_just_at_tolerance(self):
        """Drop = 0.029 < tolerance(0.03) → NOT regression.
        (Using 0.029 rather than the exact boundary 0.030 because
         floating-point subtraction 1.00 - 0.970 yields
         0.030000000000000027 > 0.030, making the boundary indeterminate.
         The unambiguous sub-tolerance case is 0.029.)"""
        assert self._is_regression(pre=1.00, post=0.971, tolerance=0.03) is False

    def test_score_drop_never_negative(self):
        """score_drop is always ≥ 0 even when post > pre (improvement)."""
        drop = self._score_drop(pre=0.85, post=0.92)
        assert drop == 0.0

    # ── Regression ledger entry payload ──────────────────────────────────

    def test_regression_event_sets_clean_run_false(self, monkeypatch, tmp_path):
        """Regression events always have clean_run=False."""
        _set_ledger_paths(monkeypatch, tmp_path)
        dt.record_regression_event("rce1", "CompClean", "drift",
                                   {"pre_score": 0.90, "post_score": 0.85})
        ledger = json.loads(dt.DRIFT_LEDGER_PATH.read_text())
        assert ledger[0]["clean_run"] is False

    def test_regression_event_type_is_regression_event(self, monkeypatch, tmp_path):
        """event_type in ledger record is REGRESSION_EVENT."""
        _set_ledger_paths(monkeypatch, tmp_path)
        dt.record_regression_event("rce2", "CompType", "score drop",
                                   {"pre_score": 0.95, "post_score": 0.87})
        ledger = json.loads(dt.DRIFT_LEDGER_PATH.read_text())
        assert ledger[0]["event_type"] == "REGRESSION_EVENT"

    def test_multiple_regression_events_stack(self, monkeypatch, tmp_path):
        """Two regression events → regression_count == 2, penalty_model_score = 0.70."""
        _set_ledger_paths(monkeypatch, tmp_path)
        monkeypatch.setattr(config, "REGRESSION_PENALTY_WEIGHT", 0.15)
        monkeypatch.setattr(config, "CLEAN_RECOVERY_THRESHOLD", 3)
        monkeypatch.setattr(config, "RECOVERY_WEIGHT", 0.05)

        dt.record_regression_event("m1", "CompMulti", "r1", {"pre_score": 0.95, "post_score": 0.90})
        dt.record_regression_event("m2", "CompMulti", "r2", {"pre_score": 0.90, "post_score": 0.85})
        dt.generate_stability_report()
        state = dt.compute_component_stability("CompMulti")
        assert state["regression_count"] == 2
        assert state["penalty_model_score"] == pytest.approx(0.70, abs=1e-4)
