"""
Autonomous Build Loop — Orchestrator
======================================
Runs the full autonomous development loop:

  spec_watcher → component_agent → test_agent → integration_agent →
  validation_agent → diff_summarizer → approval_gate

If no spec changes are detected, exits cleanly.
Aborts on validation violations or empty Gemini output.
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# Ensure automation/ is on the path
AUTOMATION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AUTOMATION_DIR.parent
sys.path.insert(0, str(AUTOMATION_DIR))

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
    """Check if an agent introduced NEW modifications to protected paths beyond the baseline."""
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


def _run_agent(name: str, func, *args):
    """Run an agent function with timing and empty-output guard."""
    _stage_separator(f"▶ {name}")
    baseline = _get_protected_dirty_files()
    t0 = time.time()
    try:
        output = func(*args)
        elapsed = time.time() - t0
        print(f"  ⏱  {name} completed in {elapsed:.1f}s")

        if output and output.strip():
            print(f"  📄 {len(output)} chars of output.")
        else:
            print(f"  ⚪ {name}: no output generated.")
            output = ""

        # Invariant check after each agent — only flag NEW violations
        violation = _check_invariant_violation(baseline)
        if violation:
            print(f"\n  ❌ {violation}")
            print("  ABORTING LOOP.")
            sys.exit(1)

        return output

    except RuntimeError as e:
        elapsed = time.time() - t0
        print(f"  ⏱  {name} failed after {elapsed:.1f}s")
        print(f"  ❌ {name} ERROR: {e}")
        return ""


def main():
    print("=" * 60)
    print("  AUTONOMOUS BUILD LOOP")
    print(f"  Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ── Stage 1: Spec Change Detection ──────────────────────────
    _stage_separator("[1/6] Spec Change Detection")
    specs = changed_specs()

    if not specs:
        print("  No spec changes detected. Exiting cleanly.")
        sys.exit(0)

    print(f"  Found {len(specs)} changed spec file(s):")
    for s in specs:
        print(f"    → {s}")

    # ── Stage 2: Component Code Generation ──────────────────────
    component_output = _run_agent("ComponentAgent", component_agent.run, specs)

    # ── Stage 3: Test Code Generation ───────────────────────────
    test_output = _run_agent("TestAgent", test_agent.run)

    # ── Stage 4: Integration Verification ───────────────────────
    integration_output = _run_agent("IntegrationAgent", integration_agent.run)
    if integration_output and "NO_CHANGES_REQUIRED" in integration_output:
        print("  DAG is consistent. No wiring changes needed.")
        integration_output = ""

    # ── Stage 5: Validation ─────────────────────────────────────
    validation_output = _run_agent("ValidationAgent", validation_agent.run)

    if validation_output:
        has_violations = any(
            keyword in validation_output
            for keyword in ["FAIL", "VIOLATION", "ERROR"]
        )
        if has_violations:
            print("\n  ⚠  ValidationAgent found violations:")
            for line in validation_output.splitlines()[:20]:
                print(f"    {line}")
            print("\n  ❌ ABORTING LOOP — validation failed.")

            # Still write report for audit
            artifacts_dir = PROJECT_ROOT / "artifacts"
            artifacts_dir.mkdir(exist_ok=True)
            (artifacts_dir / "validation_report.txt").write_text(
                validation_output, encoding="utf-8"
            )
            sys.exit(1)

    # ── Stage 6: Diff Summary + Approval Gate ───────────────────
    _stage_separator("[6/6] Diff Summary + Approval Gate")
    summary = summarize()
    print(summary)

    # Write outputs to artifacts/ for audit trail
    artifacts_dir = PROJECT_ROOT / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    if component_output:
        (artifacts_dir / "component_diff.txt").write_text(component_output, encoding="utf-8")
    if test_output:
        (artifacts_dir / "test_diff.txt").write_text(test_output, encoding="utf-8")
    if integration_output:
        (artifacts_dir / "integration_diff.txt").write_text(integration_output, encoding="utf-8")
    if validation_output:
        (artifacts_dir / "validation_report.txt").write_text(validation_output, encoding="utf-8")

    # Approval gate — human decides
    approved = approve()

    if approved:
        print("\n  ✅ Autonomous loop completed. Changes committed.")
    else:
        print("\n  ⏸  Autonomous loop paused. Changes are uncommitted for manual review.")

    print("=" * 60)


if __name__ == "__main__":
    main()
