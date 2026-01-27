"""
Dispersion Breakout Watcher (EV-WATCH-DISPERSION).
Non-trading diagnostic component that observes Factor Context v1.3 to detect
widening of opportunity sets.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class DispersionBreakoutWatcher:
    """
    Watches for Dispersion Breakout (stable -> wide).
    States: NONE, EARLY_BREAKOUT, CONFIRMED_BREAKOUT
    """

    def watch(self, window_id: str, factor_context_path: Path, output_dir: Path) -> None:
        if not factor_context_path.exists():
            return

        try:
            with open(factor_context_path, 'r', encoding='utf-8') as f:
                ctx = json.load(f)["factor_context"]["factors"]
            
            # Extract Signals
            dispersion = ctx.get("value", {}).get("dispersion", {}).get("state", "stable")
            # Persistence usually in momentum, but relevant for breakout confirmation
            persistence = ctx.get("momentum", {}).get("persistence", {}).get("state", "intermittent")
            
            # Logic
            state = "NONE"
            confidence = 0.5
            notes = "Dispersion stable or contracting."

            if dispersion == "expanding":
                if persistence == "persistent":
                    state = "CONFIRMED_BREAKOUT"
                    confidence = 0.8
                    notes = "Persistent dispersion expansion."
                else:
                    state = "EARLY_BREAKOUT"
                    confidence = 0.6
                    notes = "Dispersion expanding but intermittent."
            
            # Output
            output_data = {
                "dispersion_breakout": {
                    "version": "1.0.0",
                    "computed_at": datetime.now().isoformat(),
                    "window_id": window_id,
                    "state": state,
                    "contributing_factors": {
                        "dispersion": dispersion,
                        "persistence": persistence
                    },
                    "confidence": confidence,
                    "notes": notes
                }
            }

            output_path = output_dir / "dispersion_breakout.json"
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
                
            print(f"  [Window: {window_id}] Watcher Emit (Dispersion): {state}")

        except Exception as e:
            print(f"[{window_id}] Dispersion Watcher Failed: {e}")
