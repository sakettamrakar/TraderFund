"""
Semantic Validator — Adversarial Regression Test Suite
=======================================================
5 Cases:
  Case 1: Perfect alignment        → ACCEPT
  Case 2: Partial enforcement       → REVIEW
  Case 3: Overreach                 → REJECT
  Case 4: Missing test update       → coverage flag
  Case 5: Superficial rename only   → REJECT
"""

import sys
import os
import json
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.semantic.scoring import compute_score
from automation.semantic.contract_enforcer import ContractEnforcer
from automation.semantic.drift_analyzer import DriftAnalyzer

logging.basicConfig(level=logging.WARNING)

PASS = 0
FAIL = 0

def report(name, passed, detail=""):
    global PASS, FAIL
    status = "✅ PASS" if passed else "❌ FAIL"
    if not passed:
        FAIL += 1
    else:
        PASS += 1
    print(f"  {status}  {name}")
    if detail:
        print(f"         → {detail}")


# ── SCORING TESTS (No LLM Required) ─────────────────────────

def test_case_1_perfect_alignment():
    """Perfect alignment → ACCEPT."""
    alignment = {
        "intent_match": 0.95,
        "plan_match": 0.92,
        "component_scope_respected": True,
    }
    drift = {
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    }
    result = compute_score(alignment, drift, [])
    report("Case 1: Perfect alignment → ACCEPT",
           result.recommendation == "ACCEPT" and result.final_score >= 0.85,
           f"score={result.final_score}, rec={result.recommendation}")


def test_case_2_partial_enforcement():
    """Partial enforcement: 1 missing req → REVIEW."""
    alignment = {
        "intent_match": 0.80,
        "plan_match": 0.70,
        "component_scope_respected": True,
    }
    drift = {
        "overreach_detected": False,
        "missing_requirements": ["Error rate tracking not implemented"],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    }
    result = compute_score(alignment, drift, [])
    report("Case 2: Partial enforcement → REVIEW",
           result.recommendation == "REVIEW",
           f"score={result.final_score}, rec={result.recommendation}")


def test_case_3_overreach():
    """Overreach detected → REJECT regardless of score."""
    alignment = {
        "intent_match": 0.90,
        "plan_match": 0.85,
        "component_scope_respected": False,
    }
    drift = {
        "overreach_detected": True,
        "missing_requirements": [],
        "unintended_modifications": ["Renamed class without authorization"],
        "semantic_mismatch": [],
    }
    result = compute_score(alignment, drift, [])
    report("Case 3: Overreach → REJECT",
           result.recommendation == "REJECT",
           f"score={result.final_score}, rec={result.recommendation}")


def test_case_4_multiple_missing():
    """3 missing requirements → heavy penalty → REJECT."""
    alignment = {
        "intent_match": 0.70,
        "plan_match": 0.60,
        "component_scope_respected": True,
    }
    drift = {
        "overreach_detected": False,
        "missing_requirements": [
            "Step 2: Error tracking",
            "Step 3: Health endpoint",
            "Step 4: Dashboard integration"
        ],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    }
    result = compute_score(alignment, drift, [])
    report("Case 4: 3 missing requirements → REJECT (score < 0.60)",
           result.recommendation == "REJECT" and result.final_score < 0.60,
           f"score={result.final_score}, rec={result.recommendation}")


def test_case_5_superficial_rename():
    """Rename only, no real work → low scores → REJECT."""
    alignment = {
        "intent_match": 0.10,
        "plan_match": 0.05,
        "component_scope_respected": False,
    }
    drift = {
        "overreach_detected": True,
        "missing_requirements": ["Actual implementation of logging"],
        "unintended_modifications": ["Class renamed from FactorLayer to EnhancedFactorEngine"],
        "semantic_mismatch": ["Renaming is not logging — completely different semantic"],
    }
    result = compute_score(alignment, drift, [])
    report("Case 5: Superficial rename → REJECT",
           result.recommendation == "REJECT" and result.final_score < 0.20,
           f"score={result.final_score}, rec={result.recommendation}")


# ── SCORING EDGE CASES ──────────────────────────────────────

def test_score_floor_at_zero():
    """Score cannot go negative."""
    alignment = {"intent_match": 0.1, "plan_match": 0.1, "component_scope_respected": False}
    drift = {
        "overreach_detected": True,
        "missing_requirements": ["a", "b", "c", "d", "e"],
        "unintended_modifications": ["x", "y"],
        "semantic_mismatch": ["z"],
    }
    result = compute_score(alignment, drift, [])
    report("Edge: Score floor at 0.0",
           result.final_score == 0.0,
           f"score={result.final_score}")


def test_contract_violation_penalty():
    """HIGH contract violation adds 0.25 penalty per violation."""
    alignment = {"intent_match": 0.90, "plan_match": 0.90, "component_scope_respected": True}
    drift = {
        "overreach_detected": False,
        "missing_requirements": [],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    }
    violations = [
        {"type": "CONSTRAINT_BREAK", "description": "Modified docs/memory/", "severity": "HIGH"},
    ]
    result = compute_score(alignment, drift, violations)
    report("Edge: HIGH contract violation → -0.25 penalty",
           result.final_score <= 0.65,
           f"score={result.final_score}, expected ~0.65")


def test_accept_requires_no_drift_flags():
    """Even with score >= 0.85, drift flags prevent ACCEPT."""
    alignment = {"intent_match": 0.95, "plan_match": 0.90, "component_scope_respected": True}
    drift = {
        "overreach_detected": False,
        "missing_requirements": ["Minor documentation update"],
        "unintended_modifications": [],
        "semantic_mismatch": [],
    }
    result = compute_score(alignment, drift, [])
    report("Edge: Score ≥0.85 but drift flag → REVIEW not ACCEPT",
           result.recommendation != "ACCEPT",
           f"score={result.final_score}, rec={result.recommendation}")


def test_breakdown_is_populated():
    """Scoring breakdown must always have content."""
    alignment = {"intent_match": 0.50, "plan_match": 0.50, "component_scope_respected": True}
    drift = {"overreach_detected": False, "missing_requirements": [], "unintended_modifications": [], "semantic_mismatch": []}
    result = compute_score(alignment, drift, [])
    report("Edge: Breakdown always populated",
           len(result.breakdown) >= 3,
           f"breakdown_len={len(result.breakdown)}")


# ── CONTRACT ENFORCER TESTS ─────────────────────────────────

def test_contract_overreach_file_detection():
    """ContractEnforcer detects memory modification."""
    enforcer = ContractEnforcer()
    diff = "+# changed"
    changed_files = ["docs/memory/01_intent/project_intent.md", "src/layers/factor_layer.py"]
    violations = enforcer.check_violations(diff, changed_files)
    constraint_breaks = [v for v in violations if v["type"] == "CONSTRAINT_BREAK"]
    report("Contract: Protected path detection",
           len(constraint_breaks) == 1,
           f"Found {len(constraint_breaks)} CONSTRAINT_BREAK")


def test_contract_layer_skip_detection():
    """ContractEnforcer layer skip with dot notation imports."""
    enforcer = ContractEnforcer()
    diff = "+from src.execution.order_router import place_order"
    changed_files = ["src/lens/technical_lens.py"]
    violations = enforcer.check_violations(diff, changed_files)
    layer_skips = [v for v in violations if v["type"] == "LAYER_SKIP"]
    report("Contract: Layer skip detection (dot notation)",
           len(layer_skips) >= 1,
           f"Found {len(layer_skips)} LAYER_SKIP")


# ── DRIFT ANALYZER DETERMINISTIC TESTS ──────────────────────

def test_file_overreach_detection():
    """DriftAnalyzer detects when changed files exceed plan targets."""
    analyzer = DriftAnalyzer()
    overreach = analyzer._detect_file_overreach(
        target_files=["src/layers/factor_layer.py"],
        changed_files=["src/layers/factor_layer.py", "src/api/health.py", "setup.py"],
    )
    report("Drift: File overreach detection",
           len(overreach) == 2,
           f"Found {len(overreach)} overreaching files: {overreach}")


def test_no_overreach_when_targets_match():
    """No overreach when all changed files are in plan."""
    analyzer = DriftAnalyzer()
    overreach = analyzer._detect_file_overreach(
        target_files=["src/layers/factor_layer.py"],
        changed_files=["src/layers/factor_layer.py"],
    )
    report("Drift: No false positive on matching files",
           len(overreach) == 0,
           f"Found {len(overreach)} overreaching files")


def test_empty_diff_no_drift():
    """Empty diff → no drift, score=1.0."""
    analyzer = DriftAnalyzer()
    result = analyzer.run_dual_pass(
        intent="Add logging",
        plan={"objective": "Add logging"},
        diff="",
    )
    alignment = result["alignment"]
    drift = result["drift"]
    report("Drift: Empty diff → perfect alignment",
           alignment["intent_match"] == 1.0 and not drift["overreach_detected"],
           f"intent_match={alignment['intent_match']}, overreach={drift['overreach_detected']}")


if __name__ == "__main__":
    print("=" * 60)
    print("  SEMANTIC VALIDATOR — ADVERSARIAL REGRESSION SUITE")
    print("=" * 60)

    print("\n── Case 1-5: Core Adversarial Scenarios ──")
    test_case_1_perfect_alignment()
    test_case_2_partial_enforcement()
    test_case_3_overreach()
    test_case_4_multiple_missing()
    test_case_5_superficial_rename()

    print("\n── Scoring Edge Cases ──")
    test_score_floor_at_zero()
    test_contract_violation_penalty()
    test_accept_requires_no_drift_flags()
    test_breakdown_is_populated()

    print("\n── Contract Enforcer ──")
    test_contract_overreach_file_detection()
    test_contract_layer_skip_detection()

    print("\n── Drift Analyzer (Deterministic) ──")
    test_file_overreach_detection()
    test_no_overreach_when_targets_match()
    test_empty_diff_no_drift()

    print(f"\n{'=' * 60}")
    print(f"  Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
    print(f"{'=' * 60}")

    sys.exit(1 if FAIL > 0 else 0)
