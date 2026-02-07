"""
Fragility & Stress Policy Engine (INT-POL-1).
Systemic Circuit Breaker that subtracts permissions based on environmental risk.

SAFETY INVARIANTS:
- SUBTRACTIVE-ONLY: Can revoke permissions, never grant them.
- READ-ONLY: Consumes policy/truth, produces constraints. No side effects.
- DETERMINISTIC: Same input context -> Same constraint output.
- MARKET-SCOPED: Independent logic per market.
"""
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any

ALLOWED_MARKETS = ["US", "INDIA"]

class FragilityPolicyEngine:
    def __init__(self, 
                 decision_policy_path: Path, 
                 factor_path: Path, # Need raw factors for VIX/Stress signals
                 output_path: Path):
        self.decision_policy_path = decision_policy_path
        self.factor_path = factor_path
        self.output_path = output_path

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def evaluate(self) -> Dict[str, Any]:
        # 1. Load Inputs
        decision_wrapper = self._load_json(self.decision_policy_path)
        decision_data = decision_wrapper.get("policy_decision", {})
        
        factor_wrapper = self._load_json(self.factor_path)
        factor_data = factor_wrapper.get("factor_context", {})
        
        market = decision_data.get("market", "UNKNOWN")
        base_permissions = set(decision_data.get("permissions", []))
        
        # 2. Market Scope Guard
        if market not in ALLOWED_MARKETS:
            return self._build_fragility_output(
                market=market,
                stress_state="NOT_EVALUATED",
                revocations=[],
                final_permissions=list(base_permissions), # Pass-through if unknown
                reason=f"Market {market} not authorized for fragility evaluation."
            )

        # 3. India Logic (Hard Stop / Redundant Check)
        if market == "INDIA":
            return self._build_fragility_output(
                market="INDIA",
                stress_state="NOT_EVALUATED",
                revocations=[],
                final_permissions=["OBSERVE_ONLY"], # Force choke
                reason="DEGRADED_PROXY_STATE: Fragility redundant for degraded surrogate."
            )

        # 4. US Logic (Stress Detection)
        return self._evaluate_us_fragility(base_permissions, factor_data)

    def _evaluate_us_fragility(self, base_permissions: set, factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates systemic stress for US Market.
        """
        market = "US"
        revocations = set()
        stress_state = "NORMAL"
        reasons = []
        
        # --- Signal Detection ---
        
        # 1. Volatility Shock
        # Check raw VIX level
        vol_level = factors.get("factors", {}).get("volatility", {}).get("level", 0.0)
        
        is_vol_shock = False
        if vol_level > 35.0:
            is_vol_shock = True
            reasons.append(f"CRITICAL VOLATILITY ({vol_level:.2f} > 35).")
            stress_state = "SYSTEMIC_STRESS"
        elif vol_level > 25.0:
            reasons.append(f"Elevated Volatility ({vol_level:.2f}).")
            if stress_state == "NORMAL": stress_state = "ELEVATED_STRESS"

        # 2. Liquidity Stress (Redundant check to base policy but stricter)
        liq_state = factors.get("factors", {}).get("liquidity", {}).get("state", "neutral")
        if liq_state == "crisis":
            reasons.append("LIQUIDITY CRISIS detected.")
            stress_state = "SYSTEMIC_STRESS"
        
        # --- Constraint Application (Subtract Permissions) ---
        
        if stress_state == "SYSTEMIC_STRESS":
            # Block ALL Entries and non-defensive actions
            revocations.update(["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY", "ALLOW_LONG_ENTRY_SPECIAL", "ALLOW_REBALANCING"])
            reasons.append("Blocking ALL entries due to Systemic Stress.")
            
        elif stress_state == "ELEVATED_STRESS":
            # Block Aggressive Entries?
            # For now, just logging warning, maybe rely on DecisionPolicy's prudence.
            # But let's demonstrate subtraction:
            if "ALLOW_LONG_ENTRY_SPECIAL" in base_permissions:
                 # In elevated stress, maybe "Special" trades are too risky?
                 # Decision: No, keep them for now, but flag it.
                 pass
        
        elif stress_state == "TRANSITION_UNCERTAIN":
             revocations.update(["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY"])
             reasons.append("Regime Transition. Whipsaw protection active.")

        # --- Final Intersection ---
        # Final = Base - Revocations
        # Use set difference
        final_permissions = base_permissions - revocations
        
        # If set becomes empty, default to OBSERVE_ONLY
        if not final_permissions:
            final_permissions.add("OBSERVE_ONLY")

        return self._build_fragility_output(
            market=market,
            stress_state=stress_state,
            revocations=list(revocations),
            final_permissions=list(final_permissions),
            reason=" | ".join(reasons) if reasons else "Nominal Conditions."
        )

    def _build_fragility_output(self, market: str, stress_state: str, revocations: List[str], final_permissions: List[str], reason: str) -> Dict[str, Any]:
        return {
            "fragility_context": {
                "market": market,
                "computed_at": datetime.datetime.now().isoformat(),
                "stress_state": stress_state,
                "constraints_applied": revocations,
                "final_authorized_intents": final_permissions,
                "reason": reason,
                "version": "1.0.0-SUBTRACTIVE"
            }
        }

    def run(self):
        policy = self.evaluate()
        
        # Persist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(policy, f, indent=2)
            
        print(f"Fragility Policy for {policy['fragility_context'].get('market')}: {policy['fragility_context'].get('stress_state')}")
        return policy

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--factor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    
    engine = FragilityPolicyEngine(args.decision, args.factor, args.output)
    engine.run()
