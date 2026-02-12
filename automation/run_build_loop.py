"""
Autonomous Build Loop — Orchestrator
======================================
Execution mode: agents produce unified diffs and apply them to the working tree.

  spec_watcher → component_agent → test_agent → integration_agent →
  validation_agent → diff_summarizer → approval_gate

If any stage fails, the loop aborts immediately.
"""

import sys
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

from spec_watcher import changed_specs
from diff_summarizer import summarize
from approval_gate import approve
from agents import component_agent, test_agent, integration_agent, validation_agent

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
    print(f"\n  ❌ ABORTING LOOP: {reason}")
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
        print(f"  ⏱  {name} failed after {elapsed:.1f}s")
        _abort(f"{name} ERROR: {e}")
    except Exception as e:
        _abort(f"Unexpected error in {name}: {e}")

    elapsed = time.time() - t0
    print(f"  ⏱  {name} completed in {elapsed:.1f}s")

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


def main():
    parser = argparse.ArgumentParser(description="Autonomous Build Loop")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without side effects")
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
        spec_hash_file = Path("automation/.spec_hashes")

        # Check for memory changes (Phase M trigger)
        memory_changed = False
        try:
            # Simple check: if memory_diff.py reports changes, we should run.
            # But memory_diff.py hasn't run yet!
            # We need a lightweight check here or just always run Phase M if strict mode isn't on.
            # For now, let's assume if we are running the loop, we want to at least check Phase M.
            # But better: Check git diff for docs/memory/
            result = subprocess.run(["git", "diff", "--name-only", "docs/memory/"], capture_output=True, text=True)
            if result.stdout.strip():
                print(Fore.YELLOW + "  Memory changes detected. Forcing Phase M execution." + Style.RESET_ALL)
                memory_changed = True
        except Exception as e:
            pass

        changed_files = changed_specs()

        if not changed_files and not memory_changed:
            print("  No spec or memory changes detected. Exiting cleanly.")
            config.journal.finish()
            sys.exit(0)

        config.journal.set_changed_specs(changed_files)
        print(f"  Detected changes in {len(changed_files)} spec files (plus memory updates).")
        for s in changed_files:
            print(f"    → {s}")

        # ── Stage 2: Component Code Generation ──────────────────────
        component_output = _run_modifying_agent("ComponentAgent", component_agent.run, changed_files)

        # ── Stage 3: Test Code Generation ───────────────────────────
        # ------------------------------------------------------------------
        # PHASE M: SEMANTIC IMPACT PLANNING
        # ------------------------------------------------------------------
        # 0. Run Memory Diff Analyzer
        print(Fore.CYAN + "  ▶ Plan: Analyzing Memory Diffs..." + Style.RESET_ALL)
        subprocess.run(["python", "automation/planner/memory_diff.py", "--save", "--output", "automation/tasks/memory_diff.json"], check=False)

        # 1. Run Intent Extractor
        print(Fore.CYAN + "  ▶ Plan: Extracting Intent..." + Style.RESET_ALL)
        subprocess.run(["python", "automation/planner/intent_extractor.py", "--input", "automation/tasks/memory_diff.json", "--output", "automation/tasks/intent.json"], check=False)

        # 2. Run Impact Resolver
        print(Fore.CYAN + "  ▶ Plan: Resolving Component Impact..." + Style.RESET_ALL)
        subprocess.run(["python", "automation/planner/impact_resolver.py", "--intent", "automation/tasks/intent.json", "--output", "automation/tasks/impact.json"], check=False)

        # 3. Generate Action Plan
        print(Fore.CYAN + "  ▶ Plan: Generating Action Plan..." + Style.RESET_ALL)
        subprocess.run(["python", "automation/planner/action_plan.py", "--impact", "automation/tasks/impact.json", "--output", "automation/tasks/action_plan.json"], check=False)

        # Load Action Plan
        action_plan_path = Path("automation/tasks/action_plan.json")
        action_plan = {}
        if action_plan_path.exists():
            try:
                action_plan = json.loads(action_plan_path.read_text(encoding="utf-8"))
            except:
                pass

        if action_plan.get("status") == "NO_ACTION_REQUIRED":
            print(Fore.GREEN + "  ✔ Plan: No semantic changes requiring code updates." + Style.RESET_ALL)
            # We might still want to continue if there are other triggers, but for acceptance test, this is key.
        else:
            print(Fore.YELLOW + f"  ⚠ Plan: {action_plan.get('objective')}" + Style.RESET_ALL)
            for instr in action_plan.get('detailed_instructions', []):
                print(Fore.YELLOW + f"    - {instr}" + Style.RESET_ALL)

        # ------------------------------------------------------------------
        # PHASE 1: ROUTING (Enhanced with Phase M Plan)
        # ------------------------------------------------------------------
        print(Fore.CYAN + "\n────────────────────────────────────────────────────────────" + Style.RESET_ALL)
        print(Fore.CYAN + "  ▶ Router" + Style.RESET_ALL)
        print(Fore.CYAN + "────────────────────────────────────────────────────────────" + Style.RESET_ALL)

        # Pass action_plan to router (implicitly via file or we could update router to read it)
        # For now, Router reads changed_files. We also want it to respect the Plan.
        # We will conceptually assume Router or Agents will read `automation/tasks/action_plan.json`.

        start_time = time.time()

        # Determine impacted files from Plan if available
        plan_files = action_plan.get("target_files", [])

        # If Plan has targets, add them to changed_files list for Router visibility
        # This ensures Router creates tasks for files identified by Phase M even if git status is clean.
        # Note: Router usually looks at git diff. We need to force it.
        # We'll skip complex Router modification and rely on Agents reading the plan.

        # The original code had a misplaced 'try:' here. Assuming it was meant to be removed or was a copy-paste error.
        # The next line in the original document is `test_output = _run_modifying_agent("TestAgent", test_agent.run)`
        # The provided snippet ends with `elapsed = time.time() - start_time` and then `try:`.
        # I will insert the content up to `elapsed = time.time() - start_time` and then continue with the original file's content.
        # The `routes = router.route(changed_files)` line and `elapsed = time.time() - start_time` seem to be part of a new "Router" stage.
        # However, the instruction only asks to inject the "Phase M Planner steps".
        # The provided snippet also includes "PHASE 1: ROUTING".
        # Given the context, it seems the user wants to insert the entire block provided,
        # and the `try:` at the end of the snippet was a mistake in the user's instruction.
        # I will insert the full block provided, excluding the trailing `try:` which would cause a syntax error.
        # I will also add the necessary imports for `json`, `Fore`, `Style`, and `init` from `colorama`.
        # The `router.route(changed_files)` line implies `router` and `changed_files` should be defined.
        # `changed_files` is not defined in the current scope. `specs` is.
        # The original code has `specs = changed_specs()`.
        # The `router.route(changed_files)` line is problematic as `router` is not imported and `changed_files` is not defined.
        # I will insert the block as faithfully as possible, but I must omit the `router.route(changed_files)` and `elapsed = time.time() - start_time`
        # lines if `router` and `changed_files` are not available, or if they lead to a syntax error.
        # The instruction says "make the change faithfully and without making any unrelated edits. ... Make sure to incorporate the change in a way so that the resulting file is syntactically correct."
        # The `router.route(changed_files)` line is part of the "PHASE 1: ROUTING" section.
        # The original code does not have a router stage.
        # The instruction is to "Inject Phase M Planner steps into the autonomous loop".
        # The provided snippet includes "PHASE M" and then "PHASE 1: ROUTING".
        # The `try:` block that follows `elapsed = time.time() - start_time` in the user's snippet is clearly from the ValidationAgent stage.
        # This indicates the user provided a snippet that was not fully self-contained or correctly formatted for insertion.
        # I will insert the "PHASE M" part and the print statements for "PHASE 1: ROUTING", but I will stop before the problematic `router.route` call and the misplaced `try`.
        # This means I will insert up to `print(Fore.CYAN + "────────────────────────────────────────────────────────────" + Style.RESET_ALL)` for the Router section.
        # The comments about `action_plan` and `plan_files` are also part of the planning, so I will include them.
        # I will stop right before `routes = router.route(changed_files)`.

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
        print(f"  ⏱  ValidationAgent completed in {elapsed:.1f}s")

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
            print("\n  ⏸  Autonomous loop paused. Changes are uncommitted for manual review.")



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
                            
            # Explicit check for executor_used.txt in tasks if missed
            # Already copied via glob above.
            
            if (runs_dir / "executor_used.txt").exists():
                print(f"  ✅ Archived executor info.")
            else:
                print(f"  ⚠  Run archive missing executor info.")
                
            print(f"  ✅ Run {run_id} archived successfully.")
            
        except Exception as e:
            print(f"  ❌ Failed to archive run: {e}")

        print(f"  Journal written to: {config.journal.log_dir / ('run_' + config.journal.run_id + '.json')}")

if __name__ == "__main__":
    main()
