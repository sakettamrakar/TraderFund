"""
Validation Agent
=================
Validates invariants, cognitive hierarchy, and success criteria alignment.
Reports violations only — never modifies files.
Hard stop: aborts the loop on any violation.
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

VIOLATION_KEYWORDS = ["FAIL", "VIOLATION", "ERROR", "BLOCKED", "INVARIANT"]


def run() -> tuple[bool, str]:
    """
    Validate the current state of the codebase against governance rules.

    Returns:
        (passed, report) tuple.
        passed=True means no violations. passed=False means hard stop.
    """
    test_result = _run_tests()
    audit_result = _run_memory_audit()
    llm_validation = _run_llm_validation()

    report_parts = []

    # Tests are a hard gate
    test_failed = False
    if test_result:
        report_parts.append(f"## Test Results\n{test_result}")
        if "FAIL" in test_result:
            test_failed = True

    if audit_result:
        report_parts.append(f"## Memory Audit\n{audit_result}")

    llm_has_violations = False
    if llm_validation:
        report_parts.append(f"## Structural Validation\n{llm_validation}")
        if "VALIDATION_PASSED" not in llm_validation:
            llm_has_violations = any(kw in llm_validation for kw in VIOLATION_KEYWORDS)

    report = "\n\n".join(report_parts) if report_parts else ""
    passed = not test_failed and not llm_has_violations
    return passed, report


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
        lines = result.stdout.strip().splitlines()
        summary_lines = [l for l in lines if "Summary:" in l or "PASS" in l or "FAIL" in l or "WARN" in l]
        return "\n".join(summary_lines[-5:]) if summary_lines else result.stdout[-500:]
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return f"SKIP: {e}"


def _run_llm_validation() -> str:
    """Ask Gemini to validate structural integrity."""
    prompt = """You are a ValidationAgent in an autonomous development loop.
You do NOT output diffs. You output a violation report ONLY.

INSTRUCTIONS:
1. Analyze the project for the following violations:
   a. INVARIANT VIOLATIONS: Any component that self-authorizes state mutations.
   b. HIERARCHY VIOLATIONS: Any data flow that skips cognitive levels (e.g., L1 to L7 without L2-L6).
   c. SUCCESS CRITERIA MISALIGNMENT: Any component output that contradicts docs/memory/02_success/success_criteria.md.
   d. SHADOW MODE VIOLATIONS: Any component emitting production-grade outputs while system is in Shadow Mode.
   e. GOVERNANCE VIOLATIONS: Any file under docs/memory/ modified by an agent without human approval.
2. For each violation found, report:
   - VIOLATION type
   - File path
   - Description (one line)
3. If NO violations are found, output exactly: VALIDATION_PASSED
4. Do NOT suggest fixes.
5. Do NOT output diffs.
6. Do NOT modify any files.
7. Output ONLY the violation report or VALIDATION_PASSED. No explanations, no prose.
"""

    try:
        response = ask(prompt)
        return response
    except RuntimeError as e:
        return f"LLM_VALIDATION_SKIP: {e}"
