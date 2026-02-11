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
import subprocess
import argparse
from pathlib import Path

AUTOMATION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AUTOMATION_DIR.parent
sys.path.insert(0, str(AUTOMATION_DIR))

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
        specs = changed_specs()

        if not specs:
            print("  No spec changes detected. Exiting cleanly.")
            config.journal.finish()
            sys.exit(0)

        config.journal.set_changed_specs(specs)
        print(f"  Found {len(specs)} changed spec file(s):")
        for s in specs:
            print(f"    → {s}")

        # ── Stage 2: Component Code Generation ──────────────────────
        component_output = _run_modifying_agent("ComponentAgent", component_agent.run, specs)

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
        print(f"  Journal written to: {config.journal.log_dir / ('run_' + config.journal.run_id + '.json')}")

    except SecurityViolation as sv:
        _abort(f"SECURITY VIOLATION: {sv}")
    except KeyboardInterrupt:
        _abort("User interrupted execution.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        _abort(f"Unexpected global error: {e}")

if __name__ == "__main__":
    main()
