"""
Expansion Transition Watcher (EV-WATCH-EXPANSION).
Non-trading diagnostic component that observes Factor Context v1.3 to detect
structural shifts from stagnation to expansion.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class ExpansionTransitionWatcher:
    """
    Watches for Expansion Transition (stagnant -> expanding).
    States: NONE, EARLY_EXPANSION, CONFIRMED_EXPANSION
    """

    def watch(self, window_id: str, factor_context_path: Path, output_dir: Path) -> None:
        if not factor_context_path.exists():
            return

        try:
            with open(factor_context_path, 'r', encoding='utf-8') as f:
                ctx = json.load(f)["factor_context"]["factors"]
            
            # Extract Signals
            # Look for volatility regime (may need fallback if v1.3 builder mock didn't fully propagate regime key)
            vol_regime = ctx.get("volatility", {}).get("regime", {}).get("state", "stable")
            
            # Momentum/Value Signals
            breadth = ctx.get("momentum", {}).get("breadth", {}).get("state", "neutral")
            dispersion = ctx.get("value", {}).get("dispersion", {}).get("state", "stable")
            
            # Logic
            state = "NONE"
            confidence = 0.5
            notes = "Stagnant or stable conditions."

            if vol_regime == "expanding":
                if breadth == "broad" or dispersion == "expanding":
                    state = "CONFIRMED_EXPANSION"
                    confidence = 0.8
                    notes = "Broad-based volatility expansion."
                else:
                    state = "EARLY_EXPANSION"
                    confidence = 0.6
                    notes = "Volatility expanding without breadth/dispersion confirmation."
            
            # Output
            output_data = {
                "expansion_transition": {
                    "version": "1.0.0",
                    "computed_at": datetime.now().isoformat(),
                    "window_id": window_id,
                    "state": state,
                    "contributing_factors": {
                        "volatility": vol_regime,
                        "breadth": breadth,
                        "dispersion": dispersion
                    },
                    "confidence": confidence,
                    "notes": notes
                }
            }

            output_path = output_dir / "expansion_transition.json"
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
                
            print(f"  [Window: {window_id}] Watcher Emit (Expansion): {state}")

        except Exception as e:
            print(f"[{window_id}] Expansion Watcher Failed: {e}")
