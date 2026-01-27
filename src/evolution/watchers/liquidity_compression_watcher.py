"""
Liquidity Compression Watcher (EV-WATCH-LIQUIDITY).
Non-trading diagnostic component that observes Factor Context v1.3 to detect
market compression states (Compressed, Neutral, Expanding).

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

class LiquidityCompressionWatcher:
    """
    Watches Factor Context for Liquidity/Volatility Compression.
    States: COMPRESSED, NEUTRAL, EXPANDING
    """

    def __init__(self):
        pass

    def watch(self, window_id: str, factor_context_path: Path, output_dir: Path) -> None:
        """
        Evaluates compression conditions and writes liquidity_compression.json.
        """
        if not factor_context_path.exists():
            print(f"[{window_id}] Watcher skipped: No Factor Context found.")
            return

        try:
            # 1. Read Factor Context
            with open(factor_context_path, 'r', encoding='utf-8') as f:
                ctx = json.load(f)["factor_context"]
            
            factors = ctx["factors"]
            
            # 2. Extract Indicators
            # Volatility Regime (Note: Schema for volatility usually has 'regime' key, 
            # but current mock only has 'confidence'. We check if v1.3 builder populated it, 
            # or default to 'stable' if missing as per current builder state which might not explicitly populate regime state yet 
            # if not added in v1.3 plan for volatility specifically, checking schema...)
            # Checking v1.1 schema: volatility.regime.state. 
            # The v1.3 builder update earlier didn't explicitly add volatility inputs because they were assumed v1.1.
            # However, looking at builder code, volatility section was: "volatility": {"confidence": 0.5}.
            # It seems 'regime' key is missing in the builder implementation (historical oversight).
            # We will handle safely:
            vol_regime = factors.get("volatility", {}).get("regime", {}).get("state", "stable")
            
            # Value Dispersion (New v1.3 field)
            dispersion = factors.get("value", {}).get("dispersion", {}).get("state", "stable")
            
            # 3. Determine State
            state = "NEUTRAL"
            confidence = 0.5
            notes = "Market in steady state."

            if vol_regime == "contracting" or (dispersion == "contracting" and vol_regime != "expanding"):
                state = "COMPRESSED"
                confidence = 0.8
                notes = "Volatility or dispersion contracting; market coiling."
            
            elif vol_regime == "expanding" or dispersion == "expanding":
                state = "EXPANDING"
                confidence = 0.8
                notes = "Volatility or opportunity set expanding."

            # 4. Construct Output Artifact
            output_data = {
                "liquidity_compression": {
                    "version": "1.0.0",
                    "computed_at": datetime.now().isoformat(),
                    "window_id": window_id,
                    "regime": "derived",
                    "state": state,
                    "contributing_factors": {
                        "volatility_regime": vol_regime,
                        "dispersion_state": dispersion
                    },
                    "confidence": confidence,
                    "notes": notes
                }
            }

            # 5. Emit Artifact
            output_path = output_dir / "liquidity_compression.json"
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
                
            print(f"  [Window: {window_id}] Watcher Emit (Liquidity): {state}")

        except Exception as e:
            print(f"[{window_id}] Liquidity Watcher Failed: {e}")
            # Non-blocking diagnostic
