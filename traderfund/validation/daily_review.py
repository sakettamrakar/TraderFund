from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PHASES = ["ingestion", "memory", "research", "evaluation", "dashboard"]


def _load_latest_phase_summary(report_dir: Path, phase: str) -> Dict[str, Any] | None:
    candidates = sorted(report_dir.glob(f"{phase}_*_latest.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    for candidate in candidates:
        try:
            return json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
    return None


def _summarize_phase(summary: Dict[str, Any]) -> Dict[str, Any]:
    results = summary.get("results", [])
    statuses = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    failures: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for result in results:
        status = str(result.get("status", "")).upper()
        if status in statuses:
            statuses[status] += 1
        if status == "FAIL":
            failures.append(
                {
                    "task": result.get("name"),
                    "message": result.get("message", ""),
                    "details": result.get("details", {}),
                }
            )
        elif status == "SKIP":
            skipped.append(
                {
                    "task": result.get("name"),
                    "message": result.get("message", ""),
                }
            )

    return {
        "phase": summary.get("phase"),
        "hook": summary.get("hook"),
        "completed_at": summary.get("completed_at"),
        "has_failures": bool(summary.get("has_failures")),
        "status_counts": statuses,
        "failure_count": len(failures),
        "skip_count": len(skipped),
        "failures": failures,
        "skipped": skipped,
        "diagnosis_count": len(summary.get("diagnoses", [])),
        "remediation_count": len(summary.get("remediations", [])),
        "applied_remediation_count": len(summary.get("applied_remediations", [])),
    }


def _write_markdown_report(path: Path, report: Dict[str, Any]) -> None:
    lines = [
        "# Daily Validation Review",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Market: {report['market']}",
        f"- Overall status: {report['overall_status']}",
        f"- Missing phases: {', '.join(report['missing_phases']) if report['missing_phases'] else 'none'}",
        f"- Critical failure count: {report['critical_failure_count']}",
        f"- Attention item count: {report['attention_item_count']}",
        "",
        "## Phase Summary",
        "",
    ]

    for phase in report["phases"]:
        lines.extend(
            [
                f"### {phase['phase']}",
                "",
                f"- Hook: {phase['hook']}",
                f"- Completed at: {phase['completed_at']}",
                f"- Status counts: PASS={phase['status_counts']['PASS']}, FAIL={phase['status_counts']['FAIL']}, SKIP={phase['status_counts']['SKIP']}",
                f"- Diagnoses: {phase['diagnosis_count']}",
                f"- Remediations proposed: {phase['remediation_count']}",
                f"- Remediations applied: {phase['applied_remediation_count']}",
            ]
        )
        if phase["failures"]:
            lines.append("- Failures:")
            for failure in phase["failures"]:
                lines.append(f"  - {failure['task']}: {failure['message']}")
        if phase["skipped"]:
            lines.append("- Skips:")
            for skipped in phase["skipped"]:
                lines.append(f"  - {skipped['task']}: {skipped['message']}")
        lines.append("")

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def run_daily_validation_review(market: str = "US") -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    report_dir = repo_root / "logs" / "validation"
    output_dir = report_dir / "daily"
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()
    phases: List[Dict[str, Any]] = []
    missing_phases: List[str] = []
    critical_failures: List[Dict[str, Any]] = []
    attention_items: List[Dict[str, Any]] = []

    for phase_name in PHASES:
        summary = _load_latest_phase_summary(report_dir, phase_name)
        if summary is None:
            missing_phases.append(phase_name)
            continue
        phase_summary = _summarize_phase(summary)
        phases.append(phase_summary)
        for failure in phase_summary["failures"]:
            critical_failures.append({"phase": phase_name, **failure})
        for skipped in phase_summary["skipped"]:
            attention_items.append({"phase": phase_name, **skipped})

    if missing_phases:
        attention_items.extend({"phase": phase, "task": "missing_summary", "message": "No latest validation summary available."} for phase in missing_phases)

    overall_status = "PASS"
    if critical_failures:
        overall_status = "FAIL"
    elif missing_phases or attention_items:
        overall_status = "ATTENTION"

    report = {
        "generated_at": generated_at,
        "market": market,
        "overall_status": overall_status,
        "phase_count": len(phases),
        "phases": phases,
        "missing_phases": missing_phases,
        "critical_failure_count": len(critical_failures),
        "critical_failures": critical_failures,
        "attention_item_count": len(attention_items),
        "attention_items": attention_items,
    }

    date_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    json_path = output_dir / f"{date_key}_validation_review.json"
    latest_json_path = output_dir / "latest_validation_review.json"
    markdown_path = output_dir / f"{date_key}_validation_review.md"
    latest_markdown_path = output_dir / "latest_validation_review.md"

    payload = json.dumps(report, indent=2)
    json_path.write_text(payload, encoding="utf-8")
    latest_json_path.write_text(payload, encoding="utf-8")
    _write_markdown_report(markdown_path, report)
    _write_markdown_report(latest_markdown_path, report)

    if critical_failures:
        raise RuntimeError(f"Daily validation review found {len(critical_failures)} critical failures.")
    if missing_phases:
        raise RuntimeError(f"Daily validation review missing phase summaries: {', '.join(missing_phases)}")

    return {
        "status": "SUCCESS" if not attention_items else "NO_OP",
        "overall_status": overall_status,
        "report_path": str(json_path),
        "markdown_report_path": str(markdown_path),
        "attention_item_count": len(attention_items),
    }