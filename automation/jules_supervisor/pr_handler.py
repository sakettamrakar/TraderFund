"""
Pull Request detection and metadata handling for Jules runs.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import requests
except Exception:  # pragma: no cover - dependency guard
    requests = None

from automation.jules_supervisor.cli_api import (
    jules_api_available,
    jules_api_get,
    jules_cli_available,
    parse_cli_output,
    run_cli_command,
)

logger = logging.getLogger(__name__)

PR_URL_RE = re.compile(r"(https://github\.com/[^/]+/[^/]+/pull/\d+)")
SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b", flags=re.IGNORECASE)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_pr_metadata(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    pr_url = (
        raw.get("pr_url")
        or raw.get("url")
        or raw.get("pull_request_url")
    )
    if not pr_url:
        return None

    branch = raw.get("branch") or raw.get("head_branch") or raw.get("headRefName")
    commit_sha = raw.get("commit_sha") or raw.get("sha") or raw.get("head_sha")
    created_at = raw.get("created_at") or raw.get("createdAt") or _utc_now()

    metadata = {
        "pr_url": str(pr_url),
        "branch": str(branch) if branch else None,
        "commit_sha": str(commit_sha) if commit_sha else None,
        "created_at": str(created_at),
    }
    return metadata


def _extract_pr_from_text(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None

    url_match = PR_URL_RE.search(text)
    if not url_match:
        return None

    sha_match = SHA_RE.search(text)
    return {
        "pr_url": url_match.group(1),
        "branch": None,
        "commit_sha": sha_match.group(0) if sha_match else None,
        "created_at": _utc_now(),
    }


def _detect_pr_api(task_id: str) -> Optional[Dict[str, Any]]:
    task_token = task_id.split("/")[-1]
    candidate_paths = [
        f"tasks/{task_token}/pr",
        f"tasks/{task_token}",
        task_id,
        f"sessions/{task_token}",
    ]

    for path in candidate_paths:
        response = jules_api_get(path)
        if not response.get("ok"):
            continue
        payload = response.get("data")

        if isinstance(payload, dict):
            # Direct PR endpoint payload
            direct = _normalize_pr_metadata(payload)
            if direct:
                return direct

            # Session payload with outputs
            outputs = payload.get("outputs", [])
            if isinstance(outputs, list):
                for output in outputs:
                    if not isinstance(output, dict):
                        continue
                    pr_obj = output.get("pullRequest") or output.get("pull_request")
                    if isinstance(pr_obj, dict):
                        normalized = _normalize_pr_metadata(pr_obj)
                        if normalized:
                            return normalized

            text_candidate = json.dumps(payload)
            parsed = _extract_pr_from_text(text_candidate)
            if parsed:
                return parsed

    return None


def _detect_pr_cli(task_id: str) -> Optional[Dict[str, Any]]:
    commands = [
        ["jules", "list-prs", "--filter", f"task_id={task_id}", "--json"],
        ["jules", "list-prs", "--filter", f"task_id={task_id}"],
    ]

    for command in commands:
        result = run_cli_command(command, timeout=30)
        if not result.get("ok"):
            continue
        parsed = parse_cli_output(result.get("stdout", ""))

        if isinstance(parsed, dict):
            normalized = _normalize_pr_metadata(parsed)
            if normalized:
                return normalized

            items = parsed.get("items")
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    normalized_item = _normalize_pr_metadata(item)
                    if normalized_item:
                        return normalized_item

        text_pr = _extract_pr_from_text(result.get("stdout", ""))
        if text_pr:
            return text_pr

    return None


def detect_jules_pr(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Detect whether a Pull Request was created by Jules.
    API lookup first, CLI fallback.
    """
    if jules_api_available():
        pr = _detect_pr_api(task_id)
        if pr:
            return pr

    if jules_cli_available():
        pr = _detect_pr_cli(task_id)
        if pr:
            return pr

    return None


def persist_jules_pr(run_id: str, pr_metadata: Optional[Dict[str, Any]]) -> Path:
    """
    Persist PR metadata in automation/runs/<run_id>/jules_pr.json.
    """
    run_dir = Path("automation/runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    output_path = run_dir / "jules_pr.json"

    output_path.write_text(
        json.dumps(pr_metadata or {}, indent=2),
        encoding="utf-8",
    )
    return output_path


def fetch_pr_diff(pr_url: str) -> str:
    """
    Fetches .diff content from a PR URL.
    """
    if not pr_url or requests is None:
        return ""

    diff_url = pr_url if pr_url.endswith(".diff") else f"{pr_url}.diff"
    try:
        response = requests.get(diff_url, timeout=20)
        if response.status_code == 200:
            return response.text or ""
    except Exception as exc:
        logger.warning("Failed to fetch PR diff from %s: %s", diff_url, exc)
    return ""
