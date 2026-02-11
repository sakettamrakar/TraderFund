"""
Test Agent
===========
Generates or updates tests based on modified components.
Execution mode: diffs are applied to the working tree.

KEY DESIGN: Includes existing test file contents and relevant source code
in the prompt so Gemini can produce real, applicable test diffs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask
from diff_applier import apply

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"


def _gather_test_files(max_chars: int = 15000) -> str:
    """Read existing test files to give Gemini context."""
    blocks = []
    total = 0
    for py in sorted(TESTS_DIR.glob("test_*.py")):
        content = py.read_text(encoding="utf-8", errors="replace")
        rel = str(py.relative_to(PROJECT_ROOT))
        if total + len(content) > max_chars:
            break
        blocks.append(f"### EXISTING TEST: {rel}\n```python\n{content}\n```")
        total += len(content)
    return "\n\n".join(blocks) if blocks else "(no test files found)"


def _gather_recently_changed_source(max_chars: int = 15000) -> str:
    """Read source files that were recently modified (unstaged changes)."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        changed = [f for f in result.stdout.strip().splitlines()
                    if f.startswith("src/") and f.endswith(".py")]
    except FileNotFoundError:
        changed = []

    blocks = []
    total = 0
    for rel in changed[:10]:
        fp = PROJECT_ROOT / rel
        if not fp.exists():
            continue
        content = fp.read_text(encoding="utf-8", errors="replace")
        if total + len(content) > max_chars:
            break
        blocks.append(f"### MODIFIED SOURCE: {rel}\n```python\n{content}\n```")
        total += len(content)
    return "\n\n".join(blocks) if blocks else "(no modified source files)"


def run() -> str:
    """
    Generate and apply test diffs for recently modified components.
    """
    test_context = _gather_test_files()
    source_context = _gather_recently_changed_source()

    prompt = f"""You are a TestAgent in an autonomous code generation system.
Your job: read the EXISTING TESTS and MODIFIED SOURCE CODE below,
and produce a unified git diff that adds or updates tests.

EXISTING TEST FILES:
{test_context}

RECENTLY MODIFIED SOURCE FILES:
{source_context}

RULES:
1. Output ONLY a valid unified git diff. No markdown fences, no explanations.
2. Add tests that verify the new health interface (health_status, failure_count, etc.) if source was modified.
3. Use the exact file paths shown above in diff headers (e.g. tests/test_momentum_logic.py).
4. New test files should go under tests/ with test_ prefix.
5. NEVER touch files under docs/memory/ or docs/epistemic/ or src/.
6. Format: 'diff --git a/path b/path' then '--- a/path' then '+++ b/path' then @@ hunks.
7. If no test changes are needed, output: NO_CHANGES_REQUIRED
"""

    response = ask(prompt)

    if not response or not response.strip():
        return ""

    if "NO_CHANGES_REQUIRED" in response:
        print("  TestAgent: no test changes needed.")
        return response

    success, message = apply(response)
    if success:
        print(f"  ✅ TestAgent patch applied: {message}")
    else:
        print(f"  ⚠  TestAgent patch skipped: {message}")

    return response
