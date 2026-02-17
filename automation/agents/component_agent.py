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
import json
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
    # Load Action Plan
    action_plan_path = PROJECT_ROOT / "automation/tasks/action_plan.json"
    action_plan = {}
    if action_plan_path.exists():
        try:
            action_plan = json.loads(action_plan_path.read_text(encoding="utf-8"))
        except:
            pass

    # Determine mode: Plan-based or Legacy Spec-based
    use_plan = action_plan.get("status") == "ACTION_REQUIRED"
    

    # New Deterministic Router Logic (Phase N) — with fallback chain
    # NOTE: JulesExecutor is NOT in the local chain. Jules is asynchronous
    # (session → poll → PR) and must be activated via --jules flag in run_build_loop.py.
    # ComponentAgent's local path uses Gemini for synchronous inline execution.
    from automation.executors import GeminiExecutor

    # 1. Initialize executor chain (local/synchronous executors only)
    executor_chain = [
        GeminiExecutor(PROJECT_ROOT)
    ]

    # 2. Build task payload
    task_payload = action_plan if use_plan else {
        "status": "LEGACY_SPEC_UPDATE",
        "changed_memory_files": spec_files,
        "objective": "Update components based on spec changes (Legacy Mode)",
        "detailed_instructions": ["See specs for details."],
        "target_files": [],
        "context": {"specs": spec_files}
    }

    # 3. Try each executor in order — fallback on failure
    last_error = None
    for executor in executor_chain:
        if not executor.is_available():
            print(f"  ComponentAgent: {executor.name} not available, skipping.")
            continue

        print(f"  ComponentAgent: Trying executor -> {executor.name}")

        # Log choice
        try:
            (PROJECT_ROOT / "automation/tasks/executor_used.txt").write_text(executor.name, encoding="utf-8")
            (PROJECT_ROOT / "artifacts").mkdir(exist_ok=True)
            (PROJECT_ROOT / "artifacts/executor_used.txt").write_text(executor.name, encoding="utf-8")
        except Exception:
            pass

        try:
            response, logs = executor.execute(task_payload)

            # Check if executor produced meaningful output
            if response and response.strip():
                print(f"  ✅ {executor.name} succeeded. Output: {len(response)} chars")
                print(f"  {executor.name} Log:\n{logs[:200]}...")
                return response

            # Executor ran but produced empty output — treat as soft failure
            if logs and ("failed" in logs.lower() or "error" in logs.lower()):
                print(f"  ⚠ {executor.name} ran but produced no usable output. Falling back...")
                print(f"  {executor.name} Log: {logs[:300]}")
                last_error = f"{executor.name}: no output — {logs[:200]}"
                continue

            # Empty but no error — might be legitimate (no changes needed)
            print(f"  {executor.name}: No output generated (may be expected).")
            return ""

        except Exception as e:
            print(f"  ❌ {executor.name} failed: {e}")
            last_error = f"{executor.name}: {e}"
            continue  # Try next executor

    # All executors exhausted
    if last_error:
        print(f"  ❌ All executors failed. Last error: {last_error}")
    return ""

