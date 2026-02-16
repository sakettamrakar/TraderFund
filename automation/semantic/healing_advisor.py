"""
Advisory Self-Healing Advisor
================================
Generates structured, human-readable healing recommendations
based on semantic reports, drift history, stability metrics,
and regression findings.

CRITICAL RULE: This module is ADVISORY ONLY.
  - It NEVER modifies code, memory, routing, or any system state.
  - It NEVER escalates autonomy.
  - All output is a JSON artifact for human review.

Suggestion Rules:
  R1: Repeated drift on same component → suggest targeted re-specification
  R2: Stability below 0.5 → suggest human review of component design
  R3: Regression pattern detected → suggest rollback investigation
  R4: Overreach in recent run → suggest scope-locking the component
  R5: High volatility (>0.2) → suggest adding invariant tests

Usage:
    from automation.semantic.healing_advisor import generate_healing_recommendations
    recs = generate_healing_recommendations(run_id="run-001", run_dir=Path(...))
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

HISTORY_DIR = Path(__file__).resolve().parent.parent / "history"
DRIFT_LEDGER_PATH = HISTORY_DIR / "drift_ledger.json"
STABILITY_REPORT_PATH = HISTORY_DIR / "stability_report.json"
REGRESSION_REPORT_PATH = HISTORY_DIR / "regression_report.json"

# Thresholds
STABILITY_CRITICAL_THRESHOLD = 0.5
VOLATILITY_HIGH_THRESHOLD = 0.2
REPEATED_DRIFT_WINDOW = 5
REPEATED_DRIFT_MIN_COUNT = 3


def _load_json(path: Path) -> Any:
    """Load a JSON file, returning empty dict/list on failure."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Healing advisor: failed to load {path.name}: {e}")
    return {}


def _rule_r1_repeated_drift(
    component: str, ledger: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    R1: Repeated drift on same component.

    If ≥ REPEATED_DRIFT_MIN_COUNT of the last REPEATED_DRIFT_WINDOW runs
    for this component have drift flags, suggest targeted re-specification.
    """
    comp_records = [r for r in ledger if r.get("component") == component]
    recent = comp_records[-REPEATED_DRIFT_WINDOW:]
    if len(recent) < REPEATED_DRIFT_MIN_COUNT:
        return None

    drift_count = sum(
        1 for r in recent
        if r.get("drift_flags") or r.get("overreach_detected")
    )

    if drift_count >= REPEATED_DRIFT_MIN_COUNT:
        return {
            "rule": "R1",
            "component": component,
            "severity": "high",
            "title": "Repeated drift detected",
            "description": (
                f"{drift_count}/{len(recent)} recent runs for '{component}' "
                f"have drift flags. The specification may be unclear or "
                f"the component boundaries are poorly defined."
            ),
            "suggestion": (
                f"Review and tighten the specification for '{component}'. "
                f"Consider adding explicit boundary constraints and "
                f"success criteria to prevent recurring drift."
            ),
            "action_type": "re-specify",
        }
    return None


def _rule_r2_low_stability(
    component: str, stability_report: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    R2: Stability below critical threshold.

    If stability_index < STABILITY_CRITICAL_THRESHOLD, suggest
    human review of component design.
    """
    for comp in stability_report.get("components", []):
        if comp.get("component") != component:
            continue

        idx = comp.get("stability_index")
        if idx is not None and idx < STABILITY_CRITICAL_THRESHOLD:
            return {
                "rule": "R2",
                "component": component,
                "severity": "critical",
                "title": "Critically low stability",
                "description": (
                    f"Stability index for '{component}' is {idx:.4f}, "
                    f"below the critical threshold of "
                    f"{STABILITY_CRITICAL_THRESHOLD}."
                ),
                "suggestion": (
                    f"Conduct a human review of '{component}' design and "
                    f"implementation. The component is consistently "
                    f"producing low-quality outputs and may need "
                    f"architectural changes."
                ),
                "action_type": "human-review",
                "stability_index": idx,
            }
    return None


def _rule_r3_regression_detected(
    component: str, regression_report: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    R3: Regression pattern detected.

    If the regression report flags findings for this component,
    suggest rollback investigation.
    """
    for comp_summary in regression_report.get("components", []):
        if comp_summary.get("component") != component:
            continue

        findings = comp_summary.get("findings", [])
        if not findings:
            return None

        worst = max(
            findings,
            key=lambda f: {"critical": 3, "high": 2, "medium": 1}.get(
                f.get("severity", ""), 0
            ),
        )

        return {
            "rule": "R3",
            "component": component,
            "severity": worst.get("severity", "medium"),
            "title": "Regression pattern detected",
            "description": (
                f"Regression pattern '{worst.get('pattern')}' detected "
                f"for '{component}': {worst.get('description', '')}"
            ),
            "suggestion": (
                f"Investigate whether recent changes to '{component}' "
                f"caused a quality regression. Consider reverting the "
                f"last change and re-evaluating the approach."
            ),
            "action_type": "rollback-investigation",
            "regression_pattern": worst.get("pattern"),
        }
    return None


def _rule_r4_overreach(
    component: str, ledger: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    R4: Overreach in recent run.

    If the most recent run for this component has overreach_detected,
    suggest scope-locking.
    """
    comp_records = [r for r in ledger if r.get("component") == component]
    if not comp_records:
        return None

    latest = comp_records[-1]
    if latest.get("overreach_detected"):
        return {
            "rule": "R4",
            "component": component,
            "severity": "high",
            "title": "Overreach detected in latest run",
            "description": (
                f"The most recent run for '{component}' "
                f"(run_id={latest.get('run_id', '?')}) detected overreach. "
                f"The executor modified files or scope beyond the plan."
            ),
            "suggestion": (
                f"Add explicit scope locks for '{component}' in the "
                f"action plan. List allowed target_files and forbid "
                f"modifications outside the defined boundary."
            ),
            "action_type": "scope-lock",
            "run_id": latest.get("run_id"),
        }
    return None


def _rule_r5_high_volatility(
    component: str, stability_report: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    R5: High alignment volatility.

    If weighted_volatility > VOLATILITY_HIGH_THRESHOLD, suggest
    adding invariant tests for the component.
    """
    for comp in stability_report.get("components", []):
        if comp.get("component") != component:
            continue

        vol = comp.get(
            "weighted_volatility", comp.get("volatility", 0.0)
        )
        if vol > VOLATILITY_HIGH_THRESHOLD:
            return {
                "rule": "R5",
                "component": component,
                "severity": "medium",
                "title": "High alignment volatility",
                "description": (
                    f"Weighted volatility for '{component}' is {vol:.4f}, "
                    f"above the threshold of {VOLATILITY_HIGH_THRESHOLD}. "
                    f"Output quality is inconsistent across runs."
                ),
                "suggestion": (
                    f"Add targeted invariant tests for '{component}' to "
                    f"catch quality regressions early. Consider stricter "
                    f"contract enforcement rules."
                ),
                "action_type": "add-invariant-tests",
                "volatility": vol,
            }
    return None


def generate_healing_recommendations(
    run_id: Optional[str] = None,
    run_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Generate advisory healing recommendations for all known components.

    Inputs:
      - Drift ledger (cross-run history)
      - Stability report (metrics per component)
      - Regression report (pattern detection output)
      - Semantic report (if run_dir provided, latest run details)

    Writes healing_recommendations.json and returns the report.

    ADVISORY ONLY — no system state is modified.

    Args:
        run_id: Optional run identifier.
        run_dir: Optional path to the current run directory
                 (for reading semantic_report.json).

    Returns:
        Recommendations dict.
    """
    ledger_raw = _load_json(DRIFT_LEDGER_PATH)
    ledger = ledger_raw if isinstance(ledger_raw, list) else []
    stability_report = _load_json(STABILITY_REPORT_PATH)
    regression_report = _load_json(REGRESSION_REPORT_PATH)

    # Optionally load semantic report from run directory
    semantic_report: Dict[str, Any] = {}
    if run_dir and (run_dir / "semantic_report.json").exists():
        semantic_report = _load_json(run_dir / "semantic_report.json")

    # Discover all components from ledger + stability report
    components = set()
    for r in ledger:
        components.add(r.get("component", "Unknown"))
    for c in stability_report.get("components", []):
        components.add(c.get("component", "Unknown"))

    all_recommendations: List[Dict[str, Any]] = []
    component_summaries: List[Dict[str, Any]] = []

    for comp in sorted(components):
        comp_recs: List[Dict[str, Any]] = []

        # Apply each rule
        r1 = _rule_r1_repeated_drift(comp, ledger)
        if r1:
            comp_recs.append(r1)

        r2 = _rule_r2_low_stability(comp, stability_report)
        if r2:
            comp_recs.append(r2)

        r3 = _rule_r3_regression_detected(comp, regression_report)
        if r3:
            comp_recs.append(r3)

        r4 = _rule_r4_overreach(comp, ledger)
        if r4:
            comp_recs.append(r4)

        r5 = _rule_r5_high_volatility(comp, stability_report)
        if r5:
            comp_recs.append(r5)

        all_recommendations.extend(comp_recs)

        worst_severity = "none"
        for rec in comp_recs:
            s = rec.get("severity", "none")
            if s == "critical":
                worst_severity = "critical"
            elif s == "high" and worst_severity != "critical":
                worst_severity = "high"
            elif s == "medium" and worst_severity not in ("critical", "high"):
                worst_severity = "medium"

        component_summaries.append({
            "component": comp,
            "recommendations_count": len(comp_recs),
            "worst_severity": worst_severity,
            "recommendations": comp_recs,
        })

    report = {
        "generated_at": datetime.now().isoformat(),
        "run_id": run_id,
        "advisory_only": True,
        "total_recommendations": len(all_recommendations),
        "components": component_summaries,
        "recommendations": all_recommendations,
    }

    # Write artifact
    output_path = HISTORY_DIR / "healing_recommendations.json"
    if run_dir:
        output_path = run_dir / "healing_recommendations.json"

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8"
        )
        logger.info(
            f"Healing recommendations written ({len(all_recommendations)} "
            f"recommendation(s)): {output_path}"
        )
    except OSError as e:
        logger.warning(f"Failed to write healing recommendations: {e}")

    return report
