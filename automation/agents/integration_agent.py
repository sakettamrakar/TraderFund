"""
Integration Agent
==================
Ensures orchestration DAG consistency after component changes.
No logic invention — strictly wiring.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask


def run() -> str:
    """
    Verify and update orchestration wiring after component changes.

    Returns:
        The diff output from Gemini CLI, or empty string if no changes needed.
    """
    prompt = """You are an IntegrationAgent in a governed autonomous development loop.

INSTRUCTIONS:
1. Read docs/memory/12_orchestration/pipeline_graph.yaml for the canonical DAG.
2. Read docs/memory/12_orchestration/execution_phases.md for phase gating rules.
3. Verify that all components in src/components/ are correctly wired into the orchestration layer.
4. Generate ONLY git-style unified diffs for files under src/orchestration/ or config/pipeline/.
5. RULES:
   a. Do NOT create cycles in the DAG.
   b. Do NOT connect components from incompatible phases (e.g., Phase 0 → Phase 5 directly).
   c. Do NOT invent new orchestration logic or scheduling behavior.
   d. Do NOT modify any files under docs/memory/.
   e. Do NOT hallucinate component names that do not exist in pipeline_graph.yaml.
6. If no wiring changes are needed, output: "NO_CHANGES_REQUIRED"
7. Output ONLY the diffs or NO_CHANGES_REQUIRED. No explanations, no summaries.
"""

    response = ask(prompt)
    return response
