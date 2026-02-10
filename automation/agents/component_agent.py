"""
Component Agent
================
Calls Gemini CLI to regenerate affected components based on spec changes.
Execution mode: diffs are applied to the working tree.

KEY DESIGN: Gemini CLI in headless mode has NO file system access.
This agent must include BOTH the spec contents AND the existing source
code in the prompt for Gemini to produce real, applicable diffs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gemini_bridge import ask
from diff_applier import apply

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

PROTECTED_PREFIXES = ["docs/memory/", "docs/epistemic/"]

# Mapping from spec YAML names to actual source directories/files
SPEC_TO_SOURCE_MAP = {
    "regime_engine": ["src/layers/", "src/evolution/regime_context_builder.py"],
    "narrative_engine": ["src/narratives/"],
    "meta_engine": ["src/intelligence/"],
    "factor_engine": ["src/layers/factor_layer.py", "src/layers/factor_live.py",
                      "src/evolution/factor_context_builder.py"],
    "strategy_selector": ["src/strategy/", "src/evolution/strategy_eligibility_resolver.py"],
    "convergence_engine": ["src/evolution/"],
    "constraint_engine": ["src/capital/"],
    "portfolio_intelligence": ["src/decision/"],
    "dashboard": ["src/dashboard/"],
    "governance": ["src/governance/"],
    "momentum_engine": ["src/core_modules/momentum_engine/"],
    "ingestion_us": ["src/ingestion/"],
    "ingestion_india": ["src/ingestion/"],
    "ingestion_events": ["src/ingestion/"],
    "factor_lens": ["src/layers/factor_layer.py"],
    "fundamental_lens": ["src/layers/"],
    "narrative_lens": ["src/narratives/"],
    "strategy_lens": ["src/strategy/"],
    "technical_lens": ["src/layers/"],
}


def _spec_key(spec_path: str) -> str:
    """Extract component key from a spec file path."""
    name = Path(spec_path).stem  # e.g. "regime_engine" from "regime_engine.yaml"
    return name


def _gather_source_files(spec_files: list[str], max_chars: int = 30000) -> str:
    """Read existing source files that correspond to the changed specs."""
    source_paths = set()
    for sf in spec_files:
        key = _spec_key(sf)
        if key in SPEC_TO_SOURCE_MAP:
            for src in SPEC_TO_SOURCE_MAP[key]:
                full = PROJECT_ROOT / src
                if full.is_file():
                    source_paths.add(src)
                elif full.is_dir():
                    for py in sorted(full.rglob("*.py"))[:5]:
                        source_paths.add(str(py.relative_to(PROJECT_ROOT)))

    blocks = []
    total = 0
    for rel in sorted(source_paths):
        fp = PROJECT_ROOT / rel
        if not fp.exists():
            continue
        content = fp.read_text(encoding="utf-8", errors="replace")
        if total + len(content) > max_chars:
            break
        blocks.append(f"### SOURCE FILE: {rel}\n```python\n{content}\n```")
        total += len(content)

    return "\n\n".join(blocks) if blocks else "(no matching source files found)"


def run(spec_files: list[str]) -> str:
    """
    Generate and apply component code updates based on changed spec files.
    """
    if not spec_files:
        return ""

    # Filter to only YAML specs (not .md contracts)
    yaml_specs = [f for f in spec_files if f.endswith(".yaml")]
    if not yaml_specs:
        return ""

    # Read spec contents
    spec_blocks = []
    for sf in yaml_specs[:5]:  # Limit to avoid huge prompts
        fp = PROJECT_ROOT / sf
        if fp.exists():
            content = fp.read_text(encoding="utf-8", errors="replace")
            spec_blocks.append(f"### SPEC: {sf}\n```yaml\n{content}\n```")

    spec_text = "\n\n".join(spec_blocks)

    # Read existing source files that these specs map to
    source_text = _gather_source_files(yaml_specs)

    prompt = f"""You are a ComponentAgent in an autonomous code generation system.
Your job: read the SPEC contracts below, read the EXISTING SOURCE CODE below,
and produce a unified git diff that adds the Component Health Interface to the source code.

The health contract requires each component to expose:
- health_status: OK | DEGRADED | FAILED
- last_success_timestamp: ISO-8601 UTC string
- failure_count: int >= 0
- degraded_reason: string or None

CHANGED SPEC FILES:
{spec_text}

EXISTING SOURCE CODE (these are the files you MUST modify):
{source_text}

RULES:
1. Output ONLY a valid unified git diff. No markdown fences, no explanations.
2. Add a ComponentHealth dataclass/model and a get_health() function to each source file.
3. Use the exact file paths shown above in your diff headers.
4. NEVER touch files under docs/memory/ or docs/epistemic/.
5. Do NOT invent new files — only modify the existing ones shown above.
6. Format: 'diff --git a/path b/path' then '--- a/path' then '+++ b/path' then @@ hunks.
7. Use minimal context (0 lines) in your diffs to avoid context mismatch errors. (i.e. git diff -U0)
8. If the source already has health fields, output: NO_CHANGES_REQUIRED
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
