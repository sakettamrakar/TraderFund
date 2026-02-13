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

# Jules Integration
from automation.jules.adapter import JulesAdapter
from automation.jules_supervisor.monitor import TaskMonitor
from automation.jules_supervisor.artifact_collector import ArtifactCollector
from automation.jules_supervisor.result_summary import ResultSummary

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

def _run_semantic_validation(run_id, intent_path, action_plan, changed_files, strict_mode):
    """
    Runs the semantic validation pipeline.
    """
    _stage_separator("▶ Phase S: Semantic Validation")
    try:
        from automation.semantic.semantic_validator import SemanticValidator

        # Get current diff
        try:
            diff_proc = subprocess.run(["git", "diff"], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
            diff = diff_proc.stdout
        except:
            diff = ""

        validator = SemanticValidator(run_id, str(PROJECT_ROOT))
        report = validator.validate(intent_path, action_plan, changed_files, diff)

        if strict_mode and report.get("recommendation") != "ACCEPT":
            _abort(f"Semantic Validation Failed (Strict Mode): {report.get('recommendation')}")
    except Exception as e:
        print(Fore.RED + f"  ❌ Semantic Validation crashed: {e}" + Style.RESET_ALL)
        if strict_mode:
            _abort("Semantic Validation crashed in strict mode.")


def create_jules_task(changed_files, action_plan=None):
    """
    Creates a Jules task using the adapter.
    """
    adapter = JulesAdapter()
    task_id = config.journal.run_id

    # Construct task details
    task_data = {
        "task_id": task_id,
        "changed_memory_files": changed_files,
        "purpose": action_plan.get("objective") if action_plan else "Automated Build Loop Task"
    }

    # Prepare instructions
    instructions = "Please address the following changes:\n"
    if action_plan:
        instructions += f"Objective: {action_plan.get('objective')}\n"
        if action_plan.get('detailed_instructions'):
            instructions += "Detailed Instructions:\n"
            for instr in action_plan.get('detailed_instructions', []):
                instructions += f"- {instr}\n"
    else:
        instructions += "Please implement changes based on the modified files provided.\n"

    print(f"  Creating Jules task {task_id}...")
    try:
        payload = adapter.create_job(task_data, instructions)
        job_id = adapter.submit_job(payload)
        print(f"  Jules Job Submitted: {job_id}")
        return job_id
    except Exception as e:
        print(f"  ❌ Failed to create Jules task: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Autonomous Build Loop")
    parser.add_argument("--dry-run", action="store_true", help="Run in simulation mode without side effects")
    parser.add_argument("--jules", action="store_true", help="Use Jules executor with supervisor")
    parser.add_argument("--retrigger-from-intent", action="store_true", help="Skip memory diff and use existing human intent")
    parser.add_argument("--strict-semantic", action="store_true", help="Fail run if semantic validation does not ACCEPT")
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

        # Check for memory changes (Phase M trigger)
        memory_changed = False
        try:
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
        subprocess.run(cmd_plan, check=False)

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
        else:
            print(Fore.YELLOW + f"  ⚠ Plan: {action_plan.get('objective')}" + Style.RESET_ALL)
            for instr in action_plan.get('detailed_instructions', []):
                print(Fore.YELLOW + f"    - {instr}" + Style.RESET_ALL)

        # ------------------------------------------------------------------
        # JULES EXECUTION PATH
        # ------------------------------------------------------------------
        if args.jules:
            _stage_separator("▶ JULES SUPERVISED EXECUTION")

            task_id = create_jules_task(changed_files, action_plan)

            monitor = TaskMonitor(config.journal.run_id)
            monitor.wait(task_id)

            collector = ArtifactCollector(config.journal.run_id)
            collector.collect(task_id)

            summary_gen = ResultSummary(config.journal.run_id)
            summary_gen.generate()

            # Non-blocking design: complete run even if tests fail/PR incomplete
            print(Fore.GREEN + "  Jules execution completed. Artifacts saved." + Style.RESET_ALL)

            # --- SEMANTIC VALIDATION ---
            _run_semantic_validation(config.journal.run_id, human_intent_path, action_plan, changed_files, args.strict_semantic)

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
            print(f"  ❌ Failed to archive run: {e}")

        print(f"  Journal written to: {config.journal.log_dir / ('run_' + config.journal.run_id + '.json')}")

if __name__ == "__main__":
    main()
