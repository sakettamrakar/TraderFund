"""
Test Agent
===========
Generates or updates tests based on modified components.
Enforces success_criteria.md alignment.
Execution mode: diffs are applied to the working tree.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask
from diff_applier import apply


def run() -> str:
    """
    Generate and apply test diffs for recently modified components.

    Returns:
        The raw diff output from Gemini CLI.
    """
    prompt = """You are a TestAgent in an autonomous development loop.
You MUST output ONLY a valid unified git diff. No markdown, no explanations, no prose.

INSTRUCTIONS:
1. Generate unified diffs (git diff format) for test files under tests/.
2. Tests must verify:
   a. Component behavior matches the contract in docs/memory/05_components/*.yaml.
   b. Invariants defined in each component YAML are enforced.
   c. Forbidden actions defined in each component YAML are tested as negative cases.
   d. Success criteria from docs/memory/02_success/success_criteria.md are covered.
3. Do NOT output diffs for files under docs/memory/ or docs/epistemic/.
4. Do NOT modify any implementation code.
5. Do NOT hallucinate test fixtures or mock data.
6. Format: start each file with 'diff --git a/path b/path', then '--- a/path', '+++ b/path', then @@ hunks.
7. If no test changes are needed, output exactly: NO_CHANGES_REQUIRED
8. Output ONLY the unified diff or NO_CHANGES_REQUIRED. Nothing else.
"""

    response = ask(prompt)

    if not response or not response.strip():
        return ""

    if "NO_CHANGES_REQUIRED" in response:
        print("  TestAgent: no test changes needed.")
        return response

    # Apply the diff to the working tree
    success, message = apply(response)
    if success:
        print(f"  ✅ TestAgent patch applied: {message}")
    else:
        print(f"  ⚠  TestAgent patch skipped: {message}")

    return response
