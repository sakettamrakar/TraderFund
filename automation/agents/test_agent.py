"""
Test Agent
===========
Generates or updates tests based on modified components.
Enforces success_criteria.md alignment.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask


def run() -> str:
    """
    Generate test diffs for recently modified components.

    Returns:
        The diff output from Gemini CLI.
    """
    prompt = """You are a TestAgent in a governed autonomous development loop.

INSTRUCTIONS:
1. Examine the current state of src/components/ for recently modified files.
2. Generate ONLY git-style unified diffs for test files under tests/.
3. Tests must verify:
   a. Component behavior matches the contract in docs/memory/05_components/*.yaml.
   b. Invariants defined in each component YAML are enforced.
   c. Forbidden actions defined in each component YAML are tested as negative cases.
   d. Success criteria from docs/memory/02_success/success_criteria.md are covered.
4. Do NOT modify any implementation code to make tests pass.
5. Do NOT reduce test coverage thresholds.
6. Do NOT modify any files under docs/memory/.
7. Do NOT hallucinate test fixtures or mock data that contradicts real domain entities.
8. Output ONLY the diffs. No explanations, no summaries.
"""

    response = ask(prompt)
    return response
