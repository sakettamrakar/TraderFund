from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from automation.jules_supervisor.cli_api import (
    jules_api_available,
    jules_api_get,
    jules_cli_available,
    run_cli_command,
)

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, default=str)


def _parse_int(pattern: str, text: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 0


def parse_jules_test_summary(test_output: str) -> Dict[str, Any]:
    """
    Parses test output into structured summary fields.
    """
    text = test_output or ""
    lower = text.lower()

    tests_total = _parse_int(r"collected\s+(\d+)\s+items", text)
    passed = _parse_int(r"(\d+)\s+passed", text)
    failed = _parse_int(r"(\d+)\s+failed", text)
    errors_count = _parse_int(r"(\d+)\s+error", text)

    if tests_total == 0 and (passed or failed):
        tests_total = passed + failed
    if tests_total == 0 and "all tests passed" in lower:
        tests_total = max(1, passed)
        passed = tests_total

    tests_failed = failed + errors_count
    coverage_match = re.search(r"coverage[^0-9]*([0-9]+(?:\.[0-9]+)?)\s*%", text, flags=re.IGNORECASE)
    coverage = float(coverage_match.group(1)) if coverage_match else None

    error_lines = []
    for line in text.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        lower_line = normalized.lower()
        if "error" in lower_line or "failed" in lower_line or "traceback" in lower_line:
            error_lines.append(normalized)
    error_lines = error_lines[:25]

    failure_rate = 0.0
    if tests_total > 0:
        failure_rate = round(tests_failed / tests_total, 4)

    return {
        "tests_total": tests_total,
        "tests_passed": passed,
        "tests_failed": tests_failed,
        "coverage": coverage,
        "errors": error_lines,
        "failure_rate": failure_rate,
        "tests_missing": tests_total == 0,
    }


def _extract_artifact_bundle(payload: Dict[str, Any]) -> Dict[str, str]:
    logs = _coerce_text(payload.get("logs"))
    diff = _coerce_text(payload.get("diff") or payload.get("patch"))
    tests = _coerce_text(payload.get("tests") or payload.get("test_summary"))

    artifacts = payload.get("artifacts")
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            kind = str(artifact.get("type", "")).lower()
            content = _coerce_text(artifact.get("content") or artifact.get("value"))
            if "log" in kind and not logs:
                logs = content
            elif ("diff" in kind or "patch" in kind) and not diff:
                diff = content
            elif "test" in kind and not tests:
                tests = content

    outputs = payload.get("outputs")
    if isinstance(outputs, list):
        for output in outputs:
            if not isinstance(output, dict):
                continue
            # Jules changeSet format: outputs[].changeSet.gitPatch.unidiffPatch
            change_set = output.get("changeSet") or output.get("change_set")
            if isinstance(change_set, dict) and not diff:
                git_patch = change_set.get("gitPatch") or change_set.get("git_patch")
                if isinstance(git_patch, dict):
                    patch_text = git_patch.get("unidiffPatch") or git_patch.get("patch")
                    if patch_text:
                        diff = _coerce_text(patch_text)

        if not logs:
            joined_outputs = "\n".join(_coerce_text(x) for x in outputs if x is not None)
            if joined_outputs:
                logs = joined_outputs

    return {"logs": logs, "diff": diff, "tests": tests}


def _collect_from_api(task_id: str) -> Dict[str, Any]:
    task_token = task_id.split("/")[-1]
    for endpoint in (f"tasks/{task_token}/artifacts", task_id, f"sessions/{task_token}", f"tasks/{task_token}"):
        response = jules_api_get(endpoint, timeout=30)
        if not response.get("ok"):
            continue
        data = response.get("data")
        if isinstance(data, dict):
            bundle = _extract_artifact_bundle(data)
            bundle["source_endpoint"] = endpoint
            return bundle
    return {"logs": "", "diff": "", "tests": "", "source_endpoint": None}


def _collect_cli_to_file(task_id: str, command: str, output_path: Path) -> Dict[str, Any]:
    result = run_cli_command(
        ["jules", command, task_id, "--out", str(output_path)],
        timeout=120,
    )
    if result.get("ok") and output_path.exists():
        return {"ok": True, "content": output_path.read_text(encoding="utf-8", errors="replace")}

    # Fallback to stdout mode if --out unsupported.
    raw = run_cli_command(["jules", command, task_id], timeout=120)
    if raw.get("ok"):
        content = raw.get("stdout", "")
        if content:
            output_path.write_text(content, encoding="utf-8")
        return {"ok": True, "content": content}
    return {"ok": False, "content": "", "error": raw.get("stderr") or result.get("stderr")}


def collect_jules_artifacts(task_id: str, run_id: str, task_status: Optional[str] = None) -> Dict[str, Any]:
    """
    Collect logs/diff/tests/patch artifacts into automation/runs/<run_id>/.
    """
    run_dir = Path("automation/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    logs_path = run_dir / "jules_logs.txt"
    diff_path = run_dir / "jules_diff.patch"
    tests_path = run_dir / "jules_tests.txt"
    info_path = run_dir / "jules_executor_info.json"
    summary_path = run_dir / "jules_test_summary.json"

    used_api = False
    used_cli = False
    errors: list[str] = []
    logs = ""
    diff = ""
    tests = ""

    if jules_api_available():
        api_bundle = _collect_from_api(task_id)
        logs = api_bundle.get("logs", "")
        diff = api_bundle.get("diff", "")
        tests = api_bundle.get("tests", "")
        used_api = bool(logs or diff or tests or api_bundle.get("source_endpoint"))

    if jules_cli_available() and (not logs or not diff or not tests):
        used_cli = True
        if not logs:
            cli_logs = _collect_cli_to_file(task_id, "fetch-logs", logs_path)
            logs = cli_logs.get("content", "") if cli_logs.get("ok") else logs
            if not cli_logs.get("ok") and cli_logs.get("error"):
                errors.append(f"fetch-logs: {cli_logs['error']}")
        if not diff:
            cli_diff = _collect_cli_to_file(task_id, "fetch-diff", diff_path)
            diff = cli_diff.get("content", "") if cli_diff.get("ok") else diff
            if not cli_diff.get("ok") and cli_diff.get("error"):
                errors.append(f"fetch-diff: {cli_diff['error']}")
        if not tests:
            cli_tests = _collect_cli_to_file(task_id, "fetch-tests", tests_path)
            tests = cli_tests.get("content", "") if cli_tests.get("ok") else tests
            if not cli_tests.get("ok") and cli_tests.get("error"):
                errors.append(f"fetch-tests: {cli_tests['error']}")

    # Always persist files (can be empty) for deterministic artifact shape.
    logs_path.write_text(logs or "", encoding="utf-8")
    diff_path.write_text(diff or "", encoding="utf-8")
    tests_path.write_text(tests or "", encoding="utf-8")

    test_summary = parse_jules_test_summary(tests or "")
    summary_path.write_text(json.dumps(test_summary, indent=2), encoding="utf-8")

    executor_info = {
        "task_id": task_id,
        "status_hint": task_status or "UNKNOWN",
        "collected_at": _utc_now(),
        "api_available": jules_api_available(),
        "cli_available": jules_cli_available(),
        "used_api": used_api,
        "used_cli": used_cli,
        "errors": errors,
        "artifacts": {
            "logs": str(logs_path),
            "diff": str(diff_path),
            "tests": str(tests_path),
            "test_summary": str(summary_path),
        },
    }
    info_path.write_text(json.dumps(executor_info, indent=2), encoding="utf-8")

    logger.info("Collector: artifacts stored in %s", run_dir)
    return {
        "task_id": task_id,
        "run_id": run_id,
        "logs_path": str(logs_path),
        "diff_path": str(diff_path),
        "tests_path": str(tests_path),
        "executor_info_path": str(info_path),
        "test_summary_path": str(summary_path),
        "test_summary": test_summary,
        "used_api": used_api,
        "used_cli": used_cli,
        "errors": errors,
    }


class ArtifactCollector:
    def __init__(self, run_id: str):
        self.run_id = run_id

    def collect(self, task_id: str, task_status: Optional[str] = None) -> Dict[str, Any]:
        return collect_jules_artifacts(task_id=task_id, run_id=self.run_id, task_status=task_status)
