"""
validate_and_approve_jules.py
==============================
Standalone tool: fetch a Jules session, run semantic validation on
its changeSet, and (if ACCEPT) call the approval endpoint.

Usage:
    python scripts/validate_and_approve_jules.py --session 11650793064624646431
    python scripts/validate_and_approve_jules.py --session 11650793064624646431 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)


def _ok(msg: str):
    print(Fore.GREEN + f"  ✔ {msg}" + Style.RESET_ALL)


def _info(msg: str):
    print(Fore.CYAN + f"  ▶ {msg}" + Style.RESET_ALL)


def _warn(msg: str):
    print(Fore.YELLOW + f"  ⚠ {msg}" + Style.RESET_ALL)


def _fail(msg: str):
    print(Fore.RED + f"  ✘ {msg}" + Style.RESET_ALL)


def _section(title: str):
    bar = "─" * 60
    print(Fore.MAGENTA + f"\n{bar}\n  {title}\n{bar}" + Style.RESET_ALL)


# ─────────────────────────────────────────────────────────────
# 1. Fetch session payload
# ─────────────────────────────────────────────────────────────

def fetch_session(session_id: str) -> dict:
    from automation.jules_supervisor.cli_api import jules_api_get, jules_api_available
    if not jules_api_available():
        sys.exit("Jules API credentials not configured.")
    result = jules_api_get(f"sessions/{session_id}")
    if not result.get("ok"):
        sys.exit(f"Failed to fetch session: {result.get('error', result.get('status_code'))}")
    return result["data"]


# ─────────────────────────────────────────────────────────────
# 2. Extract changeset
# ─────────────────────────────────────────────────────────────

def extract_changeset(session: dict) -> dict:
    """Returns {diff, base_commit, commit_msg, source}, or exits."""
    from automation.jules_supervisor.pr_handler import extract_changeset_from_session
    cs = extract_changeset_from_session(session)
    if not cs or not cs.get("diff", "").strip():
        sys.exit("Session has no pending changeSet diff. Nothing to validate.")
    return cs


# ─────────────────────────────────────────────────────────────
# 3. Build intent from session prompt / title
# ─────────────────────────────────────────────────────────────

def build_intent_text(session: dict) -> str:
    title = session.get("title", "")
    prompt = session.get("prompt", "")
    # Extract the Detailed Instructions block from the prompt
    if "Detailed Instructions:" in prompt:
        after = prompt.split("Detailed Instructions:", 1)[1].strip()
        # Trim trailing noise (Relevant files section)
        for noise in ("\nRelevant files:", "\nFiles to implement"):
            if noise in after:
                after = after.split(noise, 0)[0].strip()
        return f"{title}\n{after}".strip()
    # Fallback: just use the first 800 chars of prompt
    return f"{title}\n{prompt[:800]}".strip()


def write_run_artifacts(run_id: str, session: dict, cs: dict) -> tuple[Path, Path, Path]:
    """
    Writes jules_diff.patch, human_intent.json, action_plan.json
    to automation/runs/{run_id}/. Returns (run_dir, intent_path, diff_path).
    """
    run_dir = PROJECT_ROOT / "automation" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # --- diff ---
    diff_path = run_dir / "jules_diff.patch"
    diff_path.write_text(cs["diff"], encoding="utf-8")

    # --- intent ---
    intent_text = build_intent_text(session)
    intent_path = run_dir / "human_intent.json"
    intent_data = {
        "run_id": run_id,
        "memory_change_summary": "Detected via Jules session changeset.",
        "user_intent": {
            "goal": session.get("title", "Jules task"),
            "expected_behavior_change": intent_text,
            "affected_layers": [],
            "risk_profile": "moderate",
            "non_goals": "Do not regress existing functionality.",
            "visual_expectations": "N/A",
            "constraints": "Ensure all tests pass.",
            "acceptance_signal": "Validation pipeline success.",
        },
        "auto_generated": True,
        "manually_modified": False,
        "original_intents": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    intent_path.write_text(json.dumps(intent_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- action_plan ---
    # Extract changed files from diff
    changed_files = []
    for line in cs["diff"].splitlines():
        if line.startswith("+++ b/"):
            f = line[6:].strip()
            if f and f != "/dev/null":
                changed_files.append(f)
    changed_files = list(dict.fromkeys(changed_files))

    plan_path = run_dir / "action_plan.json"
    action_plan = {
        "status": "ACTION_REQUIRED",
        "objective": session.get("title", "Jules task"),
        "target_files": changed_files,
        "target_components": [],
        "detailed_instructions": [intent_text],
        "forbidden_paths": ["docs/memory/**", ".git/**"],
        "context": {
            "intents": [{"concept": session.get("title", ""), "domain_level": "L3", "intent": intent_text, "source": "jules_session"}],
            "human_intent": intent_data,
        },
    }
    plan_path.write_text(json.dumps(action_plan, indent=2, ensure_ascii=False), encoding="utf-8")

    return run_dir, intent_path, changed_files


# ─────────────────────────────────────────────────────────────
# 4. Semantic validation
# ─────────────────────────────────────────────────────────────

def run_semantic_validation(run_id: str, intent_path: Path, action_plan: dict, changed_files: list, diff: str) -> dict:
    from automation.semantic.semantic_validator import SemanticValidator
    _info(f"Run ID: {run_id}")
    _info(f"Changed files: {changed_files}")
    _info(f"Diff size: {len(diff)} chars")

    validator = SemanticValidator(run_id, str(PROJECT_ROOT))
    report = validator.validate(
        str(intent_path),
        action_plan,
        changed_files,
        diff,
    )
    return report


# ─────────────────────────────────────────────────────────────
# 5. Approval
# ─────────────────────────────────────────────────────────────

def approve_session(session_id: str, dry_run: bool) -> None:
    if dry_run:
        _warn("DRY RUN — skipping approval API call.")
        return
    from automation.jules_supervisor.pr_handler import approve_jules_changeset, poll_for_pr_after_approval
    _info(f"Calling approve_jules_changeset for session {session_id}...")
    result = approve_jules_changeset(f"sessions/{session_id}")
    if result.get("ok"):
        _ok(f"Approval sent via {result.get('method')}")
        pr_url = result.get("pr_url")
        if pr_url:
            print(f"\n    ✔ PR created immediately: {pr_url}\n")
        else:
            _info("No PR URL in approval response — Jules creates PRs asynchronously. Polling (up to 120s)...")
            polled = poll_for_pr_after_approval(f"sessions/{session_id}", timeout=120, poll_interval=8)
            if polled:
                pr_url = polled["pr_url"]
                print(f"\n    ✔ PR created: {pr_url}\n")
            else:
                _warn("PR not yet visible after 120s — Jules may still be processing.")
                print(f"    Check manually: https://jules.google.com/session/{session_id}/")
    else:
        _fail(f"Approval failed: {result.get('error')}")
        print(f"    Raw result: {json.dumps(result, indent=4)}")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate and approve a Jules session changeSet.")
    parser.add_argument("--session", required=True, help="Jules session ID (numeric)")
    parser.add_argument("--dry-run", action="store_true", help="Skip the approval API call")
    parser.add_argument("--run-id", default=None, help="Override run ID (default: new UUID)")
    args = parser.parse_args()

    session_id = args.session.strip()
    run_id = args.run_id or str(uuid.uuid4())
    dry_run = args.dry_run

    _section("STEP 1: Fetch Jules Session")
    _info(f"Session: {session_id}")
    session = fetch_session(session_id)
    print(f"    state  : {session.get('state')}")
    print(f"    title  : {session.get('title')}")
    print(f"    updated: {session.get('updateTime')}")
    _ok("Session fetched.")

    if session.get("state") != "COMPLETED":
        _warn(f"Session state is '{session.get('state')}' — not COMPLETED. Proceeding anyway.")

    _section("STEP 2: Extract changeSet Diff")
    cs = extract_changeset(session)
    diff_lines = cs["diff"].splitlines()
    changed_files_from_diff = [l[6:].strip() for l in diff_lines if l.startswith("+++ b/") and l[6:].strip() != "/dev/null"]
    changed_files_from_diff = list(dict.fromkeys(changed_files_from_diff))
    print(f"    Diff size    : {len(cs['diff'])} chars")
    print(f"    Files changed: {changed_files_from_diff}")
    print(f"    Base commit  : {cs.get('base_commit')}")
    print(f"    Commit msg   : {(cs.get('commit_msg') or '')[:80]}")
    _ok("changeSet extracted.")

    _section("STEP 3: Write Run Artifacts")
    _info(f"Run dir: automation/runs/{run_id}")
    run_dir, intent_path, _ = write_run_artifacts(run_id, session, cs)
    _ok(f"Wrote jules_diff.patch, human_intent.json, action_plan.json")

    _section("STEP 4: Semantic Validation")
    action_plan = json.loads((run_dir / "action_plan.json").read_text(encoding="utf-8"))
    report = run_semantic_validation(run_id, intent_path, action_plan, changed_files_from_diff, cs["diff"])

    recommendation = report.get("recommendation", "UNKNOWN")
    intent_score = report.get("intent_match", report.get("alignment_score", 0.0))
    plan_score = report.get("plan_match", 0.0)

    print(f"\n    Recommendation : {recommendation}")
    print(f"    Intent match   : {intent_score}")
    print(f"    Plan match     : {plan_score}")
    violations = report.get("contract_violations", [])
    if violations:
        _warn(f"Contract violations ({len(violations)}):")
        for v in violations:
            print(f"      - {v}")

    summary_path = run_dir / "semantic_report.json"
    if summary_path.exists():
        print(f"    Full report    : automation/runs/{run_id}/semantic_report.json")

    _section("STEP 5: Decision")
    if recommendation == "ACCEPT":
        _ok("Semantic validation PASSED.")
        approve_session(session_id, dry_run)
    else:
        _fail(f"Semantic validation REJECTED: {recommendation}")
        reasoning = report.get("reasoning") or report.get("rejection_reason") or ""
        if reasoning:
            print(f"\n    Reason: {reasoning[:600]}")
        print(f"\n    See full report: automation/runs/{run_id}/semantic_alignment.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
