"""
Fragility & Stress Policy Engine (INT-POL-1).
Evaluates systemic risk to constrain decision permissions.
"""
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any

ALLOWED_MARKETS = ["US", "INDIA"]

STRESS_LEVELS = {
    "NORMAL": [],
    "ELEVATED_STRESS": ["ALLOW_SHORT_ENTRY", "ALLOW_LONG_ENTRY_SPECIAL"],
    "SYSTEMIC_STRESS": ["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY", "ALLOW_REBALANCING", "ALLOW_LONG_ENTRY_SPECIAL"],
    "TRANSITION_UNCERTAIN": ["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY", "ALLOW_LONG_ENTRY_SPECIAL"]
}

class FragilityEngine:
    def __init__(self, factor_path: Path, output_path: Path):
        self.factor_path = factor_path
        self.output_path = output_path

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def evaluate(self, market: str) -> Dict[str, Any]:
        """
        Main evaluation entry point for fragility.
        """
        if market not in ALLOWED_MARKETS:
            return self._build_fragility(market, "NOT_EVALUATED", "Unauthorized market.")

        if market == "INDIA":
            return self._build_fragility(
                market="INDIA",
                state="NOT_EVALUATED",
                reason="DEGRADED_PROXY_STATE: Fragility evaluation impossible with current data resolution.",
                signals={s: "DEGRADED" for s in ["liquidity", "volatility", "correlation", "regime_transition"]},
                blocked=STRESS_LEVELS["SYSTEMIC_STRESS"] # India is effectively systemic stress equivalent
            )

        # US Evaluation Logic
        factor_data = self._load_json(self.factor_path).get("factor_context", {})
        return self._evaluate_us_fragility(factor_data)

    def _evaluate_us_fragility(self, factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        US-specific fragility evaluation.
        """
        signals = {
            "liquidity": "STABLE",
            "volatility": "MODERATE",
            "correlation": "LOW"
        }
        
        # Simple Logic Based on Factor Context
        liq_state = factors.get("factors", {}).get("liquidity", {}).get("state", "unknown")
        vol_state = factors.get("factors", {}).get("momentum", {}).get("volatility", {}).get("state", "neutral")
        
        if liq_state == "crisis":
            state = "SYSTEMIC_STRESS"
            signals["liquidity"] = "CRISIS"
            reason = "Liquidity Crisis detected. All entries blocked."
        elif liq_state == "tight" or vol_state == "extreme":
            state = "ELEVATED_STRESS"
            signals["liquidity"] = "TIGHT" if liq_state == "tight" else "STABLE"
            signals["volatility"] = "EXTREME" if vol_state == "extreme" else "MODERATE"
            reason = "Elevated stress detected in Liquidity/Volatility. High-convexity entries blocked."
        else:
            state = "NORMAL"
            reason = "Systemic signals within normal ranges."

        return self._build_fragility(
            market="US",
            state=state,
            reason=reason,
            signals=signals,
            blocked=STRESS_LEVELS.get(state, [])
        )

    def _build_fragility(self, market: str, state: str, reason: str, signals: Dict[str, str] = None, blocked: List[str] = None) -> Dict[str, Any]:
        return {
            "fragility_policy": {
                "market": market,
                "stress_state": state,
                "signals": signals or {},
                "blocked_intents": blocked or [],
                "reason": reason,
                "evaluation_timestamp": datetime.datetime.now().isoformat(),
                "epoch_id": "TE-2026-01-30"
            }
        }

    def run(self, market: str):
        policy = self.evaluate(market)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(policy, f, indent=2)
        print(f"Fragility Policy Generated for {market}: {policy['fragility_policy'].get('stress_state')}")
        return policy

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", type=str, required=True)
    parser.add_argument("--factor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    
    engine = FragilityEngine(args.factor, args.output)
    engine.run(args.market)
