"""
Two-stage semantic merge controller for Jules PR lifecycle.

Flow:
1) Pre-merge semantic gate on PR diff.
2) Deterministic close-or-merge decision.
3) Post-merge follow-up semantic run.
4) Cross-run regression detection and drift penalty signal.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from automation.automation_config import config
from automation.history.drift_tracker import (
    append_run_record,
    compute_memory_hash,
    compute_plan_hash,
    generate_stability_report,
)
from automation.semantic.regression_detector import detect_regression
from automation.semantic.semantic_validator import SemanticValidator

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = PROJECT_ROOT / "automation" / "runs"
GITHUB_PR_RE = re.compile(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)")


def handle_pr_with_semantic(run_id: str, pr_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute deterministic pre-merge semantic gate and controlled merge.
    """
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    pre_report = _run_pre_merge_semantic(run_id, pr_info)
    pre_report["target_components"] = (
        (pr_info.get("action_plan") or {}).get("target_components", [])
        if isinstance(pr_info.get("action_plan"), dict)
        else []
    )
    pre_report["action_plan"] = pr_info.get("action_plan", {}) if isinstance(pr_info.get("action_plan"), dict) else {}
    pre_report["intent_source"] = pr_info.get("intent_source", "")
    pre_report["pr_info"] = {
        "pr_url": pr_info.get("pr_url"),
        "branch": pr_info.get("branch"),
        "commit_sha": pr_info.get("commit_sha"),
        "task_id": pr_info.get("task_id"),
    }

    _append_semantic_ledger_entries(
        run_id=run_id,
        plan=pre_report.get("action_plan", {}),
        report=pre_report,
        event_type="PRE_MERGE_SEMANTIC",
        regression_detected=False,
        regression_score_drop=0.0,
        clean_run=False,
    )
    generate_stability_report()

    pre_merge_path = run_dir / "pre_merge_semantic.json"
    pre_merge_path.write_text(json.dumps(pre_report, indent=2, default=str), encoding="utf-8")

    recommendation = str(pre_report.get("recommendation", "REJECT")).upper()
    pr_url = str(pr_info.get("pr_url") or "")

    if recommendation != "ACCEPT":
        close_result = _close_pr(pr_url, reason=f"Pre-merge semantic gate rejected ({recommendation}).")
        merge_result = {
            "timestamp": _utc_now(),
            "status": "REJECTED",
            "recommendation": recommendation,
            "pr_url": pr_url,
            "action": "CLOSE_PR",
            "close_result": close_result,
            "reason": "Pre-merge semantic recommendation was not ACCEPT.",
        }
        (run_dir / "merge_result.json").write_text(
            json.dumps(merge_result, indent=2, default=str),
            encoding="utf-8",
        )
        return {
            "success": False,
            "run_id": run_id,
            "recommendation": recommendation,
            "merged": False,
            "reason": merge_result["reason"],
            "merge_result": merge_result,
        }

    merge_result = _merge_pr(pr_url)
    merge_payload = {
        "timestamp": _utc_now(),
        "status": "MERGED" if merge_result.get("success") else "MERGE_FAILED",
        "recommendation": recommendation,
        "pr_url": pr_url,
        "action": "MERGE_PR",
        "merge_result": merge_result,
    }
    (run_dir / "merge_result.json").write_text(
        json.dumps(merge_payload, indent=2, default=str),
        encoding="utf-8",
    )

    if not merge_result.get("success"):
        return {
            "success": False,
            "run_id": run_id,
            "recommendation": recommendation,
            "merged": False,
            "reason": merge_result.get("error") or "PR merge failed.",
            "merge_result": merge_payload,
        }

    followup = None
    followup_error = None
    try:
        followup = spawn_followup_run(parent_run_id=run_id)
    except Exception as exc:
        followup_error = str(exc)
        logger.error("Follow-up run failed for parent run %s: %s", run_id, exc)
        failure_payload = {
            "timestamp": _utc_now(),
            "parent_run_id": run_id,
            "status": "FAILED",
            "error": followup_error,
        }
        (run_dir / "followup_failure.json").write_text(
            json.dumps(failure_payload, indent=2, default=str),
            encoding="utf-8",
        )

    return {
        "success": True,
        "run_id": run_id,
        "recommendation": recommendation,
        "merged": True,
        "followup_run_id": followup.get("run_id") if isinstance(followup, dict) else None,
        "followup_result": followup,
        "followup_status": "FAILED" if followup_error else "SUCCESS",
        "followup_error": followup_error,
        "merge_result": merge_payload,
    }


def spawn_followup_run(parent_run_id: str) -> Dict[str, Any]:
    """
    Spawn post-merge semantic-only follow-up run.
    """
    parent_dir = RUNS_DIR / parent_run_id
    pre_merge_path = parent_dir / "pre_merge_semantic.json"
    if not pre_merge_path.exists():
        raise RuntimeError(f"Missing pre-merge semantic artifact: {pre_merge_path}")

    pre_report = json.loads(pre_merge_path.read_text(encoding="utf-8"))

    new_run_id = f"{parent_run_id}_post_merge_{uuid.uuid4().hex[:8]}"
    run_dir = RUNS_DIR / new_run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Required parent linkage artifact.
    (run_dir / "parent_run.txt").write_text(
        f"{parent_run_id}\ntrigger_type: POST_MERGE_VALIDATION\n",
        encoding="utf-8",
    )

    # Optional explicit trigger marker for machine readers.
    (run_dir / "trigger_type.txt").write_text("POST_MERGE_VALIDATION\n", encoding="utf-8")

    post_report = _run_post_merge_semantic(
        run_id=new_run_id,
        parent_run_id=parent_run_id,
        pre_report=pre_report,
    )
    (run_dir / "post_merge_semantic.json").write_text(
        json.dumps(post_report, indent=2, default=str),
        encoding="utf-8",
    )

    tolerance = float(getattr(config, "SEMANTIC_REGRESSION_TOLERANCE", 0.03))
    regression = detect_regression(
        float(pre_report.get("final_score", 0.0)),
        float(post_report.get("final_score", 0.0)),
        tolerance=tolerance,
        pre_report=pre_report,
        post_report=post_report,
    )
    regression["parent_run_id"] = parent_run_id
    regression["run_id"] = new_run_id

    (run_dir / "regression_report.json").write_text(
        json.dumps(regression, indent=2, default=str),
        encoding="utf-8",
    )

    pre_accept = str(pre_report.get("recommendation", "")).upper() == "ACCEPT"
    post_overreach = bool((post_report.get("drift") or {}).get("overreach_detected", False))
    post_score = float(post_report.get("final_score", 0.0))
    pre_score = float(pre_report.get("final_score", 0.0))
    score_drop = max(0.0, pre_score - post_score)
    clean_run = bool(
        pre_accept
        and (not bool(regression.get("regression")))
        and (not post_overreach)
        and (post_score >= 0.90)
    )

    _append_semantic_ledger_entries(
        run_id=new_run_id,
        plan=pre_report.get("action_plan", {}),
        report=post_report,
        event_type="POST_MERGE_VALIDATION",
        regression_detected=bool(regression.get("regression")),
        regression_score_drop=score_drop,
        clean_run=clean_run,
    )
    generate_stability_report()

    return {
        "run_id": new_run_id,
        "parent_run_id": parent_run_id,
        "trigger_type": "POST_MERGE_VALIDATION",
        "regression": regression,
        "clean_run": clean_run,
        "success": True,
    }


def _run_pre_merge_semantic(run_id: str, pr_info: Dict[str, Any]) -> Dict[str, Any]:
    action_plan = pr_info.get("action_plan", {}) if isinstance(pr_info.get("action_plan"), dict) else {}
    intent_source = str(
        pr_info.get("intent_source")
        or action_plan.get("objective")
        or "Jules pre-merge semantic validation"
    )

    diff_text = _resolve_pr_diff(run_id, pr_info)
    changed_files = _resolve_changed_files(pr_info, diff_text)

    jules_context = pr_info.get("jules_context", {})
    if not isinstance(jules_context, dict):
        jules_context = {}

    validator = SemanticValidator(run_id=run_id, project_root=str(PROJECT_ROOT))
    return validator.validate(
        intent_file=intent_source,
        plan=action_plan,
        changed_files=changed_files,
        diff=diff_text,
        jules_context=jules_context,
        append_drift_ledger=False,
    )


def _run_post_merge_semantic(
    run_id: str,
    parent_run_id: str,
    pre_report: Dict[str, Any],
) -> Dict[str, Any]:
    action_plan = pre_report.get("action_plan")
    if not isinstance(action_plan, dict):
        action_plan = {
            "target_components": pre_report.get("target_components", []),
        }

    intent_source = str(pre_report.get("intent_source") or f"Post-merge validation for {parent_run_id}")
    changed_files = _git_changed_files_since_last_commit()
    diff_text = _git_last_commit_diff()

    jules_context = {
        "jules_pr": pre_report.get("jules_pr", pre_report.get("pr_info", {})),
        "jules_test_summary": pre_report.get("jules_test_summary", {}),
    }

    validator = SemanticValidator(run_id=run_id, project_root=str(PROJECT_ROOT))
    return validator.validate(
        intent_file=intent_source,
        plan=action_plan,
        changed_files=changed_files,
        diff=diff_text,
        jules_context=jules_context,
        append_drift_ledger=False,
    )


def _resolve_pr_diff(run_id: str, pr_info: Dict[str, Any]) -> str:
    provided = pr_info.get("diff")
    if isinstance(provided, str) and provided.strip():
        return provided

    run_dir = RUNS_DIR / run_id
    patch_path = run_dir / "jules_diff.patch"
    if patch_path.exists():
        text = patch_path.read_text(encoding="utf-8", errors="replace")
        if text.strip():
            return text

    pr_url = str(pr_info.get("pr_url") or "")
    # Only fetch diff from real GitHub PR URLs — not Jules session/task URLs
    if pr_url and GITHUB_PR_RE.match(pr_url):
        fetched = _fetch_pr_diff(pr_url)
        if fetched.strip():
            patch_path.write_text(fetched, encoding="utf-8")
            return fetched

    return ""


def _resolve_changed_files(pr_info: Dict[str, Any], diff_text: str) -> List[str]:
    extracted = _extract_changed_files_from_diff(diff_text)
    if extracted:
        return extracted
    provided = pr_info.get("changed_files")
    if isinstance(provided, list) and provided:
        return [str(x) for x in provided]
    return []


def _extract_changed_files_from_diff(diff_text: str) -> List[str]:
    files: List[str] = []
    if not diff_text:
        return files
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            candidate = line[6:].strip()
            if candidate and candidate != "/dev/null":
                files.append(candidate)
    # Keep order deterministic with de-dup.
    seen = set()
    ordered = []
    for path in files:
        if path in seen:
            continue
        seen.add(path)
        ordered.append(path)
    return ordered


def _merge_pr(pr_url: str) -> Dict[str, Any]:
    if not pr_url:
        return {"success": False, "method": "none", "error": "Missing PR URL."}

    if shutil.which("gh"):
        result = _run_command(["gh", "pr", "merge", pr_url, "--merge", "--delete-branch"], timeout=240)
        if result["returncode"] == 0:
            return {"success": True, "method": "gh", "stdout": result["stdout"]}
        combined = f"{result['stdout']} {result['stderr']}".lower()
        if "already merged" in combined:
            return {"success": True, "method": "gh", "stdout": result["stdout"], "stderr": result["stderr"]}

    api_result = _merge_pr_via_api(pr_url)
    if api_result.get("success"):
        return api_result

    return {
        "success": False,
        "method": "gh_or_api",
        "error": api_result.get("error") or "PR merge failed.",
    }


def _close_pr(pr_url: str, reason: str) -> Dict[str, Any]:
    if not pr_url:
        return {"success": False, "method": "none", "error": "Missing PR URL."}

    if shutil.which("gh"):
        result = _run_command(["gh", "pr", "close", pr_url, "--comment", reason], timeout=180)
        if result["returncode"] == 0:
            return {"success": True, "method": "gh", "stdout": result["stdout"]}

    api_result = _close_pr_via_api(pr_url)
    if api_result.get("success"):
        return api_result

    return {
        "success": False,
        "method": "gh_or_api",
        "error": api_result.get("error") or "PR close failed.",
    }


def _merge_pr_via_api(pr_url: str) -> Dict[str, Any]:
    if requests is None:
        return {"success": False, "error": "requests unavailable"}

    token = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    parsed = _parse_pr_url(pr_url)
    if not token or not parsed:
        return {"success": False, "error": "GitHub API token or PR URL parse missing."}

    owner, repo, number = parsed
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}/merge"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.put(url, headers=headers, json={"merge_method": "merge"}, timeout=30)
    if response.status_code in (200, 201):
        return {"success": True, "method": "github_api", "status_code": response.status_code}

    body = _safe_json(response)
    message = str(body.get("message", "")).lower()
    if "already merged" in message:
        return {"success": True, "method": "github_api", "status_code": response.status_code}

    return {
        "success": False,
        "method": "github_api",
        "status_code": response.status_code,
        "error": body.get("message") or response.text,
    }


def _close_pr_via_api(pr_url: str) -> Dict[str, Any]:
    if requests is None:
        return {"success": False, "error": "requests unavailable"}

    token = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    parsed = _parse_pr_url(pr_url)
    if not token or not parsed:
        return {"success": False, "error": "GitHub API token or PR URL parse missing."}

    owner, repo, number = parsed
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.patch(url, headers=headers, json={"state": "closed"}, timeout=30)
    if response.status_code in (200, 201):
        return {"success": True, "method": "github_api", "status_code": response.status_code}
    return {
        "success": False,
        "method": "github_api",
        "status_code": response.status_code,
        "error": response.text,
    }


def _parse_pr_url(pr_url: str) -> Optional[tuple[str, str, str]]:
    match = GITHUB_PR_RE.match(pr_url.strip())
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def _fetch_pr_diff(pr_url: str) -> str:
    if requests is None:
        return ""
    diff_url = pr_url if pr_url.endswith(".diff") else f"{pr_url}.diff"
    try:
        response = requests.get(diff_url, timeout=20)
        if response.status_code == 200:
            return response.text or ""
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to fetch PR diff from %s: %s", diff_url, exc)
    return ""


def _git_last_commit_diff() -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout or ""


def _git_changed_files_since_last_commit() -> List[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def _append_semantic_ledger_entries(
    run_id: str,
    plan: Dict[str, Any],
    report: Dict[str, Any],
    event_type: str,
    regression_detected: bool,
    regression_score_drop: float,
    clean_run: bool,
) -> None:
    target_components = plan.get("target_components", []) if isinstance(plan, dict) else []
    if not isinstance(target_components, list) or not target_components:
        target_components = ["General"]

    drift = report.get("drift", {}) if isinstance(report, dict) else {}
    if not isinstance(drift, dict):
        drift = {}

    drift_flags = _extract_drift_flags(drift)
    overreach = bool(drift.get("overreach_detected", False))
    missing_steps = len(drift.get("missing_requirements", [])) if isinstance(drift.get("missing_requirements"), list) else 0
    semantic_score = float(report.get("final_score", 0.0))
    recommendation = report.get("recommendation")
    plan_hash = compute_plan_hash(plan if isinstance(plan, dict) else {})
    memory_hash = compute_memory_hash(report.get("alignment", {}))

    for component in target_components:
        append_run_record(
            run_id=run_id,
            component=str(component),
            alignment_score=semantic_score,
            semantic_score=semantic_score,
            overreach_detected=overreach,
            missing_steps=missing_steps,
            drift_flags=drift_flags,
            plan_hash=plan_hash,
            memory_hash=memory_hash,
            recommendation=recommendation,
            regression_detected=bool(regression_detected),
            target_components=[str(c) for c in target_components],
            regression_score_drop=float(regression_score_drop),
            clean_run=bool(clean_run),
            event_type=event_type,
        )


def _extract_drift_flags(drift: Dict[str, Any]) -> List[str]:
    flags: List[str] = []
    if drift.get("overreach_detected"):
        flags.append("overreach")
    for key, prefix in (
        ("missing_requirements", "missing"),
        ("unintended_modifications", "unintended"),
        ("semantic_mismatch", "mismatch"),
    ):
        values = drift.get(key, [])
        if not isinstance(values, list):
            continue
        for item in values:
            flags.append(f"{prefix}:{str(item)[:60]}")
    return flags


def _run_command(command: List[str], timeout: int) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
        }
    except Exception as exc:
        return {"returncode": -1, "stdout": "", "stderr": str(exc)}


def _safe_json(response: Any) -> Dict[str, Any]:
    try:
        value = response.json()
        if isinstance(value, dict):
            return value
    except Exception:
        pass
    return {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
