"""
Integration Agent
==================
Ensures orchestration DAG consistency after component changes.
Execution mode: diffs are applied to the working tree.

KEY DESIGN: Includes relevant pipeline config and orchestration code
so Gemini can produce real diffs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask
from diff_applier import apply

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

ORCHESTRATION_PATHS = [
    "src/evolution/pipeline_runner.py",
    "src/evolution/orchestration/",
    "src/harness/",
]


def _gather_orchestration_files(max_chars: int = 20000) -> str:
    """Read existing orchestration/pipeline files."""
    blocks = []
    total = 0
    for rel in ORCHESTRATION_PATHS:
        fp = PROJECT_ROOT / rel
        if fp.is_file() and fp.suffix == ".py":
            content = fp.read_text(encoding="utf-8", errors="replace")
            if total + len(content) > max_chars:
                break
            blocks.append(f"### SOURCE: {rel}\n```python\n{content}\n```")
            total += len(content)
        elif fp.is_dir():
            for py in sorted(fp.rglob("*.py"))[:5]:
                content = py.read_text(encoding="utf-8", errors="replace")
                r = str(py.relative_to(PROJECT_ROOT))
                if total + len(content) > max_chars:
                    break
                blocks.append(f"### SOURCE: {r}\n```python\n{content}\n```")
                total += len(content)
    return "\n\n".join(blocks) if blocks else "(no orchestration files found)"


def run() -> str:
    """
    Verify and update orchestration wiring after component changes.
    """
    source_text = _gather_orchestration_files()

    prompt = f"""You are an IntegrationAgent in an autonomous code generation system.
Your job: verify that the orchestration pipeline correctly wires all components,
and produce a unified git diff if wiring changes are needed.

EXISTING ORCHESTRATION / PIPELINE CODE:
{source_text}

RULES:
1. Output ONLY a valid unified git diff. No markdown fences, no explanations.
2. Only modify files under src/evolution/, src/harness/, or config/.
3. NEVER touch files under docs/memory/ or docs/epistemic/.
4. Do NOT create cycles in the DAG.
5. Do NOT invent new orchestration logic.
6. Format: 'diff --git a/path b/path' then '--- a/path' then '+++ b/path' then @@ hunks.
7. If no wiring changes are needed, output: NO_CHANGES_REQUIRED
"""

    response = ask(prompt)

    if not response or not response.strip():
        return ""

    if "NO_CHANGES_REQUIRED" in response:
        print("  IntegrationAgent: DAG is consistent. No changes needed.")
        return response

    success, message = apply(response)
    if success:
        print(f"  ✅ IntegrationAgent patch applied: {message}")
    else:
        print(f"  ⚠  IntegrationAgent patch skipped: {message}")

    return response
