"""
10-Invariant Burn-In Runner
==============================
Sequentially executes each invariant through the FULL autonomous loop:

  1. Memory diff simulation
  2. Intent extraction  (intent_translation.py)
  3. Impact resolution  (target_components from action_plan)
  4. Action plan construction
  5. Stability-aware routing  (router.py + drift_tracker)
  6. Executor dispatch  (routing result)
  7. Semantic adversarial scoring  (semantic_validator.py with mocked LLM)
  8. Drift ledger update  (auto via semantic_validator)
  9. Stability recalculation  (auto via semantic_validator)
  10. Visual validator  (when applicable, mocked capture)

Mocking strategy:
  - LLM (ask()) → per-invariant controlled JSON responses
  - Playwright   → skipped; visual_report.json injected when fixture says
  - File system  → temp directory per test suite (isolated artifacts)

Usage:
    python -m automation.tests.burn_in_runner
"""

import json
import logging
import os
import shutil
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch, MagicMock
from dataclasses import dataclass, field

# ── Path setup ────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.tests.burn_in_fixtures import ALL_INVARIANTS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("burn_in")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data classes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class RunResult:
    """Recorded result for one burn-in run."""
    invariant_id: int
    invariant_name: str
    run_id: str
    worst_stability: float
    executor_used: str
    semantic_score: float
    recommendation: str
    overreach_detected: bool
    visual_drift: Optional[bool]
    stability_index_before: Dict[str, float]
    stability_index_after: Dict[str, float]
    intent_confidence: float
    routing_reason: str
    visual_penalty_applied: float
    pass_fail: str  # PASS / FAIL / WARN
    notes: List[str] = field(default_factory=list)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM Mock Factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LLMMockController:
    """
    Controls what the mocked ask() returns per call.
    The DriftAnalyzer calls ask() twice:
      Call 1 → Alignment Judge  → return mock_alignment JSON
      Call 2 → Drift Prosecutor → return mock_drift JSON
    """

    def __init__(self):
        self._alignment: Dict[str, Any] = {}
        self._drift: Dict[str, Any] = {}
        self._call_count = 0

    def configure(self, alignment: Dict, drift: Dict):
        self._alignment = alignment
        self._drift = drift
        self._call_count = 0

    def mock_ask(self, prompt: str) -> str:
        self._call_count += 1
        if self._call_count == 1:
            return json.dumps(self._alignment)
        else:
            return json.dumps(self._drift)


# Global controller for patching
_llm_controller = LLMMockController()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Isolated Workspace
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class IsolatedWorkspace:
    """Creates a temp workspace for burn-in artifacts."""

    def __init__(self, base_dir: Path):
        self.base = base_dir
        self.runs_dir = base_dir / "automation" / "runs"
        self.history_dir = base_dir / "automation" / "history"
        self.intent_dir = base_dir / "automation" / "intent"

    def setup(self):
        for d in [self.runs_dir, self.history_dir, self.intent_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Initialise empty drift ledger
        ledger_path = self.history_dir / "drift_ledger.json"
        if not ledger_path.exists():
            ledger_path.write_text("[]", encoding="utf-8")

    def cleanup(self):
        if self.base.exists():
            shutil.rmtree(self.base, ignore_errors=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Per-Run Pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_stability_snapshot(components: List[str]) -> Dict[str, float]:
    """Get current stability index for each component."""
    from automation.history.drift_tracker import compute_stability_index
    return {c: compute_stability_index(c) for c in components}


def run_single_invariant(
    fixture: Dict[str, Any],
    workspace: IsolatedWorkspace,
) -> RunResult:
    """
    Execute one invariant through the full autonomous loop.

    Steps:
      1. Generate run_id
      2. Save intent translation
      3. Snapshot stability (before)
      4. Route task
      5. Run semantic validation (mocked LLM)
      6. Inject visual report if applicable
      7. Re-apply visual penalty if visual report was injected
      8. Snapshot stability (after)
      9. Record result
    """
    run_id = f"burnin-{fixture['id']:02d}-{uuid.uuid4().hex[:8]}"
    components = fixture["target_components"]
    notes: List[str] = []

    logger.info(f"\n{'='*70}")
    logger.info(f"  INVARIANT {fixture['id']}: {fixture['name']}")
    logger.info(f"  Run ID: {run_id}")
    logger.info(f"{'='*70}")

    # ── 1. Intent Extraction ──────────────────────────────────
    from automation.intent.intent_translation import save_intent_translation

    intent_path = save_intent_translation(
        run_id=run_id,
        memory_changes=fixture["memory_changes"],
        intents=fixture["intents"],
        target_components=components,
    )
    # Read back confidence
    intent_data = json.loads(intent_path.read_text(encoding="utf-8"))
    intent_confidence = intent_data.get("confidence", 0.0)
    notes.append(f"Intent confidence: {intent_confidence:.4f}")

    # ── 2. Stability Snapshot (before) ────────────────────────
    stability_before = _get_stability_snapshot(components)
    notes.append(f"Stability before: {stability_before}")

    # ── 3. Stability-Aware Routing ────────────────────────────
    from automation.router import TaskRouter

    router = TaskRouter(project_root=workspace.base)
    task = {
        "task_id": f"invariant-{fixture['id']}",
        "run_id": run_id,
        "action_plan": fixture["action_plan"],
        "changed_memory_files": [
            m["file"] for m in fixture["memory_changes"]
        ],
    }
    executor_used, routing_reason = router.route(task)
    notes.append(f"Routed to: {executor_used} — {routing_reason}")

    # Read worst_stability from stability_decision if written
    worst_stability = 1.0
    decision_path = (
        workspace.runs_dir / run_id / "stability_decision.json"
    )
    if decision_path.exists():
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        worst_stability = decision.get("worst_stability", 1.0)

    # ── 4. Semantic Validation (mocked LLM) ───────────────────
    _llm_controller.configure(
        alignment=fixture["mock_alignment"],
        drift=fixture["mock_drift"],
    )

    from automation.semantic.semantic_validator import SemanticValidator

    validator = SemanticValidator(
        run_id=run_id,
        project_root=str(workspace.base),
    )

    with patch(
        "automation.semantic.drift_analyzer.ask",
        side_effect=_llm_controller.mock_ask,
    ):
        report = validator.validate(
            intent_file=fixture["intents"][0].get("intent", ""),
            plan=fixture["action_plan"],
            changed_files=fixture["changed_files"],
            diff=fixture["diff"],
            success_criteria=fixture["invariant_text"],
        )

    semantic_score = report.get("final_score", 0.0)
    recommendation = report.get("recommendation", "UNKNOWN")
    overreach_detected = report.get("drift", {}).get("overreach_detected", False)
    notes.append(f"Semantic score (pre-visual): {semantic_score:.4f}")
    notes.append(f"Recommendation (pre-visual): {recommendation}")

    # ── 4b. Regression Detection (Phase C) ────────────────
    from automation.history.regression_detector import detect_regressions
    regression = detect_regressions(run_id=run_id)
    reg_found = regression.get("regression_detected", False)
    reg_count = regression.get("total_findings", 0)
    notes.append(f"Regression detected: {reg_found} ({reg_count} finding(s))")

    # ── 4c. Healing Advisor (Phase C) ─────────────────────
    from automation.semantic.healing_advisor import generate_healing_recommendations
    run_dir_for_healing = workspace.runs_dir / run_id
    run_dir_for_healing.mkdir(parents=True, exist_ok=True)
    healing = generate_healing_recommendations(
        run_id=run_id, run_dir=run_dir_for_healing,
    )
    heal_count = healing.get("total_recommendations", 0)
    notes.append(f"Healing recommendations: {heal_count}")

    # ── 5. Visual Validation ──────────────────────────────────
    visual_drift = None
    visual_penalty = 0.0

    if fixture["is_ui_related"] and fixture.get("visual_report_override"):
        # Inject visual report
        run_dir = workspace.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        vr = fixture["visual_report_override"].copy()
        vr["run_id"] = run_id
        vr_path = run_dir / "visual_report.json"
        vr_path.write_text(json.dumps(vr, indent=2), encoding="utf-8")
        notes.append(f"Visual report injected: drift={vr.get('visual_drift')}, "
                     f"dom_passed={vr.get('dom_passed')}")

        # Re-apply visual penalty (the validator already tried, but the
        # visual_report hadn't been injected yet — re-run the penalty step)
        validator._apply_visual_penalty(report, run_dir)

        semantic_score = report.get("final_score", semantic_score)
        recommendation = report.get("recommendation", recommendation)
        visual_penalty = report.get("visual_penalty_applied", 0.0)
        visual_drift = vr.get("visual_drift", False)
        notes.append(f"Post-visual score: {semantic_score:.4f}")
        notes.append(f"Post-visual recommendation: {recommendation}")
    elif fixture["is_ui_related"]:
        notes.append("UI-related but no visual_report_override — visual skipped")

    # ── 6. Stability Snapshot (after) ─────────────────────────
    # The semantic validator already called generate_stability_report()
    stability_after = _get_stability_snapshot(components)
    notes.append(f"Stability after: {stability_after}")

    # ── 7. Assess pass/fail ───────────────────────────────────
    expected_rec = fixture["expected_recommendation"]
    expected_overreach = fixture["expected_overreach"]
    expected_visual = fixture["expected_visual_triggered"]

    checks_passed = True
    if recommendation != expected_rec:
        notes.append(
            f"⚠ MISMATCH: recommendation={recommendation}, expected={expected_rec}"
        )
        checks_passed = False
    if overreach_detected != expected_overreach:
        notes.append(
            f"⚠ MISMATCH: overreach={overreach_detected}, expected={expected_overreach}"
        )
        checks_passed = False
    if fixture["is_ui_related"] and (visual_drift is not None) != expected_visual:
        notes.append(
            f"⚠ MISMATCH: visual_triggered={visual_drift is not None}, expected={expected_visual}"
        )
        checks_passed = False

    pass_fail = "PASS" if checks_passed else "FAIL"

    return RunResult(
        invariant_id=fixture["id"],
        invariant_name=fixture["name"],
        run_id=run_id,
        worst_stability=worst_stability,
        executor_used=executor_used,
        semantic_score=semantic_score,
        recommendation=recommendation,
        overreach_detected=overreach_detected,
        visual_drift=visual_drift,
        stability_index_before=stability_before,
        stability_index_after=stability_after,
        intent_confidence=intent_confidence,
        routing_reason=routing_reason,
        visual_penalty_applied=visual_penalty,
        pass_fail=pass_fail,
        notes=notes,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Results Reporter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_summary_table(results: List[RunResult]):
    """Print a summary table of all 10 runs."""
    print("\n" + "=" * 120)
    print("  10-INVARIANT BURN-IN — RESULTS SUMMARY")
    print("=" * 120)
    print(
        f"{'#':>3} | {'Name':<28} | {'Status':<6} | {'Run ID':<24} | "
        f"{'Stab':>5} | {'Exec':<7} | {'Score':>6} | {'Rec':<7} | "
        f"{'Over':>4} | {'VDrift':>6} | {'VPen':>5}"
    )
    print("-" * 120)

    for r in results:
        vd = str(r.visual_drift) if r.visual_drift is not None else "N/A"
        print(
            f"{r.invariant_id:>3} | {r.invariant_name:<28} | "
            f"{r.pass_fail:<6} | {r.run_id:<24} | "
            f"{r.worst_stability:>5.2f} | {r.executor_used:<7} | "
            f"{r.semantic_score:>6.4f} | {r.recommendation:<7} | "
            f"{str(r.overreach_detected):>4} | {vd:>6} | "
            f"{r.visual_penalty_applied:>5.2f}"
        )

    print("=" * 120)

    passed = sum(1 for r in results if r.pass_fail == "PASS")
    failed = sum(1 for r in results if r.pass_fail == "FAIL")
    print(f"\n  ✅ Passed: {passed}  |  ❌ Failed: {failed}  |  Total: {len(results)}")
    print()


def print_stability_evolution(results: List[RunResult]):
    """Show how stability indices evolved across all 10 runs."""
    print("\n" + "=" * 80)
    print("  STABILITY EVOLUTION ACROSS RUNS")
    print("=" * 80)

    # Collect all components
    all_components = set()
    for r in results:
        all_components.update(r.stability_index_after.keys())

    for comp in sorted(all_components):
        print(f"\n  Component: {comp}")
        for r in results:
            before = r.stability_index_before.get(comp)
            after = r.stability_index_after.get(comp)
            if before is not None or after is not None:
                b = f"{before:.4f}" if before is not None else "  N/A "
                a = f"{after:.4f}" if after is not None else "  N/A "
                delta = ""
                if before is not None and after is not None:
                    d = after - before
                    sign = "+" if d >= 0 else ""
                    delta = f"  ({sign}{d:.4f})"
                print(f"    Run {r.invariant_id:>2}: {b} → {a}{delta}")

    print("=" * 80)


def print_detailed_notes(results: List[RunResult]):
    """Print per-run detailed notes."""
    print("\n" + "=" * 80)
    print("  DETAILED RUN NOTES")
    print("=" * 80)

    for r in results:
        status_icon = "✅" if r.pass_fail == "PASS" else "❌"
        print(f"\n  {status_icon} Invariant {r.invariant_id}: {r.invariant_name}")
        print(f"     Run ID: {r.run_id}")
        print(f"     Routing: {r.routing_reason}")
        for n in r.notes:
            print(f"       • {n}")

    print("=" * 80)


def save_results_json(results: List[RunResult], output_path: Path):
    """Persist results to JSON for downstream analysis."""
    records = []
    for r in results:
        records.append({
            "invariant_id": r.invariant_id,
            "invariant_name": r.invariant_name,
            "run_id": r.run_id,
            "worst_stability": r.worst_stability,
            "executor_used": r.executor_used,
            "semantic_score": r.semantic_score,
            "recommendation": r.recommendation,
            "overreach_detected": r.overreach_detected,
            "visual_drift": r.visual_drift,
            "stability_index_before": r.stability_index_before,
            "stability_index_after": r.stability_index_after,
            "intent_confidence": r.intent_confidence,
            "routing_reason": r.routing_reason,
            "visual_penalty_applied": r.visual_penalty_applied,
            "pass_fail": r.pass_fail,
            "notes": r.notes,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps({"timestamp": datetime.now().isoformat(), "runs": records}, indent=2),
        encoding="utf-8",
    )
    logger.info(f"Results saved to {output_path}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main Entry Point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("\n" + "█" * 70)
    print("  10-INVARIANT BURN-IN TEST")
    print("  Stress testing every layer of the autonomous loop")
    print("█" * 70)

    # Set up isolated workspace
    workspace_base = PROJECT_ROOT / "automation" / "tests" / "_burn_in_workspace"
    workspace = IsolatedWorkspace(workspace_base)

    # Clean previous run
    if workspace_base.exists():
        shutil.rmtree(workspace_base, ignore_errors=True)
    workspace.setup()

    # Redirect drift tracker paths to isolated workspace
    import automation.history.drift_tracker as dt
    original_ledger_path = dt.DRIFT_LEDGER_PATH
    original_stability_path = dt.STABILITY_REPORT_PATH
    dt.DRIFT_LEDGER_PATH = workspace.history_dir / "drift_ledger.json"
    dt.STABILITY_REPORT_PATH = workspace.history_dir / "stability_report.json"

    # Redirect regression detector paths to isolated workspace
    import automation.history.regression_detector as rd
    original_rd_ledger = rd.DRIFT_LEDGER_PATH
    original_rd_stability = rd.STABILITY_REPORT_PATH
    original_rd_report = rd.REGRESSION_REPORT_PATH
    rd.DRIFT_LEDGER_PATH = workspace.history_dir / "drift_ledger.json"
    rd.STABILITY_REPORT_PATH = workspace.history_dir / "stability_report.json"
    rd.REGRESSION_REPORT_PATH = workspace.history_dir / "regression_report.json"

    # Redirect healing advisor paths to isolated workspace
    import automation.semantic.healing_advisor as ha
    original_ha_ledger = ha.DRIFT_LEDGER_PATH
    original_ha_stability = ha.STABILITY_REPORT_PATH
    original_ha_regression = ha.REGRESSION_REPORT_PATH
    ha.DRIFT_LEDGER_PATH = workspace.history_dir / "drift_ledger.json"
    ha.STABILITY_REPORT_PATH = workspace.history_dir / "stability_report.json"
    ha.REGRESSION_REPORT_PATH = workspace.history_dir / "regression_report.json"

    # Redirect intent directory
    import automation.intent.intent_translation as it
    original_intent_dir = it.INTENT_DIR
    it.INTENT_DIR = workspace.intent_dir

    results: List[RunResult] = []

    try:
        for i, fixture in enumerate(ALL_INVARIANTS, 1):
            logger.info(f"\n{'━'*70}")
            logger.info(f"  Starting invariant {i}/10: {fixture['name']}")
            logger.info(f"{'━'*70}")

            try:
                result = run_single_invariant(fixture, workspace)
                results.append(result)

                status = "✅ PASS" if result.pass_fail == "PASS" else "❌ FAIL"
                logger.info(
                    f"  Invariant {i} complete: {status}  "
                    f"score={result.semantic_score:.4f}  "
                    f"rec={result.recommendation}  "
                    f"executor={result.executor_used}"
                )
            except Exception as e:
                logger.error(f"  ❌ Invariant {i} CRASHED: {e}", exc_info=True)
                results.append(RunResult(
                    invariant_id=fixture["id"],
                    invariant_name=fixture["name"],
                    run_id=f"burnin-{fixture['id']:02d}-CRASHED",
                    worst_stability=0.0,
                    executor_used="NONE",
                    semantic_score=0.0,
                    recommendation="CRASH",
                    overreach_detected=False,
                    visual_drift=None,
                    stability_index_before={},
                    stability_index_after={},
                    intent_confidence=0.0,
                    routing_reason=f"CRASHED: {e}",
                    visual_penalty_applied=0.0,
                    pass_fail="FAIL",
                    notes=[f"Exception: {e}"],
                ))

        # ── Print reports ────────────────────────────────────
        print_summary_table(results)
        print_stability_evolution(results)
        print_detailed_notes(results)

        # ── Save JSON results ────────────────────────────────
        results_path = workspace_base / "burn_in_results.json"
        save_results_json(results, results_path)

        # ── Final Ledger Dump ────────────────────────────────
        ledger = json.loads(dt.DRIFT_LEDGER_PATH.read_text(encoding="utf-8"))
        print(f"\n  Drift ledger entries: {len(ledger)}")

        stability = {}
        if dt.STABILITY_REPORT_PATH.exists():
            stability = json.loads(dt.STABILITY_REPORT_PATH.read_text(encoding="utf-8"))
        print(f"  Stability report components: {len(stability.get('components', []))}")

        # ── Exit code ────────────────────────────────────────
        failed = sum(1 for r in results if r.pass_fail == "FAIL")
        if failed > 0:
            print(f"\n  ❌ {failed} invariant(s) did not match expectations.")
            return 1
        else:
            print(f"\n  ✅ All 10 invariants behaved as expected.")
            return 0

    finally:
        # Restore original paths
        dt.DRIFT_LEDGER_PATH = original_ledger_path
        dt.STABILITY_REPORT_PATH = original_stability_path
        rd.DRIFT_LEDGER_PATH = original_rd_ledger
        rd.STABILITY_REPORT_PATH = original_rd_stability
        rd.REGRESSION_REPORT_PATH = original_rd_report
        ha.DRIFT_LEDGER_PATH = original_ha_ledger
        ha.STABILITY_REPORT_PATH = original_ha_stability
        ha.REGRESSION_REPORT_PATH = original_ha_regression
        it.INTENT_DIR = original_intent_dir


if __name__ == "__main__":
    sys.exit(main())
