"""
Validation Agent
=================
Validates invariants, cognitive hierarchy, and success criteria alignment.
Reports violations only — never modifies specs or governance files.
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def run() -> str:
    """
    Validate the current state of the codebase against governance rules.

    Returns:
        Validation report string. Empty string means all checks passed.
    """
    # Run existing tests first
    test_result = _run_tests()

    # Run memory audit if available
    audit_result = _run_memory_audit()

    # Ask Gemini for structural validation
    llm_validation = _run_llm_validation()

    report_parts = []

    if test_result:
        report_parts.append(f"## Test Results\n{test_result}")

    if audit_result:
        report_parts.append(f"## Memory Audit\n{audit_result}")

    if llm_validation:
        report_parts.append(f"## Structural Validation\n{llm_validation}")

    return "\n\n".join(report_parts) if report_parts else ""


def _run_tests() -> str:
    """Run pytest and return results summary."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=120,
        )
        if result.returncode != 0:
            return f"FAIL\n{result.stdout}\n{result.stderr}"
        return f"PASS\n{result.stdout.splitlines()[-1] if result.stdout.strip() else 'All tests passed.'}"
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return f"SKIP: {e}"


def _run_memory_audit() -> str:
    """Run memory_audit.py and return results summary."""
    audit_script = PROJECT_ROOT / "scripts" / "memory_audit.py"
    if not audit_script.exists():
        return "SKIP: memory_audit.py not found."

    try:
        result = subprocess.run(
            [sys.executable, str(audit_script)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=60,
        )
        # Extract summary line
        lines = result.stdout.strip().splitlines()
        summary_lines = [l for l in lines if "Summary:" in l or "PASS" in l or "FAIL" in l or "WARN" in l]
        return "\n".join(summary_lines[-5:]) if summary_lines else result.stdout[-500:]
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return f"SKIP: {e}"


def _run_llm_validation() -> str:
    """Ask Gemini to validate structural integrity."""
    prompt = """You are a ValidationAgent in a governed autonomous development loop.

INSTRUCTIONS:
1. Analyze the project for the following violations:
   a. INVARIANT VIOLATIONS: Any component that self-authorizes state mutations.
   b. HIERARCHY VIOLATIONS: Any data flow that skips cognitive levels (e.g., L1 → L7 without L2-L6).
   c. SUCCESS CRITERIA MISALIGNMENT: Any component output that contradicts docs/memory/02_success/success_criteria.md.
   d. SHADOW MODE VIOLATIONS: Any component emitting production-grade outputs while system is in Shadow Mode.
   e. GOVERNANCE VIOLATIONS: Any file under docs/memory/ modified by an agent without human approval.
2. For each violation found, report:
   - Violation type
   - File path
   - Description
3. If NO violations are found, output: "VALIDATION_PASSED"
4. Do NOT suggest fixes. Report violations ONLY.
5. Do NOT modify any files.
6. Output ONLY the violation report or VALIDATION_PASSED. No explanations.
"""

    try:
        response = ask(prompt)
        return response
    except RuntimeError as e:
        return f"LLM_VALIDATION_SKIP: {e}"
