"""
Integration Agent
==================
Ensures orchestration DAG consistency after component changes.
No logic invention — strictly wiring.
Execution mode: diffs are applied to the working tree.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask
from diff_applier import apply


def run() -> str:
    """
    Verify and update orchestration wiring after component changes.
    Applies diffs directly to the working tree.

    Returns:
        The raw diff output from Gemini CLI, or empty string if no changes needed.
    """
    prompt = """You are an IntegrationAgent in an autonomous development loop.
You MUST output ONLY a valid unified git diff. No markdown, no explanations, no prose.

INSTRUCTIONS:
1. Read docs/memory/12_orchestration/pipeline_graph.yaml for the canonical DAG.
2. Read docs/memory/12_orchestration/execution_phases.md for phase gating rules.
3. Verify that all components in src/components/ are correctly wired into the orchestration layer.
4. Generate unified diffs (git diff format) ONLY for files under src/orchestration/ or config/pipeline/.
5. RULES:
   a. Do NOT create cycles in the DAG.
   b. Do NOT connect components from incompatible phases.
   c. Do NOT invent new orchestration logic or scheduling behavior.
   d. Do NOT output diffs for files under docs/memory/ or docs/epistemic/.
   e. Do NOT hallucinate component names not in pipeline_graph.yaml.
6. Format: start each file with 'diff --git a/path b/path', then '--- a/path', '+++ b/path', then @@ hunks.
7. If no wiring changes are needed, output exactly: NO_CHANGES_REQUIRED
8. Output ONLY the unified diff or NO_CHANGES_REQUIRED. Nothing else.
"""

    response = ask(prompt)

    if not response or not response.strip():
        return ""

    if "NO_CHANGES_REQUIRED" in response:
        print("  IntegrationAgent: DAG is consistent. No changes needed.")
        return response

    # Apply the diff to the working tree
    success, message = apply(response)
    if success:
        print(f"  ✅ IntegrationAgent patch applied: {message}")
    else:
        print(f"  ⚠  IntegrationAgent patch skipped: {message}")

    return response
