"""
Decision Policy Engine (INT-POL-0).
Stateless evaluator translating Market Truth into Governance Permissions.

SAFETY INVARIANTS:
- READ-ONLY: Consumes factors/regime, produces policy. No side effects.
- DETERMINISTIC: Same input context -> Same policy output.
- ABSTRACT: Outputs permissions (ALLOW_LONG), not commands (BUY SPY).
- MARKET-SCOPED: Independent logic per market.
"""
import json
import datetime
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# F2 partiality controls
try:
    from governance.canonical_partiality import (
        CANONICAL_COMPLETE,
        load_or_detect_canonical_partiality,
        log_regime_degradation,
    )
except Exception:
    from src.governance.canonical_partiality import (  # type: ignore
        CANONICAL_COMPLETE,
        load_or_detect_canonical_partiality,
        log_regime_degradation,
    )

# Define allowed markets
ALLOWED_MARKETS = ["US", "INDIA"]

class DecisionPolicyEngine:
    def __init__(self, 
                 regime_path: Path, 
                 factor_path: Path, 
                 output_path: Path):
        self.regime_path = regime_path
        self.factor_path = factor_path
        self.output_path = output_path

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def evaluate(self) -> Dict[str, Any]:
        """
        Main evaluation entry point.
        """
        # 1. Load Contexts
        regime_data = self._load_json(self.regime_path).get("regime_context", {})
        factor_data = self._load_json(self.factor_path).get("factor_context", {})

        market = (regime_data.get("market") or factor_data.get("market") or "UNKNOWN").upper()

        # 2. Market Scope Guard
        if market not in ALLOWED_MARKETS:
            return self._build_policy(
                market=market,
                status="HALTED",
                permissions=[],
                reason=f"Market {market} not authorized for policy evaluation.",
            )

        # 3. Canonical partiality gate (F2: DEGRADE-ON-PARTIAL)
        partiality = load_or_detect_canonical_partiality(market)
        canonical_state = regime_data.get("canonical_state", partiality.get("canonical_state"))
        missing_roles = regime_data.get("canonical_missing_roles", partiality.get("missing_roles", []))
        stale_roles = regime_data.get("canonical_stale_roles", partiality.get("stale_roles", []))

        if canonical_state != CANONICAL_COMPLETE:
            degrade_reason = (
                f"Partial canonical inputs ({canonical_state}). "
                f"Missing roles: {missing_roles or ['NONE']}. "
                f"Stale roles: {stale_roles or ['NONE']}. "
                "Regime inference disabled."
            )
            log_regime_degradation(
                market=market,
                canonical_state=canonical_state,
                missing_roles=list(missing_roles),
                stale_roles=list(stale_roles),
                reason=degrade_reason,
                source="src/intelligence/decision_policy_engine.py",
            )
            return self._build_policy(
                market=market,
                status="HALTED",
                permissions=["OBSERVE_ONLY"],
                reason=degrade_reason,
                epistemic_grade="DEGRADED",
                regime_state="UNKNOWN",
                regime_confidence="DEGRADED",
                regime_reason="Partial canonical inputs",
                canonical_state=canonical_state,
                canonical_missing_roles=list(missing_roles),
                canonical_stale_roles=list(stale_roles),
            )

        # 4. Market logic (complete canonical only)
        if market == "US":
            return self._evaluate_us_policy(regime_data, factor_data)
        return self._evaluate_india_policy(regime_data, factor_data)

    def _evaluate_us_policy(self, regime: Dict[str, Any], factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates policy for US Market based on canonical logic.
        """
        market = "US"
        permissions = []
        blocks = []
        status = "ACTIVE"
        reasons = []
        
        # --- Input Extraction ---
        regime_code = regime.get("regime_code", regime.get("regime", "UNKNOWN"))
        regime_confidence = regime.get("regime_confidence", regime.get("confidence", "DECLARED"))
        canonical_state = regime.get("canonical_state", CANONICAL_COMPLETE)
        canonical_missing_roles = regime.get("canonical_missing_roles", [])
        canonical_stale_roles = regime.get("canonical_stale_roles", [])
        
        liq = factors.get("factors", {}).get("liquidity", {})
        liq_state = liq.get("state", "unknown")
        
        breadth = factors.get("factors", {}).get("momentum", {}).get("breadth", {})
        breadth_state = breadth.get("state", "neutral")
        
        # --- Logic: Constraint Accumulation ---
        
        # 1. Liquidity Check (The "Money" Gate)
        # Tight/Crisis money blocks entries.
        if liq_state in ["tight", "crisis"]:
            blocks.append("ALLOW_LONG_ENTRY")
            blocks.append("ALLOW_SHORT_ENTRY") # Squeeze risk often high in tight money
            reasons.append(f"Liquidity is {liq_state.upper()}. New entries blocked.")
            status = "RESTRICTED"
        else:
            # Liquidity neutral/loose allows us to proceed to Regime check
            pass

        # 2. Regime Check (The "Trend" Gate)
        if "ALLOW_LONG_ENTRY" not in blocks:
            if regime_code == "BULLISH":
                permissions.append("ALLOW_LONG_ENTRY")
                permissions.append("ALLOW_POSITION_HOLD")
                reasons.append("Regime BULLISH. Longs permitted.")
            
            elif regime_code == "BEARISH":
                permissions.append("ALLOW_SHORT_ENTRY")
                permissions.append("ALLOW_POSITION_HOLD") # Logic: Hold shorts or defensive longs?
                # For now, simplistic: Bearish means Risk Off or Short.
                # If Breadth is Tech Lead (Divergent), maybe allow specialized Longs?
                
                if breadth_state == "tech_lead":
                    permissions.append("ALLOW_LONG_ENTRY_SPECIAL")
                    reasons.append("Regime BEARISH but Tech Lead detected. Specialized Longs permitted.")
                else:
                    reasons.append("Regime BEARISH. General Longs discouraged.")
                    
            elif regime_code == "NEUTRAL":
                permissions.append("ALLOW_POSITION_HOLD")
                permissions.append("ALLOW_REBALANCING")
                reasons.append("Regime NEUTRAL. Hold/Rebalance only.")
            
            else:
                # Unknown/Uncertain
                permissions.append("OBSERVE_ONLY")
                status = "HALTED"
                reasons.append("Regime UNKNOWN. System Halted.")

        # 3. Breadth Check (The "Quality" Gate)
        # Assuming we have permission, does Breadth restrict it?
        # (Implemented simply above in Bearish case)

        # --- Final Assembly ---
        # Default if nothing allowed -> Observe
        if not permissions:
            permissions.append("OBSERVE_ONLY")
            status = "RESTRICTED"
            if not reasons: reasons.append("Default restriction.")

        return self._build_policy(
            market=market,
            status=status,
            permissions=permissions,
            reason=" | ".join(reasons),
            epistemic_grade="CANONICAL", # US Phase 10 is Canonical
            blocks=blocks,
            regime_state=regime_code,
            regime_confidence=regime_confidence,
            regime_reason=regime.get("regime_reason", "Regime evaluated on canonical-complete inputs."),
            canonical_state=canonical_state,
            canonical_missing_roles=canonical_missing_roles,
            canonical_stale_roles=canonical_stale_roles,
        )

    def _evaluate_india_policy(self, regime: Dict[str, Any], factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates policy for INDIA market when canonical inputs are complete.
        """
        market = "INDIA"
        permissions: List[str] = []
        blocks: List[str] = []
        reasons: List[str] = []
        status = "ACTIVE"

        regime_code = regime.get("regime_code", regime.get("regime", "UNKNOWN"))
        regime_confidence = regime.get("regime_confidence", regime.get("confidence", "DECLARED"))
        canonical_state = regime.get("canonical_state", CANONICAL_COMPLETE)
        canonical_missing_roles = regime.get("canonical_missing_roles", [])
        canonical_stale_roles = regime.get("canonical_stale_roles", [])

        liq = factors.get("factors", {}).get("liquidity", {})
        liq_state = liq.get("state", "unknown")

        if liq_state in ["tight", "crisis"]:
            blocks.extend(["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY"])
            reasons.append(f"Liquidity is {liq_state.upper()}. New entries blocked.")
            status = "RESTRICTED"

        if "ALLOW_LONG_ENTRY" not in blocks:
            if regime_code == "BULLISH":
                permissions.extend(["ALLOW_LONG_ENTRY", "ALLOW_POSITION_HOLD"])
                reasons.append("Regime BULLISH. Longs permitted.")
            elif regime_code == "BEARISH":
                permissions.extend(["ALLOW_SHORT_ENTRY", "ALLOW_POSITION_HOLD"])
                reasons.append("Regime BEARISH. Shorts permitted.")
            elif regime_code == "NEUTRAL":
                permissions.extend(["ALLOW_POSITION_HOLD", "ALLOW_REBALANCING"])
                reasons.append("Regime NEUTRAL. Hold/Rebalance only.")
            else:
                permissions.append("OBSERVE_ONLY")
                status = "HALTED"
                reasons.append("Regime UNKNOWN. System Halted.")

        if not permissions:
            permissions.append("OBSERVE_ONLY")
            status = "RESTRICTED"
            if not reasons:
                reasons.append("Default restriction.")

        return self._build_policy(
            market=market,
            status=status,
            permissions=permissions,
            reason=" | ".join(reasons),
            epistemic_grade="CANONICAL",
            blocks=blocks,
            regime_state=regime_code,
            regime_confidence=regime_confidence,
            regime_reason=regime.get("regime_reason", "Regime evaluated on canonical-complete inputs."),
            canonical_state=canonical_state,
            canonical_missing_roles=canonical_missing_roles,
            canonical_stale_roles=canonical_stale_roles,
        )

    def _build_policy(
        self,
        market: str,
        status: str,
        permissions: List[str],
        reason: str,
        epistemic_grade: str = "UNKNOWN",
        blocks: List[str] = None,
        regime_state: str = "UNKNOWN",
        regime_confidence: Any = "UNKNOWN",
        regime_reason: str = "Unavailable",
        canonical_state: str = "UNKNOWN",
        canonical_missing_roles: List[str] = None,
        canonical_stale_roles: List[str] = None,
    ) -> Dict[str, Any]:
        return {
            "policy_decision": {
                "market": market,
                "computed_at": datetime.datetime.now().isoformat(),
                "policy_state": status, # ACTIVE, RESTRICTED, HALTED
                "permissions": permissions,
                "blocked_actions": blocks or [],
                "reason": reason,
                "regime_state": regime_state,
                "regime_confidence": regime_confidence,
                "regime_reason": regime_reason,
                "canonical_state": canonical_state,
                "canonical_missing_roles": canonical_missing_roles or [],
                "canonical_stale_roles": canonical_stale_roles or [],
                "epistemic_health": {
                    "grade": epistemic_grade,
                    "proxy_status": "CANONICAL" if canonical_state == CANONICAL_COMPLETE else "DEGRADED",
                },
                "version": "1.1.0-F2-DEGRADE"
            }
        }

    def run(self):
        policy = self.evaluate()
        
        # Persist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(policy, f, indent=2)
            
        print(f"Policy Generated for {policy['policy_decision'].get('market')}: {policy['policy_decision'].get('policy_state')}")
        return policy

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", type=Path, required=True)
    parser.add_argument("--factor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    
    engine = DecisionPolicyEngine(args.regime, args.factor, args.output)
    engine.run()
