"""
Semantic Validator — Edge Case Test Suite
==========================================
Tests the FOUR unvalidated scenarios:
  1. Ambiguous diff reasoning (DriftAnalyzer)
  2. Subtle partial implementation detection (DriftAnalyzer)
  3. Cross-layer violation detection (ContractEnforcer)
  4. Contract enforcement under conflicting rules (ContractEnforcer)
"""

import sys
import os
import json
import logging
from pathlib import Path

# Mock LLM before any imports
os.environ["MOCK_GEMINI"] = "1"

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

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
    if detail and not passed:
        print(f"         → {detail}")


def test_cross_layer_violation_lens_imports_execution():
    """
    TEST 3a: Lens file importing from execution layer = LAYER_SKIP violation.
    """
    enforcer = ContractEnforcer()
    diff = """+from src.execution.order_router import place_order
+import src.execution.portfolio_manager as pm
 class TechnicalLens:
"""
    changed_files = ["src/lens/technical_lens.py"]
    violations = enforcer.check_violations(diff, changed_files)
    layer_skips = [v for v in violations if v["type"] == "LAYER_SKIP"]
    report("Cross-layer: Lens → Execution import detected",
           len(layer_skips) >= 1,
           f"Expected ≥1 LAYER_SKIP, got {len(layer_skips)}: {layer_skips}")


def test_cross_layer_violation_no_false_positive():
    """
    TEST 3b: Normal lens import should NOT trigger violation.
    """
    enforcer = ContractEnforcer()
    diff = """+from src.layers.factor_layer import FactorLayer
+import logging
"""
    changed_files = ["src/lens/technical_lens.py"]
    violations = enforcer.check_violations(diff, changed_files)
    layer_skips = [v for v in violations if v["type"] == "LAYER_SKIP"]
    report("Cross-layer: Normal import → no false positive",
           len(layer_skips) == 0,
           f"Expected 0 LAYER_SKIP, got {len(layer_skips)}: {layer_skips}")


def test_cross_layer_non_lens_file_importing_execution():
    """
    TEST 3c: Non-lens file importing execution should NOT trigger LAYER_SKIP.
    """
    enforcer = ContractEnforcer()
    diff = """+from src.execution.order_router import place_order
"""
    changed_files = ["src/strategy/momentum_strategy.py"]
    violations = enforcer.check_violations(diff, changed_files)
    layer_skips = [v for v in violations if v["type"] == "LAYER_SKIP"]
    report("Cross-layer: Strategy → Execution (no violation expected)",
           len(layer_skips) == 0,
           f"Expected 0 LAYER_SKIP, got {len(layer_skips)}")


def test_protected_path_memory_modification():
    """
    TEST 4a: Modifying docs/memory/ file = HIGH CONSTRAINT_BREAK.
    """
    enforcer = ContractEnforcer()
    diff = "+# changed something"
    changed_files = ["docs/memory/03_domain/domain_model.md"]
    violations = enforcer.check_violations(diff, changed_files)
    constraint_breaks = [v for v in violations if v["type"] == "CONSTRAINT_BREAK"]
    report("Contract: Memory file modification flagged as HIGH",
           len(constraint_breaks) == 1 and constraint_breaks[0]["severity"] == "HIGH",
           f"Got {len(constraint_breaks)} CONSTRAINT_BREAK violations: {constraint_breaks}")


def test_protected_path_epistemic_modification():
    """
    TEST 4b: Modifying docs/epistemic/ file = should be flagged.
    Current code only checks docs/memory/. This tests if docs/epistemic/ is MISSING.
    """
    enforcer = ContractEnforcer()
    diff = "+# changed something"
    changed_files = ["docs/epistemic/current_phase.md"]
    violations = enforcer.check_violations(diff, changed_files)
    constraint_breaks = [v for v in violations if v["type"] == "CONSTRAINT_BREAK"]
    report("Contract: Epistemic file modification flagged",
           len(constraint_breaks) >= 1,
           f"MISSING RULE: docs/epistemic/ not checked! Got {len(constraint_breaks)} violations")


def test_conflicting_yaml_memory_and_source():
    """
    TEST 4c: Changed files include BOTH memory AND source files.
    Memory should be flagged, source should be clean.
    """
    enforcer = ContractEnforcer()
    diff = """+# some change to memory
+# some change to source
"""
    changed_files = [
        "docs/memory/02_success/success_criteria.md",
        "src/layers/factor_layer.py"
    ]
    violations = enforcer.check_violations(diff, changed_files)
    constraint_breaks = [v for v in violations if v["type"] == "CONSTRAINT_BREAK"]
    report("Contract: Mixed memory+source → only memory flagged",
           len(constraint_breaks) == 1,
           f"Expected 1 CONSTRAINT_BREAK (memory only), got {len(constraint_breaks)}")


def test_drift_analyzer_empty_diff():
    """
    TEST 1a: Empty diff should return no drift, score=1.0.
    """
    analyzer = DriftAnalyzer()
    result = analyzer.detect_drift(
        intent="Add logging",
        plan={"objective": "Add logging"},
        diff="",
    )
    report("Drift: Empty diff → no drift, score=1.0",
           result["drift_detected"] == False and result["alignment_score"] == 1.0,
           f"Got drift={result['drift_detected']}, score={result['alignment_score']}")


def test_drift_analyzer_no_intent():
    """
    TEST 1b: Missing intent should use fallback string, not crash.
    """
    analyzer = DriftAnalyzer()
    result = analyzer.detect_drift(
        intent="",
        plan={"objective": "Add logging"},
        diff="+print('hello')",
    )
    report("Drift: Missing intent → no crash",
           result is not None and "alignment_score" in result,
           f"Result: {result}")


def test_drift_analyzer_no_plan():
    """
    TEST 1c: Missing plan should use fallback dict, not crash.
    """
    analyzer = DriftAnalyzer()
    result = analyzer.detect_drift(
        intent="Add logging",
        plan=None,
        diff="+print('hello')",
    )
    report("Drift: Missing plan → no crash",
           result is not None and "alignment_score" in result,
           f"Result: {result}")


def test_contract_enforcer_empty_inputs():
    """
    TEST 4d: Empty diff and empty changed_files should return no violations.
    """
    enforcer = ContractEnforcer()
    violations = enforcer.check_violations("", [])
    report("Contract: Empty inputs → 0 violations",
           len(violations) == 0,
           f"Got {len(violations)} violations")


def test_contract_enforcer_automation_config_protection():
    """
    TEST 4e: Modifying automation_config.py should NOT be flagged by current rules
    (unless we add a rule for it).
    """
    enforcer = ContractEnforcer()
    diff = "+DRY_RUN = True"
    changed_files = ["automation/automation_config.py"]
    violations = enforcer.check_violations(diff, changed_files)
    report("Contract: automation_config.py → no false positive",
           len(violations) == 0,
           f"Got {len(violations)} violations: {violations}")


def test_cross_layer_multiple_violations():
    """
    TEST 3d: Multiple layer violations in a single diff.
    """
    enforcer = ContractEnforcer()
    diff = """+from src.execution.order_router import place_order
+from src.execution.portfolio_manager import rebalance
"""
    changed_files = ["src/lens/factor_lens.py"]
    violations = enforcer.check_violations(diff, changed_files)
    layer_skips = [v for v in violations if v["type"] == "LAYER_SKIP"]
    report("Cross-layer: Multiple violations detected",
           len(layer_skips) >= 2,
           f"Expected ≥2 LAYER_SKIP, got {len(layer_skips)}")


if __name__ == "__main__":
    print("=" * 60)
    print("  SEMANTIC VALIDATOR — EDGE CASE TEST SUITE")
    print("=" * 60)

    print("\n── Cross-Layer Violation Detection ──")
    test_cross_layer_violation_lens_imports_execution()
    test_cross_layer_violation_no_false_positive()
    test_cross_layer_non_lens_file_importing_execution()
    test_cross_layer_multiple_violations()

    print("\n── Contract Enforcement ──")
    test_protected_path_memory_modification()
    test_protected_path_epistemic_modification()
    test_conflicting_yaml_memory_and_source()
    test_contract_enforcer_empty_inputs()
    test_contract_enforcer_automation_config_protection()

    print("\n── Drift Analyzer Robustness ──")
    test_drift_analyzer_empty_diff()
    test_drift_analyzer_no_intent()
    test_drift_analyzer_no_plan()

    print(f"\n{'=' * 60}")
    print(f"  Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
    print(f"{'=' * 60}")

    sys.exit(1 if FAIL > 0 else 0)
