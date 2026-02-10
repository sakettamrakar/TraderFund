"""
Component Agent
================
Calls Gemini CLI to regenerate affected components based on spec changes.
Enforces: no edits to domain_model.md, respect component contracts, output diffs only.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask


FORBIDDEN_FILES = [
    "docs/memory/03_domain/domain_model.md",
    "docs/memory/00_vision/vision.md",
    "docs/memory/02_success/success_criteria.md",
]


def run(spec_files: list[str]) -> str:
    """
    Generate component code updates based on changed spec files.

    Args:
        spec_files: List of changed spec file paths (relative to project root).

    Returns:
        The diff output from Gemini CLI.
    """
    if not spec_files:
        return ""

    file_list = "\n".join(f"  - {f}" for f in spec_files)

    prompt = f"""You are a ComponentAgent in a governed autonomous development loop.

CHANGED SPEC FILES:
{file_list}

INSTRUCTIONS:
1. Read the changed spec files listed above.
2. Generate ONLY git-style unified diffs for implementation files under src/components/.
3. Each diff must strictly implement the component contract defined in the corresponding YAML spec.
4. Do NOT modify, reference, or output diffs for any of these files:
   {', '.join(FORBIDDEN_FILES)}
5. Do NOT invent new domain entities, concepts, or terminology.
6. Do NOT hallucinate imports, classes, or functions that do not exist in the project.
7. Respect the orchestration DAG defined in docs/memory/12_orchestration/pipeline_graph.yaml.
8. All outputs must be tagged SHADOW_MODE.
9. Output ONLY the diffs. No explanations, no summaries.
"""

    response = ask(prompt)
    return response
