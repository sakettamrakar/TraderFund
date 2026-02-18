"""
PHASE QA-2 — Enforcement & Prompt Integrity
=============================================
Comprehensive coverage for:
  1. ContractEnforcer._check_config_integrity()
  2. SemanticValidator._apply_visual_penalty()
  3. SemanticValidator._apply_jules_context()
  4. _build_fix_prompt() in run_build_loop.py

No new architecture or abstractions. Functions under test run real code.
Only filesystem interactions (visual_report.json) are managed via tmp_path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AUTOMATION_DIR = PROJECT_ROOT / "automation"

# Ensure both roots are importable before any project imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

from automation.semantic.contract_enforcer import ContractEnforcer
from automation.semantic.semantic_validator import SemanticValidator
from automation.run_build_loop import _build_fix_prompt


# ──────────────────────────────────────────────────────────────────────────────
# Test helpers
# ──────────────────────────────────────────────────────────────────────────────

def _fresh_validator() -> SemanticValidator:
    """Instantiate SemanticValidator without touching the filesystem."""
    v = SemanticValidator.__new__(SemanticValidator)
    v.report_generator = MagicMock()
    return v


def _accept_report(score: float = 0.90) -> dict:
    return {
        "final_score": score,
        "recommendation": "ACCEPT",
        "intent_alignment_score": score,
        "explanation_tree": [],
    }


def _review_report(score: float = 0.75) -> dict:
    return {
        "final_score": score,
        "recommendation": "REVIEW",
        "intent_alignment_score": score,
        "explanation_tree": [],
    }


def _write_visual(tmp_path: Path, visual_drift: bool, dom_passed: bool) -> None:
    (tmp_path / "visual_report.json").write_text(
        json.dumps({"visual_drift": visual_drift, "dom_passed": dom_passed}),
        encoding="utf-8",
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1. ContractEnforcer._check_config_integrity()
# ══════════════════════════════════════════════════════════════════════════════

class TestCheckConfigIntegrity:

    _CFG = ["automation/automation_config.py"]

    def _ce(self) -> ContractEnforcer:
        return ContractEnforcer()

    # ── Tamper detection cases ─────────────────────────────────────────────

    def test_detects_dry_run_lowercase_false(self):
        """`+dry_run = false` → CONFIG_TAMPER."""
        violations = self._ce()._check_config_integrity("+dry_run = false\n", self._CFG)
        assert len(violations) == 1
        assert violations[0]["type"] == "CONFIG_TAMPER"
        assert violations[0]["severity"] == "HIGH"

    def test_detects_DRY_RUN_capital_False(self):
        """`+DRY_RUN = False` (mixed case) → CONFIG_TAMPER."""
        violations = self._ce()._check_config_integrity("+DRY_RUN = False\n", self._CFG)
        assert len(violations) == 1
        assert violations[0]["type"] == "CONFIG_TAMPER"

    def test_detects_no_spaces_around_equals(self):
        """`+dry_run=False` (no spaces) → CONFIG_TAMPER."""
        violations = self._ce()._check_config_integrity("+dry_run=False\n", self._CFG)
        assert len(violations) == 1
        assert violations[0]["type"] == "CONFIG_TAMPER"

    def test_detects_all_caps_FALSE(self):
        """`+DRY_RUN = FALSE` (all caps) → CONFIG_TAMPER."""
        violations = self._ce()._check_config_integrity("+DRY_RUN = FALSE\n", self._CFG)
        assert len(violations) == 1
        assert violations[0]["type"] == "CONFIG_TAMPER"

    def test_case_insensitive_dry_run_mixed(self):
        """`+Dry_Run = false` (arbitrary mixed case for key) → CONFIG_TAMPER."""
        violations = self._ce()._check_config_integrity("+Dry_Run = false\n", self._CFG)
        assert len(violations) == 1
        assert violations[0]["type"] == "CONFIG_TAMPER"

    def test_multiple_tamper_lines_each_flagged(self):
        """Two separate tamper lines → two violations."""
        diff = "+dry_run = False\n+DRY_RUN = false\n"
        violations = self._ce()._check_config_integrity(diff, self._CFG)
        assert len(violations) == 2
        assert all(v["type"] == "CONFIG_TAMPER" for v in violations)

    def test_description_is_human_readable(self):
        """Violation description mentions DRY_RUN."""
        violations = self._ce()._check_config_integrity("+DRY_RUN = False\n", self._CFG)
        assert "DRY_RUN" in violations[0]["description"].upper()

    # ── No false positives ─────────────────────────────────────────────────

    def test_no_violation_when_file_is_not_automation_config(self):
        """Even matching diff is ignored if the file is not automation_config."""
        violations = self._ce()._check_config_integrity(
            "+dry_run = False\n", ["src/somemodule.py"]
        )
        assert violations == []

    def test_no_violation_for_removal_line(self):
        """`-dry_run = False` (deletion) is not a tamper attempt."""
        violations = self._ce()._check_config_integrity("-dry_run = False\n", self._CFG)
        assert violations == []

    def test_no_violation_unchanged_context_line(self):
        """A context line (space prefix) must not trigger detection."""
        violations = self._ce()._check_config_integrity(" dry_run = False\n", self._CFG)
        assert violations == []

    def test_no_violation_setting_to_true(self):
        """`+dry_run = true` is not a disable attempt."""
        violations = self._ce()._check_config_integrity("+dry_run = true\n", self._CFG)
        assert violations == []

    def test_no_violation_empty_diff(self):
        """Empty diff with config file in changeset → no violations."""
        violations = self._ce()._check_config_integrity("", self._CFG)
        assert violations == []

    def test_no_violation_empty_changed_files(self):
        """Matching diff but no changed files → no violations."""
        violations = self._ce()._check_config_integrity("+dry_run = False\n", [])
        assert violations == []


# ══════════════════════════════════════════════════════════════════════════════
# 2. SemanticValidator._apply_visual_penalty()
# ══════════════════════════════════════════════════════════════════════════════

class TestApplyVisualPenalty:

    def _run(self, report: dict, tmp_path: Path) -> dict:
        v = _fresh_validator()
        v._apply_visual_penalty(report, tmp_path)
        return report

    # ── No-penalty paths ───────────────────────────────────────────────────

    def test_no_visual_report_file_leaves_report_untouched(self, tmp_path):
        """Absent visual_report.json → report is not modified at all."""
        report = _accept_report(0.90)
        self._run(report, tmp_path)
        assert report["final_score"] == 0.90
        assert report["recommendation"] == "ACCEPT"
        assert "visual_penalty_applied" not in report

    def test_no_drift_no_dom_failure_is_clean(self, tmp_path):
        """visual_drift=False, dom_passed=True → early return, no penalty."""
        report = _accept_report(0.90)
        _write_visual(tmp_path, visual_drift=False, dom_passed=True)
        self._run(report, tmp_path)
        assert report["final_score"] == 0.90
        assert "visual_penalty_applied" not in report

    # ── Penalty arithmetic ─────────────────────────────────────────────────

    def test_visual_drift_only_applies_015(self, tmp_path):
        """visual_drift=True, dom_passed=True → penalty exactly 0.15."""
        report = _accept_report(0.90)
        _write_visual(tmp_path, visual_drift=True, dom_passed=True)
        self._run(report, tmp_path)
        assert report["visual_penalty_applied"] == 0.15
        assert report["final_score"] == pytest.approx(0.75, abs=1e-4)

    def test_dom_failure_only_applies_010(self, tmp_path):
        """visual_drift=False, dom_passed=False → penalty exactly 0.10."""
        report = _accept_report(0.90)
        _write_visual(tmp_path, visual_drift=False, dom_passed=False)
        self._run(report, tmp_path)
        assert report["visual_penalty_applied"] == 0.10
        assert report["final_score"] == pytest.approx(0.80, abs=1e-4)

    def test_combined_penalty_is_025(self, tmp_path):
        """visual_drift=True AND dom_passed=False → combined penalty 0.25."""
        report = _accept_report(0.90)
        _write_visual(tmp_path, visual_drift=True, dom_passed=False)
        self._run(report, tmp_path)
        assert report["visual_penalty_applied"] == 0.25
        assert report["final_score"] == pytest.approx(0.65, abs=1e-4)

    def test_score_clamped_to_zero(self, tmp_path):
        """Score never goes below 0.0 even with combined penalty."""
        report = _accept_report(0.10)
        _write_visual(tmp_path, visual_drift=True, dom_passed=False)
        self._run(report, tmp_path)
        assert report["final_score"] >= 0.0

    def test_intent_alignment_score_updated(self, tmp_path):
        """intent_alignment_score mirrors final_score after penalty."""
        report = _accept_report(0.90)
        _write_visual(tmp_path, visual_drift=True, dom_passed=True)
        self._run(report, tmp_path)
        assert report["intent_alignment_score"] == report["final_score"]

    # ── Recommendation downgrade logic ────────────────────────────────────

    def test_accept_becomes_review_on_minor_drift(self, tmp_path):
        """ACCEPT 0.90 − 0.15 = 0.75 → REVIEW."""
        report = _accept_report(0.90)
        _write_visual(tmp_path, visual_drift=True, dom_passed=True)
        self._run(report, tmp_path)
        assert report["recommendation"] == "REVIEW"

    def test_accept_becomes_reject_on_major_combined_drift(self, tmp_path):
        """ACCEPT 0.80 − 0.25 = 0.55 → REJECT."""
        report = _accept_report(0.80)
        _write_visual(tmp_path, visual_drift=True, dom_passed=False)
        self._run(report, tmp_path)
        assert report["recommendation"] == "REJECT"

    def test_review_can_downgrade_to_reject(self, tmp_path):
        """REVIEW 0.75 − 0.25 = 0.50 → REJECT (downgrade from REVIEW is allowed)."""
        report = _review_report(0.75)
        _write_visual(tmp_path, visual_drift=True, dom_passed=False)
        self._run(report, tmp_path)
        assert report["recommendation"] == "REJECT"

    def test_downgrade_only_no_upgrade_from_review(self, tmp_path):
        """REVIEW with high score: dom_passed=False pushes 0.95 → 0.85.
        New computed rec would be ACCEPT (0.85 >= 0.85), but ACCEPT rank 0 < REVIEW rank 1,
        so downgrade check fails → recommendation stays REVIEW."""
        report = {
            "final_score": 0.95,
            "recommendation": "REVIEW",
            "intent_alignment_score": 0.95,
            "explanation_tree": [],
        }
        _write_visual(tmp_path, visual_drift=False, dom_passed=False)
        self._run(report, tmp_path)
        assert report["recommendation"] == "REVIEW"

    def test_reject_never_upgraded_regardless_of_score(self, tmp_path):
        """A REJECT stays REJECT even after penalty (which can only worsen it)."""
        report = {
            "final_score": 0.20,
            "recommendation": "REJECT",
            "intent_alignment_score": 0.20,
            "explanation_tree": [],
        }
        _write_visual(tmp_path, visual_drift=True, dom_passed=True)
        self._run(report, tmp_path)
        assert report["recommendation"] == "REJECT"

    # ── Explanation tree population ────────────────────────────────────────

    def test_visual_drift_adds_explanation_tree_entry(self, tmp_path):
        """visual_drift flag produces an explanation tree entry."""
        report = _accept_report(0.90)
        report["explanation_tree"] = []
        _write_visual(tmp_path, visual_drift=True, dom_passed=True)
        self._run(report, tmp_path)
        tree_text = " ".join(report["explanation_tree"])
        assert "Visual drift" in tree_text or "visual_drift" in tree_text.lower()

    def test_dom_failure_adds_explanation_tree_entry(self, tmp_path):
        """dom_passed=False flag produces an explanation tree entry."""
        report = _accept_report(0.90)
        report["explanation_tree"] = []
        _write_visual(tmp_path, visual_drift=False, dom_passed=False)
        self._run(report, tmp_path)
        tree_text = " ".join(report["explanation_tree"])
        assert "DOM" in tree_text


# ══════════════════════════════════════════════════════════════════════════════
# 3. SemanticValidator._apply_jules_context()
# ══════════════════════════════════════════════════════════════════════════════

class TestApplyJulesContext:

    def _run(self, report: dict, context) -> dict:
        v = _fresh_validator()
        v._apply_jules_context(report, context)
        return report

    # ── No-advisory baseline ───────────────────────────────────────────────

    def test_no_context_no_penalty(self):
        """None context → report enriched but score/recommendation unchanged."""
        report = _accept_report(0.90)
        self._run(report, None)
        assert report["final_score"] == 0.90
        assert report["recommendation"] == "ACCEPT"
        assert report["strict_failure"] is False
        assert "jules_advisory_penalty" not in report

    def test_pr_without_url_does_not_trigger_mandatory_missing(self):
        """PR dict present but no pr_url → mandatory_tests_missing=False."""
        report = _accept_report(0.90)
        ctx = {"jules_pr": {"title": "feat: something"}, "jules_test_summary": {}}
        self._run(report, ctx)
        assert report["final_score"] == 0.90
        assert report["strict_failure"] is False

    def test_tests_all_pass_no_penalty(self):
        """PR URL exists, all tests pass → no advisory, score unchanged."""
        report = _accept_report(0.90)
        ctx = {
            "jules_pr": {"pr_url": "https://github.com/org/repo/pull/1"},
            "jules_test_summary": {"tests_total": 4, "tests_passed": 4, "tests_failed": 0},
        }
        self._run(report, ctx)
        assert report["final_score"] == 0.90
        assert "jules_advisory_penalty" not in report
        assert report["strict_failure"] is False

    # ── mandatory_tests_missing only ──────────────────────────────────────

    def test_mandatory_tests_missing_applies_008_penalty(self):
        """PR URL + tests_total=0 → advisory penalty -0.08."""
        report = _accept_report(0.90)
        ctx = {
            "jules_pr": {"pr_url": "https://github.com/org/repo/pull/1"},
            "jules_test_summary": {"tests_total": 0, "tests_passed": 0, "tests_failed": 0},
        }
        self._run(report, ctx)
        assert report["jules_advisory_penalty"] == pytest.approx(0.08)
        assert report["final_score"] == pytest.approx(0.82, abs=1e-4)
        assert report["recommendation"] == "REVIEW"
        assert report["strict_failure"] is True

    def test_mandatory_tests_missing_advisory_in_tree(self):
        """Advisory note about missing test summary appears in explanation_tree."""
        report = _accept_report(0.90)
        report["explanation_tree"] = []
        ctx = {
            "jules_pr": {"pr_url": "https://github.com/org/repo/pull/1"},
            "jules_test_summary": {},
        }
        self._run(report, ctx)
        combined = " | ".join(report["explanation_tree"])
        assert "test summary is missing" in combined

    # ── critical_tests_failed only ────────────────────────────────────────

    def test_critical_tests_failed_applies_012_penalty(self):
        """tests_failed > 0 → advisory penalty -0.12."""
        report = _accept_report(0.90)
        ctx = {
            "jules_pr": {},
            "jules_test_summary": {"tests_total": 10, "tests_passed": 8, "tests_failed": 2},
        }
        self._run(report, ctx)
        assert report["jules_advisory_penalty"] == pytest.approx(0.12)
        assert report["final_score"] == pytest.approx(0.78, abs=1e-4)
        assert report["recommendation"] == "REVIEW"
        assert report["strict_failure"] is True

    def test_critical_tests_failed_advisory_mentions_count(self):
        """Advisory note includes the exact failed test count."""
        report = _accept_report(0.90)
        report["explanation_tree"] = []
        ctx = {
            "jules_pr": {},
            "jules_test_summary": {"tests_total": 5, "tests_passed": 3, "tests_failed": 2},
        }
        self._run(report, ctx)
        combined = " | ".join(report["explanation_tree"])
        assert "2 failed tests" in combined

    # ── Both conditions combined ───────────────────────────────────────────

    def test_both_mandatory_and_critical_combined_020_penalty(self):
        """PR URL + tests_total=0 AND tests_failed=1 → -0.08 + -0.12 = -0.20."""
        report = _accept_report(0.90)
        ctx = {
            "jules_pr": {"pr_url": "https://github.com/org/repo/pull/1"},
            "jules_test_summary": {"tests_total": 0, "tests_passed": 0, "tests_failed": 1},
        }
        self._run(report, ctx)
        assert report["jules_advisory_penalty"] == pytest.approx(0.20)
        assert report["final_score"] == pytest.approx(0.70, abs=1e-4)
        assert report["strict_failure"] is True

    # ── Metadata population (always) ──────────────────────────────────────

    def test_metadata_fields_populated_unconditionally(self):
        """did_pr_exist, tests_passed, tests_failed, test_failure_rate always set."""
        report = _accept_report(0.90)
        ctx = {
            "jules_pr": {"pr_url": "https://example.com/pr/5"},
            "jules_test_summary": {"tests_total": 4, "tests_passed": 4, "tests_failed": 0},
        }
        self._run(report, ctx)
        assert report["did_pr_exist"] is True
        assert report["tests_passed"] == 4
        assert report["tests_failed"] == 0
        assert report["test_failure_rate"] == 0.0

    def test_test_failure_rate_computed_correctly(self):
        """test_failure_rate = failed / total, rounded to 4 decimal places."""
        report = _accept_report(0.90)
        ctx = {
            "jules_pr": {},
            "jules_test_summary": {"tests_total": 3, "tests_passed": 1, "tests_failed": 2},
        }
        self._run(report, ctx)
        assert report["test_failure_rate"] == pytest.approx(0.6667, abs=1e-3)

    # ── Advisory downgrade scope ───────────────────────────────────────────

    def test_advisory_only_downgrades_accept_not_review(self):
        """Advisory does not downgrade REVIEW to REJECT — only ACCEPT to REVIEW."""
        report = _review_report(0.75)
        ctx = {
            "jules_pr": {"pr_url": "https://github.com/org/repo/pull/1"},
            "jules_test_summary": {"tests_total": 0},
        }
        self._run(report, ctx)
        # _apply_jules_context only downgrades when recommendation == "ACCEPT"
        assert report["recommendation"] == "REVIEW"

    def test_non_dict_context_treated_safely(self):
        """Passing a non-dict context does not crash; report gets defaults."""
        report = _accept_report(0.90)
        self._run(report, "invalid_context_type")
        # No crash, strict_failure is False (no conditions triggered)
        assert "strict_failure" in report


# ══════════════════════════════════════════════════════════════════════════════
# 4. _build_fix_prompt()
# ══════════════════════════════════════════════════════════════════════════════

_INTENT = "Implement regime-aware trust score boundaries per Invariant 2."


class TestBuildFixPrompt:

    def test_forbidden_block_always_present(self):
        """FORBIDDEN keyword appears regardless of report contents."""
        prompt = _build_fix_prompt({}, _INTENT, "")
        assert "FORBIDDEN" in prompt

    def test_docs_memory_protection_clause_present(self):
        """docs/memory/ must be listed as a protected path."""
        prompt = _build_fix_prompt({}, _INTENT, "")
        assert "docs/memory/" in prompt

    def test_docs_epistemic_protection_clause_present(self):
        """docs/epistemic/ must also be listed as a protected path."""
        prompt = _build_fix_prompt({}, _INTENT, "")
        assert "docs/epistemic/" in prompt

    def test_dot_git_protection_clause_present(self):
        """.git/ must be listed as a protected path."""
        prompt = _build_fix_prompt({}, _INTENT, "")
        assert ".git/" in prompt

    def test_empty_report_produces_graceful_fallback(self):
        """Empty report → fallback issue text, no crash."""
        prompt = _build_fix_prompt({}, _INTENT, "")
        assert "Review failed without specific issue details." in prompt

    def test_contract_violation_description_in_prompt(self):
        """Contract violation message appears under [CONTRACT <SEVERITY>] label."""
        report = {
            "contract_violations": [
                {"severity": "HIGH", "message": "Protected path violated in docs/memory/"}
            ]
        }
        prompt = _build_fix_prompt(report, _INTENT, "")
        assert "[CONTRACT HIGH]" in prompt
        assert "Protected path violated" in prompt

    def test_contract_violation_file_field_fallback(self):
        """If no 'message' key, falls back to 'file' key."""
        report = {
            "contract_violations": [
                {"severity": "MEDIUM", "file": "src/risky_module.py"}
            ]
        }
        prompt = _build_fix_prompt(report, _INTENT, "")
        assert "src/risky_module.py" in prompt

    def test_missing_requirement_appears(self):
        """drift.missing_requirements items appear with [MISSING] prefix."""
        report = {"drift": {"missing_requirements": ["Trust boundary check is absent"]}}
        prompt = _build_fix_prompt(report, _INTENT, "")
        assert "[MISSING] Trust boundary check is absent" in prompt

    def test_unintended_modification_appears(self):
        """drift.unintended_modifications items appear with [UNINTENDED] prefix."""
        report = {"drift": {"unintended_modifications": ["Modified read-only fixture"]}}
        prompt = _build_fix_prompt(report, _INTENT, "")
        assert "[UNINTENDED] Modified read-only fixture" in prompt

    def test_semantic_mismatch_appears(self):
        """drift.semantic_mismatch items appear with [MISMATCH] prefix."""
        report = {"drift": {"semantic_mismatch": ["Trust logic inconsistent with spec"]}}
        prompt = _build_fix_prompt(report, _INTENT, "")
        assert "[MISMATCH] Trust logic inconsistent with spec" in prompt

    def test_multi_issue_each_prefixed_with_dash(self):
        """Multiple issues each get `  - ` prefix formatting."""
        report = {
            "drift": {
                "missing_requirements": ["req_A", "req_B"],
                "semantic_mismatch": ["mismatch_C"],
            }
        }
        prompt = _build_fix_prompt(report, _INTENT, "")
        assert "  - [MISSING] req_A" in prompt
        assert "  - [MISSING] req_B" in prompt
        assert "  - [MISMATCH] mismatch_C" in prompt

    def test_intent_truncated_at_600_chars(self):
        """Intent string is truncated at 600 characters."""
        long_intent = "x" * 800
        prompt = _build_fix_prompt({}, long_intent, "")
        assert "x" * 600 in prompt
        assert "x" * 601 not in prompt

    def test_original_intent_short_not_truncated(self):
        """Short intent is included verbatim."""
        short_intent = "Fix invariant boundary check."
        prompt = _build_fix_prompt({}, short_intent, "")
        assert short_intent in prompt

    def test_deterministic_identical_inputs_identical_output(self):
        """Same inputs produce character-identical output."""
        report = {"drift": {"missing_requirements": ["R1", "R2"]}}
        assert _build_fix_prompt(report, _INTENT, "diff") == _build_fix_prompt(report, _INTENT, "diff")

    def test_violations_list_items_merged_without_duplication(self):
        """Top-level `violations` list merged; no item appears more than once."""
        report = {
            "violations": [
                {"message": "layer_violation_unique"},
            ]
        }
        prompt = _build_fix_prompt(report, _INTENT, "")
        assert prompt.count("layer_violation_unique") == 1

    def test_prompt_contains_numbered_requirements(self):
        """Requirements block lists numbered items (1. 2. 3. etc.)."""
        prompt = _build_fix_prompt({}, _INTENT, "")
        assert "1." in prompt
        assert "2." in prompt
        assert "3." in prompt
