"""
Factor Context Builder (EV-RUN-CTX-FACTOR).
Establishes the Factor Context for a specific execution window.

SAFETY INVARIANTS:
- READ-ONLY: Loads data/regime, does not modify.
- ATOMIC: Computed once per window.
- SHARED: All strategies see the same factors.
- OBSERVATIONAL: No predictive logic, no strategy optimization.
"""
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from evolution.profile_loader import EvaluationProfile

class FactorContextBuilder:
    """
    Builds and persists Factor Context for an EV-RUN window.
    """
    
    def __init__(self, context_path: Path, output_path: Path, profile: Optional[EvaluationProfile] = None):
        self.context_path = context_path # Path to regime_context.json
        self.output_path = output_path   # Path to factor_context.json (output)
        self.profile = profile

    def _load_regime_context(self) -> Dict[str, Any]:
        if not self.context_path.exists():
            raise FileNotFoundError(f"Regime Context not found at {self.context_path}")
        with open(self.context_path, 'r', encoding='utf-8') as f:
            return json.load(f)["regime_context"]

    def build(self) -> Dict[str, Any]:
        # 1. Load Regime Context
        regime_ctx = self._load_regime_context()
        window = regime_ctx["evaluation_window"]
        
        # 2. "Observe" Factors
        # NOTE: In Phase 3 (Structure), we generate a STRUCTURALLY VALID context.
        # Since we don't have a live Data Engine yet, we return valid "Neutral" state.
        # This proves the Binding working without halluncinating data.
        
        # v1.1 Observational Logic (Mocked for Structural Verification)
        # Includes strict backward compatibility for v1 consumers.
        
        # Momentum
        mom_level = "neutral"
        factors = {
            "momentum": {
                # v1.1 Fields
                "level": {"state": mom_level, "confidence": 0.5},
                "acceleration": {"state": "flat", "confidence": 0.5},
                "persistence": {"state": "intermittent", "confidence": 0.5},
                # v1.2 Fields
                "breadth": {"state": "narrow", "confidence": 0.5},
                "dispersion": {"state": "stable", "confidence": 0.5},
                "time_in_state": {"state": "medium", "confidence": 0.5},
                # v1 Compatibility (Aliasing)
                "strength": mom_level
            },
            "value": {
                # v1.1 Fields
                "spread": {"state": "neutral", "confidence": 0.5}, # Kept as primary
                "trend": {"state": "flat", "confidence": 0.5},
                # v1.3 Fields
                "dispersion": {"state": "stable", "confidence": 0.5},
                "mean_reversion_pressure": {"state": "low", "confidence": 0.5}
            },
            "quality": {
                # v1.1 Fields
                "signal": {"state": "neutral", "confidence": 0.5},
                "stability": {"state": "stable", "confidence": 0.5},
                # v1.3 Fields
                "defensiveness": {"state": "neutral", "confidence": 0.5},
                "drawdown_resilience": {"state": "medium", "confidence": 0.5}
            },
            "volatility": {
                "confidence": 0.5
            },
            "meta": {
                "factor_alignment": "mixed",
                "momentum_quality": "noisy",
                "alpha_environment": "mixed",
                "notes": None
            }
        }

        # 3. Construct Context Object
        factor_context = {
            "factor_context": {
                "computed_at": datetime.now().isoformat(),
                "window": window,
                "factors": factors,
                "inputs_used": ["price_series", "volatility_index"],
                "validity": {
                    "viable": True,
                    "reason": "Structural binding verification (mock data)"
                },
                "version": "1.3.0"
            }
        }

        # 4. Persist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(factor_context, f, indent=2)
            
        print(f"Generated Factor Context at: {self.output_path}")
        return factor_context

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EV-RUN-CTX-FACTOR Builder")
    parser.add_argument("--context", type=Path, required=True, help="Path to regime_context.json")
    parser.add_argument("--output", type=Path, required=True, help="Path to output factor_context.json")
    args = parser.parse_args()

    try:
        builder = FactorContextBuilder(context_path=args.context, output_path=args.output)
        builder.build()
    except Exception as e:
        print(f"FACTOR BUILD FAILURE: {e}")
        sys.exit(1)
