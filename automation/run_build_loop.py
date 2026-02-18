"""
Autonomous Build Loop — Orchestrator
======================================
Execution mode: agents produce unified diffs and apply them to the working tree.

  spec_watcher → component_agent → test_agent → integration_agent →
  validation_agent → diff_summarizer → approval_gate

If any stage fails, the loop aborts immediately.
"""

import sys
import re
import time
import json
import subprocess
import argparse
from pathlib import Path
from colorama import init, Fore, Style
init()

# Force utf-8 output for Windows consoles/redirection
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

AUTOMATION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AUTOMATION_DIR.parent
# Ensure both automation directory and project root are in path
sys.path.insert(0, str(AUTOMATION_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

# New Imports
from automation_config import config, SecurityViolation
from journal import RunJournal

from planner.memory_diff import detect_commit_memory_changes, mark_commit_processed
from diff_summarizer import summarize
from approval_gate import approve
from agents import component_agent, test_agent, integration_agent, validation_agent

# Jules Integration
from automation.jules.adapter import JulesAdapter
from automation.jules_supervisor.monitor import TaskMonitor
from automation.jules_supervisor.artifact_collector import ArtifactCollector
from automation.jules_supervisor.cli_api import (
    jules_cli_available,
    parse_cli_output,
    run_cli_command,
)
from automation.jules_supervisor.pr_handler import (
    detect_jules_pr,
    fetch_pr_diff,
    persist_jules_pr,
    extract_changeset_from_session,
    approve_jules_changeset,
    post_jules_followup_message,
    poll_for_pr_after_approval,
)
from automation.jules_supervisor.result_summary import ResultSummary
from automation.merge_controller import handle_pr_with_semantic

# Intent Translation (Phase X)
from automation.intent.intent_translation import (
    save_intent_translation,
    load_intent_override,
)

PROTECTED_PATHS = ["docs/memory/", "docs/epistemic/"]


def _get_protected_dirty_files() -> set[str]:
    """Return the set of currently dirty files under protected paths."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            return set()
        changed = result.stdout.strip().splitlines()
    except FileNotFoundError:
        return set()

    return {
        f for f in changed
        if any(f.startswith(p) for p in PROTECTED_PATHS)
    }


def _check_invariant_violation(baseline: set[str]) -> str | None:
    """Check if an agent introduced NEW modifications to protected paths."""
    current = _get_protected_dirty_files()
    new_violations = current - baseline
    if new_violations:
        files = ", ".join(sorted(new_violations))
        return f"INVARIANT VIOLATION: Agent modified protected path(s): {files}"
    return None


def _stage_separator(label: str):
    print()
    print("─" * 60)
    print(f"  {label}")
    print("─" * 60)


def _abort(reason: str):
    """Print abort reason and exit. Also logs to journal."""
    print(f"\n  [ABORT] ABORTING LOOP: {reason}")
    print("=" * 60)

    if config.journal:
        config.journal.fail(reason)

    sys.exit(1)


def _run_modifying_agent(name: str, func, *args) -> str:
    """Run a modifying agent (component/test/integration) with guards."""
    _stage_separator(f"▶ {name}")
    baseline = _get_protected_dirty_files()
    t0 = time.time()

    try:
        output = func(*args)
    except SecurityViolation as sv:
        _abort(f"SECURITY VIOLATION in {name}: {sv}")
    except RuntimeError as e:
        elapsed = time.time() - t0
        print(f"  [TIME] {name} failed after {elapsed:.1f}s")
        _abort(f"{name} ERROR: {e}")
    except Exception as e:
        _abort(f"Unexpected error in {name}: {e}")

    elapsed = time.time() - t0
    print(f"  [TIME] {name} completed in {elapsed:.1f}s")

    if output and output.strip():
        print(f"  📄 {len(output)} chars of output.")
    else:
        print(f"  ⚪ {name}: no output generated.")
        output = ""

    # Invariant check — did the agent touch protected paths?
    # Note: diff_applier should have caught this, but double check is good.
    violation = _check_invariant_violation(baseline)
    if violation:
        # Log violation to journal
        if config.journal:
            config.journal.log_violation(violation)
        _abort(violation)

    return output

def _run_semantic_validation(run_id, intent_path, action_plan, changed_files, strict_mode, jules_context=None):
    """
    Runs the semantic validation pipeline.
    """
    _stage_separator("▶ Phase S: Semantic Validation")
    try:
        from automation.semantic.semantic_validator import SemanticValidator

        # Prefer Jules changeSet diff (stored by artifact collector) over local git diff.
        # When Jules completes with a changeSet it hasn't applied locally, git diff is
        # empty and we must use the Jules-supplied patch.
        diff = ""
        jules_patch_path = PROJECT_ROOT / "automation" / "runs" / run_id / "jules_diff.patch"
        if jules_patch_path.exists():
            candidate = jules_patch_path.read_text(encoding="utf-8", errors="replace").strip()
            # Only use if it looks like a real unified diff (reject HTML/session pages)
            if candidate.startswith("diff --git") or candidate.startswith("--- "):
                diff = candidate
                # Derive changed_files from the Jules diff so overreach detection
                # compares code files (not memory trigger files)
                extracted = []
                for line in diff.splitlines():
                    if line.startswith("+++ b/"):
                        f = line[6:].strip()
                        if f and f != "/dev/null":
                            extracted.append(f)
                if extracted:
                    changed_files = list(dict.fromkeys(extracted))  # deduplicated, ordered
                    print(Fore.CYAN + f"  ▶ Using Jules changeset diff ({len(changed_files)} files)" + Style.RESET_ALL)

        if not diff:
            try:
                diff_proc = subprocess.run(["git", "diff"], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
                diff = diff_proc.stdout
            except:
                diff = ""

        validator = SemanticValidator(run_id, str(PROJECT_ROOT))
        report = validator.validate(
            intent_path,
            action_plan,
            changed_files,
            diff,
            jules_context=jules_context,
        )

        # Phase AB: Visual validation integration
        _run_visual_validation_phase(run_id, action_plan, report)

        if strict_mode and (
            report.get("recommendation") != "ACCEPT"
            or report.get("strict_failure", False)
        ):
            _abort(f"Semantic Validation Failed (Strict Mode): {report.get('recommendation')}")
    except Exception as e:
        print(Fore.RED + f"  [FAIL] Semantic Validation crashed: {e}" + Style.RESET_ALL)
        if strict_mode:
            _abort("Semantic Validation crashed in strict mode.")


def _run_stability_check(run_id, action_plan):
    """
    Phase AB: Evaluate component stability and write decision artifact.
    """
    try:
        from automation.history.drift_tracker import compute_stability_index

        target_components = action_plan.get("target_components", [])
        if not target_components:
            print(Fore.GREEN + "  ✔ Stability: No target components — skipping." + Style.RESET_ALL)
            return

        component_indices = {}
        for comp in target_components:
            idx = compute_stability_index(comp)
            component_indices[comp] = idx

        worst_stability = min(component_indices.values()) if component_indices else 1.0

        if worst_stability < 0.60:
            execution_mode = "risk_controlled"
        elif worst_stability < 0.85:
            execution_mode = "guarded_autonomy"
        else:
            execution_mode = "normal"

        decision = {
            "worst_stability": round(worst_stability, 6),
            "components": target_components,
            "execution_mode": execution_mode,
        }

        run_dir = PROJECT_ROOT / "automation" / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        decision_path = run_dir / "stability_decision.json"
        decision_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")

        color = Fore.RED if execution_mode == "risk_controlled" else (
            Fore.YELLOW if execution_mode == "guarded_autonomy" else Fore.GREEN
        )
        print(color + f"  ✔ Stability: worst={worst_stability:.4f}, mode={execution_mode}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.YELLOW + f"  ⚠ Stability check failed (non-blocking): {e}" + Style.RESET_ALL)


def _run_visual_validation_phase(run_id, action_plan, semantic_report):
    """
    Phase AB: Run visual validation if UI components are touched.
    Applies penalty to semantic report if visual drift is detected.
    """
    try:
        from automation.visual.visual_validator import run_visual_validation

        visual_report = run_visual_validation(run_id, action_plan)
        if visual_report is None:
            return

        # Apply visual penalty to semantic report if needed
        visual_drift = visual_report.get("visual_drift", False)
        dom_passed = visual_report.get("dom_passed", True)

        if visual_drift or not dom_passed:
            original_score = semantic_report.get("final_score", 0.0)
            original_rec = semantic_report.get("recommendation", "REVIEW")

            total_penalty = 0.0
            semantic_report["explanation_tree"] = semantic_report.get("explanation_tree", [])
            if visual_drift:
                total_penalty += 0.15
                semantic_report["explanation_tree"].append(
                    "⚠ Visual drift detected (penalty=-0.15)"
                )
            if not dom_passed:
                total_penalty += 0.10
                semantic_report["explanation_tree"].append(
                    "⚠ DOM assertions failed (penalty=-0.10)"
                )

            adjusted_score = max(0.0, round(original_score - total_penalty, 4))
            semantic_report["final_score"] = adjusted_score
            semantic_report["visual_penalty_applied"] = round(total_penalty, 4)

            # Downgrade-only recommendation — never upgrade, never override hard REJECT
            if adjusted_score >= 0.85:
                new_rec = "ACCEPT"
            elif adjusted_score >= 0.60:
                new_rec = "REVIEW"
            else:
                new_rec = "REJECT"

            REC_RANK = {"ACCEPT": 0, "REVIEW": 1, "REJECT": 2}
            if REC_RANK.get(new_rec, 0) > REC_RANK.get(original_rec, 0):
                semantic_report["recommendation"] = new_rec

            # Rewrite updated semantic report
            run_dir = PROJECT_ROOT / "automation" / "runs" / run_id
            report_path = run_dir / "semantic_report.json"
            if report_path.exists():
                report_path.write_text(
                    json.dumps(semantic_report, indent=2, default=str),
                    encoding="utf-8",
                )

            print(Fore.YELLOW + f"  ⚠ Visual penalty applied: -{total_penalty} → score={adjusted_score:.4f}" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "  ✔ Visual validation passed — no penalty." + Style.RESET_ALL)
    except ImportError:
        print(Fore.YELLOW + "  ⚠ Visual validator not available — skipping." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.YELLOW + f"  ⚠ Visual validation failed (non-blocking): {e}" + Style.RESET_ALL)


def create_jules_task(changed_files, action_plan=None):
    """
    Creates a Jules task.
    API path is preferred; CLI path is used as fallback.
    """
    adapter = JulesAdapter()
    task_id = config.journal.run_id

    # Extract rich title from action plan context
    title = "Automated Build Loop Task"
    if action_plan:
        # Try finding the user intent goal first (most descriptive)
        try:
            title = action_plan["context"]["human_intent"]["user_intent"]["goal"]
        except (KeyError, TypeError):
            # Fallback to objective
            title = action_plan.get("objective", title)
    
    # Ensure title isn't too long for API (if applicable, but good practice)
    if len(title) > 200:
        title = title[:197] + "..."

    task_data = {
        "task_id": task_id,
        "changed_memory_files": changed_files,
        "purpose": action_plan.get("objective") if action_plan else "Automated Build Loop Task",
        "title": title,
    }

    instructions = "Please address the following changes:\n"
    if action_plan:
        instructions += f"Objective: {action_plan.get('objective')}\n"
        if action_plan.get("detailed_instructions"):
            instructions += "Detailed Instructions:\n"
            for instr in action_plan.get("detailed_instructions", []):
                instructions += f"- {instr}\n"
    else:
        instructions += "Please implement changes based on the modified files provided.\n"

    # List target code files from the action plan (not the memory trigger files that
    # Jules would mistakenly interpret as files to modify).
    _protected = ("docs/memory/", "docs/epistemic/")
    target_files = (
        action_plan.get("target_files", []) if action_plan else []
    )
    code_refs = [f for f in (target_files or []) if not any(f.startswith(p) for p in _protected)]
    # Fall back to changed_files only when no code target_files, but never include protected paths.
    if not code_refs:
        code_refs = [f for f in changed_files if not any(f.startswith(p) for p in _protected)]
    if code_refs:
        instructions += "\nFiles to implement changes in:\n" + "\n".join(code_refs)
    else:
        instructions += "\nPlease create or modify the appropriate Python source files to implement this."

    # Explicit guard — Jules must never touch memory or documentation folders.
    instructions += (
        "\n\nFORBIDDEN — Do NOT create, modify, or delete any files under:\n"
        "  - docs/memory/\n"
        "  - docs/epistemic/\n"
        "  - docs/ (any subdirectory)\n"
        "  - .git/\n"
        "Only modify source code files (src/, tests/, traderfund/, or similar Python modules). "
        "Memory files are read-only reference documents; they must never be committed as part of this task."
    )

    print(f"  Creating Jules task {task_id}...")
    try:
        payload = adapter.create_job(task_data, instructions)
        job_id = adapter.submit_job(payload)
        print(f"  Jules Job Submitted: {job_id}")
        _save_last_jules_session(job_id)
        return job_id
    except Exception as exc:
        print(f"  Jules API submission failed: {exc}")

    if not jules_cli_available():
        raise RuntimeError("Jules API submission failed and Jules CLI is unavailable.")

    cli_attempts = [
        ["jules", "create-task", "--task-id", task_id, "--prompt", instructions, "--json"],
        ["jules", "submit", "--task-id", task_id, "--prompt", instructions, "--json"],
        ["jules", "submit", "--task-id", task_id, "--prompt", instructions],
    ]

    for command in cli_attempts:
        result = run_cli_command(command, timeout=120)
        if not result.get("ok"):
            continue

        parsed = parse_cli_output(result.get("stdout", ""))
        cli_job_id = None
        if isinstance(parsed, dict):
            cli_job_id = (
                parsed.get("task_id")
                or parsed.get("id")
                or parsed.get("name")
                or parsed.get("session")
            )

        if not cli_job_id:
            stdout = (result.get("stdout") or "").strip()
            for token in stdout.replace("\n", " ").split():
                if "/" in token and ("sessions/" in token or "tasks/" in token):
                    cli_job_id = token.strip()
                    break

        if cli_job_id:
            print(f"  Jules Job Submitted via CLI: {cli_job_id}")
            _save_last_jules_session(str(cli_job_id))
            return str(cli_job_id)

    raise RuntimeError("Jules CLI fallback submission failed.")


# ─────────────────────────────────────────────────────────────────────────────
# Jules session helpers
# ─────────────────────────────────────────────────────────────────────────────

_LAST_SESSION_FILE = AUTOMATION_DIR / "history" / "last_jules_session.txt"


def _save_last_jules_session(session_id: str) -> None:
    """Persist the most recently submitted Jules session ID."""
    try:
        _LAST_SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        _LAST_SESSION_FILE.write_text(session_id.strip(), encoding="utf-8")
    except OSError as exc:
        print(Fore.YELLOW + f"  ⚠ Could not save last Jules session: {exc}" + Style.RESET_ALL)


def _load_last_jules_session() -> str | None:
    """Return the last saved Jules session ID, or None."""
    try:
        if _LAST_SESSION_FILE.exists():
            val = _LAST_SESSION_FILE.read_text(encoding="utf-8").strip()
            return val or None
    except OSError:
        pass
    return None


def _build_fix_prompt(report: dict, intent: str, diff: str) -> str:
    """
    Construct a precise fix prompt to post back to Jules when semantic
    validation rejects or flags the changeset.

    The prompt explains:
      - What was wrong (violations, mismatches)
      - What must be fixed
      - Explicit constraint that memory/docs files are NOT to be touched
    """
    issues = []

    contract_violations = report.get("contract_violations", [])
    for v in contract_violations:
        sev = v.get("severity", "")
        msg = v.get("message") or v.get("file") or str(v)
        issues.append(f"[CONTRACT {sev}] {msg}")

    for m in report.get("drift", {}).get("missing_requirements", []):
        issues.append(f"[MISSING] {m}")

    for u in report.get("drift", {}).get("unintended_modifications", []):
        issues.append(f"[UNINTENDED] {u}")

    for s in report.get("drift", {}).get("semantic_mismatch", []):
        issues.append(f"[MISMATCH] {s}")

    # Flatten nested report structure too
    for v in report.get("violations", []):
        msg = v if isinstance(v, str) else v.get("message", str(v))
        if msg not in issues:
            issues.append(f"[VIOLATION] {msg}")

    issues_text = "\n".join(f"  - {i}" for i in issues) if issues else "  - Review failed without specific issue details."

    return (
        "The previous implementation was reviewed by the automated semantic validation pipeline "
        "and was NOT accepted. Please fix the following issues:\n\n"
        f"{issues_text}\n\n"
        f"Original intent:\n{intent[:600]}\n\n"
        "Requirements:\n"
        "  1. Fix only the listed issues — do not change unrelated code.\n"
        "  2. All existing tests must continue to pass.\n"
        "  3. FORBIDDEN — do NOT modify any file under: docs/, docs/memory/, docs/epistemic/, .git/\n"
        "  4. Only modify source code files (src/, tests/, traderfund/, or similar Python modules).\n"
        "  5. Submit an updated changeSet for review."
    )


def main():
    parser = argparse.ArgumentParser(description="Autonomous Build Loop")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without side effects")
    parser.add_argument("--jules", action="store_true", help="Use Jules executor with supervisor")
    parser.add_argument("--retrigger-from-intent", action="store_true", help="Skip memory diff and use existing human intent")
    parser.add_argument("--strict-semantic", action="store_true", help="Fail run if semantic validation does not ACCEPT")
    parser.add_argument(
        "--session",
        default=None,
        metavar="SESSION_ID",
        help=(
            "Skip Jules task creation and validate/approve an existing session. "
            "Use this when re-triggering to avoid creating a garbage new task. "
            "If omitted but --retrigger-from-intent is set, the last saved session is used automatically."
        ),
    )
    parser.add_argument("--fix-retries", type=int, default=2, metavar="N",
                        help="Max times to post a fix message to Jules and re-validate (default: 2)")
    args = parser.parse_args()

    # Initialize Config & Journal
    config.dry_run = args.dry_run
    config.journal = RunJournal(dry_run=args.dry_run)

    print("=" * 60)
    print("  AUTONOMOUS BUILD LOOP — EXECUTION MODE")
    if config.dry_run:
        print("  🚧 DRY RUN MODE ACTIVE 🚧")
    print(f"  Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Run ID: {config.journal.run_id}")
    print("=" * 60)

    try:
        # ── Stage 1: Spec Change Detection ──────────────────────────
        _stage_separator("[1/6] Spec Change Detection")

        trigger_state = detect_commit_memory_changes()
        memory_changed = bool(trigger_state.get("changed"))
        changed_files = list(trigger_state.get("changed_files", []))
        pending_commit_for_update = trigger_state.get("pending_commit")
        fallback_to_snapshot = bool(trigger_state.get("fallback_to_snapshot"))

        if memory_changed and not fallback_to_snapshot:
            print(Fore.YELLOW + "  Commit-based memory change detected" + Style.RESET_ALL)
            print(Fore.YELLOW + f"  Changed files: {changed_files}" + Style.RESET_ALL)
        elif fallback_to_snapshot:
            trigger_error = trigger_state.get("error", "unknown git error")
            print(Fore.YELLOW + f"  Commit trigger unavailable; using snapshot fallback ({trigger_error})." + Style.RESET_ALL)
        elif args.retrigger_from_intent:
            print(Fore.MAGENTA + "  Retrigger requested; bypassing commit trigger gate." + Style.RESET_ALL)

        # When re-triggering, auto-resolve an existing session to avoid creating
        # a new garbage task. --session takes precedence; fallback to last saved.
        _reuse_session: str | None = None
        if args.retrigger_from_intent or args.session:
            explicit = args.session or _load_last_jules_session()
            if explicit:
                _reuse_session = explicit
                print(Fore.MAGENTA + f"  ↩ Re-trigger: will reuse existing Jules session {_reuse_session}" + Style.RESET_ALL)
                print(Fore.MAGENTA + "    (Skipping new task creation — validating existing session directly)" + Style.RESET_ALL)
            elif args.session:
                print(Fore.YELLOW + "  ⚠ --session flag given but no session ID found." + Style.RESET_ALL)

        if not memory_changed and not args.retrigger_from_intent and not _reuse_session:
            print("  No new memory commits detected. Exiting cleanly.")
            config.journal.finish()
            sys.exit(0)

        config.journal.set_changed_specs(changed_files)
        print(f"  Detected changes in {len(changed_files)} memory files.")
        for s in changed_files:
            print(f"    → {s}")

        # ------------------------------------------------------------------
        # PHASE M: SEMANTIC IMPACT PLANNING
        # ------------------------------------------------------------------

        human_intent_path = None

        if args.retrigger_from_intent:
            print(Fore.MAGENTA + "  ▶ Plan: Retriggering from existing intent..." + Style.RESET_ALL)
            # Find latest intent
            cmd = ["python", "automation/intent/intent_loader.py", "--find-latest"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.stdout.strip():
                human_intent_path = res.stdout.strip()
                print(f"    Found intent: {human_intent_path}")
            else:
                _abort("No existing intent found for retriggering.")
        else:
            # 0. Run Memory Diff Analyzer
            print(Fore.CYAN + "  ▶ Plan: Analyzing Memory Diffs..." + Style.RESET_ALL)
            subprocess.run(["python", "automation/planner/memory_diff.py", "--save", "--output", "automation/tasks/memory_diff.json"], check=False)

            # 1. Run Intent Extractor
            print(Fore.CYAN + "  ▶ Plan: Extracting Intent..." + Style.RESET_ALL)
            subprocess.run(["python", "automation/planner/intent_extractor.py", "--input", "automation/tasks/memory_diff.json", "--output", "automation/tasks/intent.json"], check=False)

            # 1.5 Run Human Intent Translator
            print(Fore.CYAN + "  ▶ Plan: Translating to Human Intent..." + Style.RESET_ALL)
            human_intent_path = f"automation/runs/{config.journal.run_id}/human_intent.json"
            subprocess.run([
                "python", "automation/intent/translator.py",
                "--intent", "automation/tasks/intent.json",
                "--diff", "automation/tasks/memory_diff.json",
                "--run-id", config.journal.run_id,
                "--output", human_intent_path
            ], check=False)

        # 2. Run Impact Resolver
        print(Fore.CYAN + "  ▶ Plan: Resolving Component Impact..." + Style.RESET_ALL)
        cmd_impact = ["python", "automation/planner/impact_resolver.py", "--intent", "automation/tasks/intent.json", "--output", "automation/tasks/impact.json"]
        if human_intent_path:
            cmd_impact.extend(["--human-intent", human_intent_path])
        subprocess.run(cmd_impact, check=False)

        # 3. Generate Action Plan
        print(Fore.CYAN + "  ▶ Plan: Generating Action Plan..." + Style.RESET_ALL)
        cmd_plan = ["python", "automation/planner/action_plan.py", "--impact", "automation/tasks/impact.json", "--output", "automation/tasks/action_plan.json"]
        if human_intent_path:
            cmd_plan.extend(["--human-intent", human_intent_path])
        plan_result = subprocess.run(cmd_plan, check=False)
        if plan_result.returncode != 0:
            _abort("Action Plan generation failed.")

        # Load Action Plan
        action_plan_path = Path("automation/tasks/action_plan.json")
        if not action_plan_path.exists():
            _abort("Action Plan generation failed: output file missing.")
        try:
            action_plan = json.loads(action_plan_path.read_text(encoding="utf-8"))
        except Exception as e:
            _abort(f"Action Plan generation failed: invalid JSON ({e})")

        # Commit baseline advances only after action plan generation succeeds.
        if pending_commit_for_update:
            try:
                mark_commit_processed(pending_commit_for_update)
            except Exception as e:
                _abort(f"Failed to persist commit trigger state: {e}")

        if action_plan.get("status") == "NO_ACTION_REQUIRED":
            print(Fore.GREEN + "  ✔ Plan: No semantic changes requiring code updates." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"  ⚠ Plan: {action_plan.get('objective')}" + Style.RESET_ALL)
            for instr in action_plan.get('detailed_instructions', []):
                print(Fore.YELLOW + f"    - {instr}" + Style.RESET_ALL)

        # ------------------------------------------------------------------
        # PHASE X: INTENT TRANSLATION + OVERRIDE DETECTION
        # ------------------------------------------------------------------
        # Save intent translation BEFORE execution begins
        print(Fore.CYAN + "  ▶ Phase X: Saving Intent Translation..." + Style.RESET_ALL)
        try:
            # Load memory diffs and intents for translation
            _memory_diffs = []
            _intents = []
            _diff_file = Path("automation/tasks/memory_diff.json")
            _intent_file = Path("automation/tasks/intent.json")
            if _diff_file.exists():
                try:
                    _memory_diffs = json.loads(_diff_file.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    pass
            if _intent_file.exists():
                try:
                    _intents = json.loads(_intent_file.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    pass

            _target_components = action_plan.get("target_components", [])

            _human_intent_data = None
            if human_intent_path and Path(human_intent_path).exists():
                try:
                    _human_intent_data = json.loads(
                        Path(human_intent_path).read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError):
                    pass

            save_intent_translation(
                run_id=config.journal.run_id,
                memory_changes=_memory_diffs if isinstance(_memory_diffs, list) else [],
                intents=_intents if isinstance(_intents, list) else [],
                target_components=_target_components,
                human_intent=_human_intent_data,
            )
            print(Fore.GREEN + "  ✔ Intent translation saved." + Style.RESET_ALL)
        except Exception as e:
            # Non-blocking — do not abort on translation failure
            print(Fore.YELLOW + f"  ⚠ Intent translation save failed (non-blocking): {e}" + Style.RESET_ALL)

        # Check for human intent override
        intent_override = load_intent_override(config.journal.run_id)
        if intent_override:
            print(Fore.MAGENTA + "  ▶ Intent Override Detected — applying corrected intent." + Style.RESET_ALL)

            # Rebuild action plan with override content
            corrected = intent_override.get("corrected_intent", "")
            clarifications = intent_override.get("clarifications", "")
            scope_limits = intent_override.get("scope_limits", "")

            override_instructions = []
            if corrected:
                override_instructions.append(f"Corrected Intent: {corrected}")
            if clarifications:
                override_instructions.append(f"Clarifications: {clarifications}")
            if scope_limits:
                override_instructions.append(f"Scope Limits: {scope_limits}")

            if override_instructions:
                action_plan["detailed_instructions"] = override_instructions
                action_plan["objective"] = corrected or action_plan.get("objective", "")
                action_plan["context"] = action_plan.get("context", {})
                action_plan["context"]["intent_override"] = intent_override

                action_plan["status"] = "ACTION_REQUIRED"  # Force action on override

                # Persist the corrected action plan
                action_plan_path.write_text(
                    json.dumps(action_plan, indent=2), encoding="utf-8"
                )
                print(Fore.MAGENTA + f"  ✔ Action plan updated with override content." + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "  ✔ No intent override — proceeding with auto-extracted intent." + Style.RESET_ALL)

        if action_plan.get("status") == "NO_ACTION_REQUIRED":
            print(Fore.GREEN + "  ✔ No semantic changes or overrides. Exiting build loop." + Style.RESET_ALL)
            config.journal.finish()
            sys.exit(0)

        # ------------------------------------------------------------------
        # JULES EXECUTION PATH
        # Auto-detect: if JULES_API_KEY is available, use Jules path
        # ------------------------------------------------------------------
        use_jules = args.jules
        if not use_jules:
            try:
                from automation.jules.config import JULES_API_KEY
                if JULES_API_KEY and JULES_API_KEY != "MOCK":
                    use_jules = True
                    print(Fore.CYAN + "  ▶ Jules API key detected — auto-activating Jules execution path." + Style.RESET_ALL)
            except ImportError:
                pass

        if use_jules:
            _stage_separator("▶ JULES SUPERVISED EXECUTION")

            # Phase AB: Stability check before Jules dispatch
            _run_stability_check(config.journal.run_id, action_plan)

            if _reuse_session:
                # Re-trigger path: skip task creation — reuse existing session
                print(Fore.MAGENTA + f"  ↩ Reusing session: {_reuse_session}" + Style.RESET_ALL)
                task_id = _reuse_session
            else:
                task_id = create_jules_task(changed_files, action_plan)

            monitor = TaskMonitor(config.journal.run_id)
            monitor_result = monitor.wait(task_id)
            task_status = monitor_result.get("status", "UNKNOWN")
            print(Fore.CYAN + f"  Jules monitor status: {task_status}" + Style.RESET_ALL)

            collector = ArtifactCollector(config.journal.run_id)
            artifacts = collector.collect(task_id, task_status=task_status)

            run_dir = PROJECT_ROOT / "automation" / "runs" / config.journal.run_id
            diff_path = run_dir / "jules_diff.patch"

            # ── Detect what Jules produced ────────────────────────────────
            # Case A: session has a pending changeSet (code ready, awaiting approval)
            # Case B: Jules already created a GitHub PR
            # Case C: neither — fall through to local semantic only

            session_payload = monitor_result.get("payload") or {}
            pending_changeset = extract_changeset_from_session(session_payload)

            # PR detection (API first, CLI fallback)
            pr_metadata = detect_jules_pr(task_id)
            persist_jules_pr(config.journal.run_id, pr_metadata)

            _github_pr_re = re.compile(r"https://github\.com/[^/]+/[^/]+/pull/\d+")
            _pr_url = (pr_metadata or {}).get("pr_url", "")
            _has_real_github_pr = bool(_pr_url and _github_pr_re.match(str(_pr_url)))

            # If artifact collector already wrote the changeset diff, prefer it.
            # If not, write it from the session payload directly.
            if pending_changeset and not (
                diff_path.exists()
                and diff_path.read_text(encoding="utf-8", errors="replace").strip().startswith("diff --git")
            ):
                diff_path.write_text(pending_changeset["diff"], encoding="utf-8")
                print(Fore.CYAN + "  ▶ Jules changeSet diff extracted from session payload." + Style.RESET_ALL)

            if _has_real_github_pr:
                # Fetch diff from the GitHub PR if not already populated
                if not diff_path.exists() or not diff_path.read_text(encoding="utf-8", errors="replace").strip():
                    pr_diff = fetch_pr_diff(pr_metadata["pr_url"])
                    if pr_diff:
                        diff_path.write_text(pr_diff, encoding="utf-8")

            jules_context = {
                "task_id": task_id,
                "task_status": task_status,
                "monitor_result": monitor_result,
                "did_pr_exist": _has_real_github_pr,
                "jules_pr": pr_metadata or {},
                "jules_test_summary": artifacts.get("test_summary", {}),
                "jules_artifacts": artifacts,
                "pending_changeset": pending_changeset,
            }

            summary_gen = ResultSummary(config.journal.run_id)
            summary_gen.generate()

            merge_control_result = None

            if pending_changeset and not _has_real_github_pr:
                # ── Case A: changeSet awaiting approval ─── with fix loop ──
                print(Fore.CYAN + "  ▶ Jules changeSet pending approval — running semantic gate..." + Style.RESET_ALL)

                _sem_report_path = run_dir / "semantic_report.json"
                _sem_recommendation = "UNKNOWN"
                _sem_report: dict = {}
                _fix_attempt = 0
                _max_fix_retries = args.fix_retries  # default 2

                while True:
                    # strict_mode=False — Case A owns the abort decision via the fix loop below
                    _run_semantic_validation(
                        config.journal.run_id,
                        human_intent_path,
                        action_plan,
                        changed_files,
                        strict_mode=False,
                        jules_context=jules_context,
                    )

                    if _sem_report_path.exists():
                        try:
                            _sem_report = json.loads(_sem_report_path.read_text(encoding="utf-8"))
                            _sem_recommendation = _sem_report.get("recommendation", "UNKNOWN").upper()
                        except (json.JSONDecodeError, OSError):
                            _sem_recommendation = "UNKNOWN"

                    if _sem_recommendation == "ACCEPT":
                        break

                    # Determine if errors are genuine (code defects) vs overreach/abort
                    _contract_violations = _sem_report.get("contract_violations", [])
                    _high_violations = [v for v in _contract_violations if v.get("severity") == "HIGH"]

                    # Overreach (touching protected files) → do not retry, abort
                    if any(
                        "CONSTRAINT_BREAK" in str(v) or "protected" in str(v).lower()
                        for v in _high_violations
                    ):
                        print(Fore.RED + "  ✘ Contract violation: protected path modification detected — will not retry." + Style.RESET_ALL)
                        break

                    if _fix_attempt >= _max_fix_retries:
                        print(Fore.YELLOW + f"  ⚠ Max fix retries ({_max_fix_retries}) exhausted." + Style.RESET_ALL)
                        break

                    # Post a fix message and re-monitor
                    _fix_attempt += 1
                    print(Fore.YELLOW + f"  ↩ Semantic gate: {_sem_recommendation} — sending fix prompt to Jules (attempt {_fix_attempt}/{_max_fix_retries})..." + Style.RESET_ALL)

                    _intent_text = ""
                    if human_intent_path and Path(human_intent_path).exists():
                        try:
                            _intent_data = json.loads(Path(human_intent_path).read_text(encoding="utf-8"))
                            _ui = _intent_data.get("user_intent") or _intent_data
                            _intent_text = _ui.get("goal", "") + "\n" + _ui.get("expected_behavior_change", "")
                        except Exception:
                            _intent_text = str(human_intent_path)

                    _current_diff = ""
                    if diff_path.exists():
                        _current_diff = diff_path.read_text(encoding="utf-8", errors="replace")[:2000]

                    fix_prompt = _build_fix_prompt(_sem_report, _intent_text, _current_diff)
                    fix_result = post_jules_followup_message(task_id, fix_prompt)
                    if not fix_result.get("ok"):
                        print(Fore.YELLOW + f"  ⚠ Could not post fix message to Jules: {fix_result.get('error')}" + Style.RESET_ALL)
                        print(Fore.YELLOW + "    Fix prompt (copy manually if needed):" + Style.RESET_ALL)
                        print(fix_prompt)
                        break

                    print(Fore.CYAN + f"  ▶ Fix message sent via {fix_result['method']} — waiting for Jules to respond..." + Style.RESET_ALL)
                    monitor_result = monitor.wait(task_id)
                    session_payload = monitor_result.get("payload") or {}
                    pending_changeset = extract_changeset_from_session(session_payload)
                    if pending_changeset:
                        diff_path.write_text(pending_changeset["diff"], encoding="utf-8")
                        print(Fore.CYAN + "  ▶ Jules updated changeSet extracted." + Style.RESET_ALL)
                        # Re-extract changed_files from new diff
                        _new_files = [
                            l[6:].strip() for l in pending_changeset["diff"].splitlines()
                            if l.startswith("+++ b/") and l[6:].strip() != "/dev/null"
                        ]
                        if _new_files:
                            changed_files = list(dict.fromkeys(_new_files))
                    else:
                        print(Fore.YELLOW + "  ⚠ Jules fix did not produce a new changeSet diff." + Style.RESET_ALL)
                        break

                # ── Decision after loop ──────────────────────────────────
                if _sem_recommendation == "ACCEPT":
                    print(Fore.GREEN + "  ✔ Semantic gate passed — approving Jules changeSet..." + Style.RESET_ALL)
                    approval = approve_jules_changeset(task_id)
                    if approval.get("ok"):
                        approved_pr_url = approval.get("pr_url")
                        if approved_pr_url:
                            print(Fore.GREEN + f"  ✔ Jules changeSet approved. PR created: {approved_pr_url}" + Style.RESET_ALL)
                            persist_jules_pr(config.journal.run_id, {
                                "pr_url": approved_pr_url,
                                "branch": (pr_metadata or {}).get("branch"),
                                "commit_sha": pending_changeset.get("base_commit") if pending_changeset else None,
                                "created_at": pr_metadata.get("created_at") if pr_metadata else None,
                            })
                        else:
                            # Jules creates PRs asynchronously — poll until it appears
                            print(Fore.CYAN + f"  ▶ Approval sent via {approval.get('method')} — polling for PR creation (up to 120s)..." + Style.RESET_ALL)
                            polled_pr = poll_for_pr_after_approval(task_id, timeout=120, poll_interval=8)
                            if polled_pr:
                                approved_pr_url = polled_pr["pr_url"]
                                print(Fore.GREEN + f"  ✔ PR created: {approved_pr_url}" + Style.RESET_ALL)
                                persist_jules_pr(config.journal.run_id, {
                                    "pr_url": approved_pr_url,
                                    "branch": polled_pr.get("branch") or (pr_metadata or {}).get("branch"),
                                    "commit_sha": polled_pr.get("commit_sha") or (pending_changeset.get("base_commit") if pending_changeset else None),
                                    "created_at": polled_pr.get("created_at"),
                                })
                            else:
                                print(Fore.YELLOW + "  ⚠ PR not yet visible after 120s — Jules may still be creating it." + Style.RESET_ALL)
                                session_token = task_id.split('/')[-1]
                                print(Fore.YELLOW + f"    Check: https://jules.google.com/session/{session_token}/" + Style.RESET_ALL)
                                print(Fore.YELLOW + f"    Or run: python scripts/validate_and_approve_jules.py --session {session_token}" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + f"  ⚠ Jules approval call failed: {approval.get('error')} (non-blocking)" + Style.RESET_ALL)
                else:
                    # Record the failure for human review
                    _failure_record = {
                        "run_id": config.journal.run_id,
                        "session_id": task_id,
                        "recommendation": _sem_recommendation,
                        "fix_attempts": _fix_attempt,
                        "issues": _sem_report.get("contract_violations", []) + _sem_report.get("drift", {}).get("missing_requirements", []),
                        "session_url": f"https://jules.google.com/session/{task_id.split('/')[-1]}/",
                        "report_path": str(_sem_report_path),
                    }
                    _failure_log = AUTOMATION_DIR / "history" / "validation_failures.json"
                    try:
                        _failure_log.parent.mkdir(parents=True, exist_ok=True)
                        _existing = []
                        if _failure_log.exists():
                            try:
                                _existing = json.loads(_failure_log.read_text(encoding="utf-8"))
                            except Exception:
                                _existing = []
                        _existing.append(_failure_record)
                        _failure_log.write_text(json.dumps(_existing, indent=2), encoding="utf-8")
                    except OSError:
                        pass
                    print(Fore.RED + f"  ✘ Semantic gate: {_sem_recommendation} after {_fix_attempt} fix attempt(s)." + Style.RESET_ALL)
                    print(Fore.RED + f"    Session for manual review: {_failure_record['session_url']}" + Style.RESET_ALL)
                    print(Fore.RED + f"    Validation report: {_sem_report_path}" + Style.RESET_ALL)
                    print(Fore.RED + f"    Failure logged to: {_failure_log}" + Style.RESET_ALL)
                    _abort(f"Semantic gate rejected Jules changeSet (recommendation={_sem_recommendation}). Not applying.")

            elif _has_real_github_pr:
                # ── Case B: GitHub PR already exists — full pre-merge gate ──
                print(Fore.CYAN + "  ▶ Pre-merge semantic gate..." + Style.RESET_ALL)
                merge_control_result = handle_pr_with_semantic(
                    run_id=config.journal.run_id,
                    pr_info={
                        "pr_url": pr_metadata.get("pr_url"),
                        "branch": pr_metadata.get("branch"),
                        "commit_sha": pr_metadata.get("commit_sha"),
                        "task_id": task_id,
                        "action_plan": action_plan,
                        "changed_files": changed_files,
                        "intent_source": human_intent_path or action_plan.get("objective", ""),
                        "jules_context": jules_context,
                    },
                )
                if not merge_control_result.get("success"):
                    _abort(
                        "Pre-merge semantic gate failed: "
                        f"{merge_control_result.get('reason', 'unknown')}"
                    )
                followup_run_id = merge_control_result.get("followup_run_id")
                print(Fore.GREEN + f"  ✔ PR merged; follow-up run created: {followup_run_id}" + Style.RESET_ALL)

            else:
                # ── Case C: No changeSet, no PR — semantic only ────────────
                print(Fore.YELLOW + "  ⚠ Jules completed but produced no changeSet or PR — running semantic only." + Style.RESET_ALL)
                _run_semantic_validation(
                    config.journal.run_id,
                    human_intent_path,
                    action_plan,
                    changed_files,
                    args.strict_semantic,
                    jules_context=jules_context,
                )

            print(Fore.GREEN + "  Jules execution completed. Artifacts saved." + Style.RESET_ALL)

            # Archive run happens in finally block
            # Skip local agents
            return

        # ------------------------------------------------------------------
        # PHASE 1: ROUTING (Enhanced with Phase M Plan)
        # ------------------------------------------------------------------
        print(Fore.CYAN + "\n────────────────────────────────────────────────────────────" + Style.RESET_ALL)
        print(Fore.CYAN + "  ▶ Router" + Style.RESET_ALL)
        print(Fore.CYAN + "────────────────────────────────────────────────────────────" + Style.RESET_ALL)

        # Determine impacted files from Plan if available
        plan_files = action_plan.get("target_files", [])

        # Phase AB: Stability check for local execution path
        _run_stability_check(config.journal.run_id, action_plan)

        # ── Stage 2: Component Code Generation ──────────────────────
        component_output = _run_modifying_agent("ComponentAgent", component_agent.run, changed_files)

        # ── Stage 3: Test Code Generation ───────────────────────────
        test_output = _run_modifying_agent("TestAgent", test_agent.run)

        # ── Stage 4: Integration Verification ───────────────────────
        integration_output = _run_modifying_agent("IntegrationAgent", integration_agent.run)

        # ── Stage 5: Validation (hard stop) ─────────────────────────
        _stage_separator("▶ ValidationAgent")
        t0 = time.time()
        try:
            passed, validation_report = validation_agent.run()
        except Exception as e:
            _abort(f"ValidationAgent crashed: {e}")

        elapsed = time.time() - t0
        print(f"  [TIME] ValidationAgent completed in {elapsed:.1f}s")

        config.journal.set_test_status("PASS" if passed else "FAIL")

        # Write validation report for audit
        artifacts_dir = PROJECT_ROOT / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        if validation_report:
            (artifacts_dir / "validation_report.txt").write_text(
                validation_report, encoding="utf-8"
            )

        if not passed:
            print("\n  ⚠  ValidationAgent found violations:")
            for line in validation_report.splitlines()[:20]:
                print(f"    {line}")
            _abort("Validation failed — changes NOT approved.")

        print("  ✅ ValidationAgent: all checks passed.")

        # ── Stage 6: Diff Summary + Approval Gate ───────────────────
        _stage_separator("[6/6] Diff Summary + Approval Gate")
        summary = summarize()
        print(summary)

        # --- SEMANTIC VALIDATION ---
        _run_semantic_validation(config.journal.run_id, human_intent_path, action_plan, changed_files, args.strict_semantic)

        # Write agent outputs for audit trail
        if component_output:
            (artifacts_dir / "component_diff.txt").write_text(component_output, encoding="utf-8")
        if test_output:
            (artifacts_dir / "test_diff.txt").write_text(test_output, encoding="utf-8")
        if integration_output:
            (artifacts_dir / "integration_diff.txt").write_text(integration_output, encoding="utf-8")

        # Approval gate — human decides
        approved = approve()

        if approved:
            print("\n  ✅ Autonomous loop completed.")
            if not config.dry_run:
                print("  Changes committed.")
        else:
            print("\n  [PAUSED] Autonomous loop paused. Changes are uncommitted for manual review.")

        config.journal.finish()

    except SecurityViolation as sv:
        _abort(f"SECURITY VIOLATION: {sv}")
    except KeyboardInterrupt:
        _abort("User interrupted execution.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        _abort(f"Unexpected global error: {e}")
    finally:
        # ── Stage 7: Run Archiving (Phase N) ────────────────────────
        _stage_separator("[7/7] Run Archiving")
        try:
            run_id = config.journal.run_id
            runs_dir = PROJECT_ROOT / "automation/runs" / run_id
            runs_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"  📂 Archiving run to {runs_dir}")
            
            # Copy Tasks artifacts
            tasks_dir = PROJECT_ROOT / "automation/tasks"
            if tasks_dir.exists():
                for f in tasks_dir.glob("*"):
                    if f.is_file():
                        try:
                            # Use read/write to copy
                            (runs_dir / f.name).write_bytes(f.read_bytes())
                        except Exception as ignore:
                            pass
                            
            # Copy Artifacts
            artifacts_dir = PROJECT_ROOT / "artifacts"
            if artifacts_dir.exists():
                 for f in artifacts_dir.glob("*"):
                    if f.is_file():
                        try:
                            (runs_dir / f.name).write_bytes(f.read_bytes())
                        except Exception as ignore:
                            pass
            
            if (runs_dir / "executor_used.txt").exists():
                print(f"  ✅ Archived executor info.")
            else:
                # If using Jules, we might have already created this info in summary,
                # but good to create a basic file if missing.
                if args.jules:
                    (runs_dir / "executor_used.txt").write_text("JULES", encoding="utf-8")
                else:
                    (runs_dir / "executor_used.txt").write_text("LOCAL", encoding="utf-8")
                
            print(f"  ✅ Run {run_id} archived successfully.")
            
        except Exception as e:
            print(f"  [WARN] Failed to archive run: {e}")

        print(f"  Journal written to: {config.journal.log_dir / ('run_' + config.journal.run_id + '.json')}")

if __name__ == "__main__":
    main()
