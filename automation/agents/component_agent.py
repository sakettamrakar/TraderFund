"""
Component Agent
================
Calls Gemini CLI to regenerate affected components based on spec changes.
Enforces: no edits to protected paths, respect component contracts, output diffs only.
Execution mode: diffs are applied to the working tree.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask
from diff_applier import apply

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

FORBIDDEN_FILES = [
    "docs/memory/03_domain/domain_model.md",
    "docs/memory/00_vision/vision.md",
    "docs/memory/02_success/success_criteria.md",
]


def run(spec_files: list[str]) -> str:
    """
    Generate and apply component code updates based on changed spec files.

    Returns:
        The raw diff output from Gemini CLI.
    """
    if not spec_files:
        return ""

    # Read spec file contents to give Gemini real context
    spec_contents = []
    for sf in spec_files:
        fp = PROJECT_ROOT / sf
        if fp.exists():
            content = fp.read_text(encoding="utf-8", errors="replace")
            spec_contents.append(f"### FILE: {sf}\n```\n{content}\n```")

    spec_block = "\n\n".join(spec_contents) if spec_contents else "\n".join(f"  - {f}" for f in spec_files)

    prompt = f"""You are a ComponentAgent in an autonomous development loop.
You MUST output ONLY a valid unified git diff. No markdown, no explanations, no prose.

CHANGED SPEC FILES AND THEIR CONTENTS:
{spec_block}

INSTRUCTIONS:
1. Generate unified diffs (git diff format) for implementation files under src/components/.
2. Each diff must implement the component contract defined in the spec.
3. NEVER output diffs for files under docs/memory/ or docs/epistemic/.
4. NEVER output diffs for: {', '.join(FORBIDDEN_FILES)}
5. Do NOT invent new domain entities not in the spec.
6. Do NOT hallucinate imports or functions.
7. Format: start each file with 'diff --git a/path b/path', then '--- a/path', '+++ b/path', then @@ hunks.
8. If no code changes are needed, output exactly: NO_CHANGES_REQUIRED
9. Output ONLY the unified diff or NO_CHANGES_REQUIRED. Nothing else.
"""

    response = ask(prompt)

    if not response or not response.strip():
        return ""

    if "NO_CHANGES_REQUIRED" in response:
        print("  ComponentAgent: no code changes needed.")
        return response

    # Apply the diff to the working tree
    success, message = apply(response)
    if success:
        print(f"  ✅ ComponentAgent patch applied: {message}")
    else:
        print(f"  ⚠  ComponentAgent patch skipped: {message}")

    return response
