"""
Momentum Emergence Watcher (EV-WATCH-MOMENTUM).
Non-trading diagnostic component that observes Factor Context v1.2 to detect
momentum formation states.

SAFETY INVARIANTS:
- READ-ONLY: Reads factor_context.json, never modifies state.
- PASSIVE: Emits diagnostics only, no execution signals.
- SIDE-EFFECT FREE: Does not impact strategy evaluation flow.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class MomentumEmergenceWatcher:
    """
    Watches Factor Context for structural momentum emergence.
    States: NONE -> ATTEMPT -> CONFIRMING -> PERSISTENT
    """

    def __init__(self):
        pass

    def watch(self, window_id: str, factor_context_path: Path, output_dir: Path) -> None:
        """
        Evaluates emergence conditions and writes momentum_emergence.json.
        """
        if not factor_context_path.exists():
            print(f"[{window_id}] Watcher skipped: No Factor Context found.")
            return

        try:
            # 1. Read Factor Context
            with open(factor_context_path, 'r', encoding='utf-8') as f:
                ctx = json.load(f)["factor_context"]
            
            mom = ctx["factors"]["momentum"]
            
            # 2. Extract Indicators
            accel = mom.get("acceleration", {}).get("state", "unknown")
            breadth = mom.get("breadth", {}).get("state", "unknown")
            dispersion = mom.get("dispersion", {}).get("state", "unknown")
            persistence = mom.get("persistence", {}).get("state", "unknown")
            time_in_state = mom.get("time_in_state", {}).get("state", "unknown")
            
            # 3. Determine State (Precedence: Persistent > Confirming > Attempt)
            emergence_state = "NONE"
            confidence = 0.0
            notes = "No emergence conditions met."

            # Condition 3: EMERGING_PERSISTENT
            if persistence == "persistent" and time_in_state in ["medium", "long"]:
                emergence_state = "EMERGING_PERSISTENT"
                confidence = 0.9
                notes = "Structurally entrenched momentum state."
            
            # Condition 2: EMERGING_CONFIRMING
            elif accel == "accelerating" and breadth == "broad" and dispersion == "expanding":
                emergence_state = "EMERGING_CONFIRMING"
                confidence = 0.7
                notes = "Broad-based acceleration confirmed."
            
            # Condition 1: EMERGING_ATTEMPT
            elif accel == "accelerating" and time_in_state == "short":
                emergence_state = "EMERGING_ATTEMPT"
                confidence = 0.4
                notes = "Early acceleration detected."

            # 4. Construct Output Artifact
            output_data = {
                "momentum_emergence": {
                    "version": "1.0.0",
                    "computed_at": datetime.now().isoformat(),
                    "window_id": window_id,
                    "regime": "derived", # Context doesn't carry regime explicitly in input, strictly factor based
                    "state": emergence_state,
                    "contributing_factors": {
                        "acceleration": accel,
                        "breadth": breadth,
                        "dispersion": dispersion,
                        "persistence": persistence,
                        "time_in_state": time_in_state
                    },
                    "confidence": confidence,
                    "notes": notes
                }
            }

            # 5. Emit Artifact
            output_path = output_dir / "momentum_emergence.json"
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
                
            print(f"  [Window: {window_id}] Watcher Emit: {emergence_state}")

        except Exception as e:
            print(f"[{window_id}] Watcher Failed: {e}")
            # Watcher failure is non-blocking (Diagnostic only)
