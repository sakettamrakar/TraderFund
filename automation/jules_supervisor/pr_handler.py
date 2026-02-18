"""
Pull Request detection and metadata handling for Jules runs.
"""

from __future__ import annotations

import json
import logging
import re
import time
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
    jules_api_post,
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

    # Reject non-GitHub PR URLs (e.g. Jules session URLs like jules.google.com/session/...)
    if not PR_URL_RE.match(str(pr_url)):
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


def extract_changeset_from_session(session_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extracts a pending changeSet from a Jules session payload.

    Jules completes with outputs[].changeSet when the code is ready but
    not yet applied (awaiting approval). Returns a dict with:
        diff        — unified diff text
        base_commit — baseCommitId from the patch
        commit_msg  — suggestedCommitMessage
        source      — source repo
    Returns None if no changeSet is present.
    """
    outputs = session_payload.get("outputs", [])
    if not isinstance(outputs, list):
        return None

    for output in outputs:
        if not isinstance(output, dict):
            continue
        change_set = output.get("changeSet") or output.get("change_set")
        if not isinstance(change_set, dict):
            continue
        git_patch = change_set.get("gitPatch") or change_set.get("git_patch")
        if not isinstance(git_patch, dict):
            continue
        diff = git_patch.get("unidiffPatch") or git_patch.get("patch") or ""
        if not diff.strip():
            continue
        return {
            "diff": diff,
            "base_commit": git_patch.get("baseCommitId"),
            "commit_msg": git_patch.get("suggestedCommitMessage"),
            "source": change_set.get("source"),
        }
    return None


def post_jules_followup_message(session_id: str, fix_prompt: str) -> Dict[str, Any]:
    """
    Post a follow-up message to an existing Jules session, asking it to fix issues.

    Tries:
      1. POST /sessions/{id}/messages   (conversational follow-up)
      2. POST /sessions/{id}:resume     (resume with new prompt)
      3. POST /sessions/{id}:retry      (retry with amended prompt)

    Returns {ok, method, data, error}.
    """
    task_token = session_id.split("/")[-1]
    endpoints = [
        (f"sessions/{task_token}/messages", {"content": fix_prompt, "role": "user"}),
        (f"sessions/{task_token}:resume",   {"prompt": fix_prompt}),
        (f"sessions/{task_token}:retry",    {"prompt": fix_prompt}),
    ]

    for path, body in endpoints:
        if not jules_api_available():
            break
        response = jules_api_post(path, body=body)
        if response.get("ok"):
            logger.info("post_jules_followup_message: posted via %s", path)
            return {"ok": True, "method": path, "data": response.get("data", {})}
        logger.warning("post_jules_followup_message: %s returned %s", path, response.get("error"))

    return {
        "ok": False,
        "method": None,
        "error": "All follow-up endpoints failed or API unavailable.",
    }


def approve_jules_changeset(task_id: str) -> Dict[str, Any]:
    """
    Approve a Jules session's pending changeSet, triggering PR creation.

    Tries POST /sessions/{id}:apply, then :approve, then :submit as fallback.
    Returns a result dict with keys: ok, pr_url (if available), method, error.
    """
    task_token = task_id.split("/")[-1]
    apply_paths = [
        f"sessions/{task_token}:apply",
        f"sessions/{task_token}:approve",
        f"sessions/{task_token}:submit",
    ]

    for path in apply_paths:
        if not jules_api_available():
            break
        response = jules_api_post(path, body={})
        if not response.get("ok"):
            logger.warning("approve_jules_changeset: %s returned %s", path, response.get("error"))
            continue

        data = response.get("data") or {}
        # Extract PR URL from response if Jules returns it immediately
        pr_url = (
            data.get("pr_url")
            or data.get("url")
            or data.get("pull_request_url")
        )
        # Some responses nest inside pullRequest obj
        pr_obj = data.get("pullRequest") or data.get("pull_request")
        if isinstance(pr_obj, dict) and not pr_url:
            pr_url = pr_obj.get("url") or pr_obj.get("html_url")

        # Validate it's a real GitHub PR URL
        if pr_url and not PR_URL_RE.match(str(pr_url)):
            pr_url = None

        logger.info("approve_jules_changeset: applied via %s, pr_url=%s", path, pr_url)
        return {"ok": True, "pr_url": pr_url, "method": path, "data": data}

    return {
        "ok": False,
        "pr_url": None,
        "method": None,
        "error": "All apply endpoints failed or API unavailable.",
    }


def poll_for_pr_after_approval(
    task_id: str,
    timeout: int = 120,
    poll_interval: int = 8,
) -> Optional[Dict[str, Any]]:
    """
    After calling approve_jules_changeset(), Jules creates the PR asynchronously.
    Poll the session until a GitHub PR URL appears in the outputs, or timeout.

    Returns the PR metadata dict (with pr_url) on success, or None on timeout.
    """
    if not jules_api_available():
        return None

    task_token = task_id.split("/")[-1]
    path = f"sessions/{task_token}"
    deadline = time.monotonic() + timeout
    attempt = 0

    logger.info("poll_for_pr_after_approval: polling %s for up to %ss", path, timeout)

    while time.monotonic() < deadline:
        attempt += 1
        response = jules_api_get(path)
        if not response.get("ok"):
            time.sleep(poll_interval)
            continue

        payload = response.get("data") or {}

        # Check outputs for a pullRequest object
        for output in payload.get("outputs", []):
            if not isinstance(output, dict):
                continue
            pr_obj = output.get("pullRequest") or output.get("pull_request")
            if isinstance(pr_obj, dict):
                meta = _normalize_pr_metadata(pr_obj)
                if meta:
                    logger.info("poll_for_pr_after_approval: PR found after %d polls", attempt)
                    return meta

        # Also scan the entire payload as text for a GitHub PR URL
        text_pr = _extract_pr_from_text(json.dumps(payload))
        if text_pr:
            logger.info("poll_for_pr_after_approval: PR URL found in session text after %d polls", attempt)
            return text_pr

        logger.debug("poll_for_pr_after_approval: attempt %d — no PR yet, waiting %ss", attempt, poll_interval)
        time.sleep(poll_interval)

    logger.warning("poll_for_pr_after_approval: timed out after %ds with no PR URL", timeout)
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
