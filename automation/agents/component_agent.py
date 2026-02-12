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
    

    # New Deterministic Router Logic (Phase N)
    from automation.executors import JulesExecutor, GeminiExecutor
    
    # 1. Initialize Executors
    executors = [
        JulesExecutor(PROJECT_ROOT),
        GeminiExecutor(PROJECT_ROOT)
    ]
    
    selected_executor = None
    
    # 2. Select First Available
    for executor in executors:
        if executor.is_available():
            selected_executor = executor
            break
            
    if not selected_executor:
        raise RuntimeError("CRITICAL: No available executors found in chain [Jules, Gemini].")
        
    print(f"  ComponentAgent: Selected executor -> {selected_executor.name}")
    
    # 3. Log Choice
    # We write to automation/tasks/executor_used.txt so run_build_loop can archive it
    # We also write to artifacts/executor_used.txt for legacy compatibility
    try:
        (PROJECT_ROOT / "automation/tasks/executor_used.txt").write_text(selected_executor.name, encoding="utf-8")
        (PROJECT_ROOT / "artifacts/executor_used.txt").write_text(selected_executor.name, encoding="utf-8")
    except Exception as e:
        print(f"  ⚠ Failed to log executor choice: {e}")

    # 4. Strict Enforcement Check
    # "If Gemini executes while Jules is available, raise ARCHITECTURE_VIOLATION"
    if selected_executor.name == "GEMINI":
        # The loop logic guarantees this naturally.
        pass

    # 5. Execute
    try:
        # Construct the task object expected by executors
        # They expect a dict with 'action_plan' or similar. 
        # My BaseExecutor.execute takes `action_plan: Dict`.
        # So we pass the loaded `action_plan` dict.
        
        # If legacy mode (no plan), we need to synthesize a plan or fail?
        # "Gemini must NEVER be invoked unless...".
        # If use_plan is False (Legacy), we are in a tricky spot. 
        # The new executors (AG, Jules) might expect a Plan.
        # `antigravity_worker.py` logic relies on `task` dict.
        # Use existing legacy logic? NO, "Replace the current ad-hoc executor selection".
        # "ComponentAgent updated".
        # I must wrap legacy spec payload into a "plan-like" structure if needed.
        
        task_payload = action_plan if use_plan else {
            "status": "LEGACY_SPEC_UPDATE",
            "changed_memory_files": spec_files,
            "objective": "Update components based on spec changes (Legacy Mode)",
            "detailed_instructions": ["See specs for details."],
            "target_files": [], # We might want to populate this if we can
            "context": {"specs": spec_files}
        }
        
        if not use_plan:
             # Gather source files for legacy context if needed by executors?
             # GeminiExecutor (LegacyWrapper) expects the raw prompt? 
             # No, `gemini_fallback.py` constructs the prompt from `task` dict (changed_files).
             # So passing `changed_memory_files` in task_payload is sufficient.
             pass

        response, logs = selected_executor.execute(task_payload)
        
        # 6. Apply Code (Executor might return diff, or might have applied it)
        # Antigravity: returns diff, log. (Worker applies? AG worker waits for changes, so it assumes external application or applies itself?)
        # `antigravity_worker.py`: "Return Diff + Logs". It does NOT apply changes. It waits for them.
        # Wait, if AG worker waits for changes, WHO applies them? The "Worker" (Playwright) acts as a human editor. 
        # So the changes ARE applied on disk. The Diff is just observed.
        # Gemini (Legacy): returns diff (string). Does NOT apply.
        # `gemini_fallback.execute` calls `self._apply_response`. So it APPLIES.
        # Jules: `jules_adapter.execute` calls `self.code_ops.apply_diff`. So it APPLIES.
        
        # Consistent behavior: All executors APPLY changes to disk.
        # They return the diff for logging/summary only.
        
        if not response and not logs:
             # Some falure
             return ""
             
        print(f"  {selected_executor.name} Execution Log:\n{logs[:200]}...")
        
        return response

    except Exception as e:
        print(f"  ❌ Executor {selected_executor.name} failed: {e}")
        # "No silent downgrade." -> Re-raise.
        raise

