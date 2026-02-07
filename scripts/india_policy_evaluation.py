"""
India Policy & Fragility Evaluation Pipeline.
Generates Factor Context, Regime Context, Decision Policy, and Fragility Policy for India.

EXECUTION MODE: REAL_RUN
DATA MODE: REAL_ONLY
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
INTEL_DIR = DOCS_DIR / "intelligence"
CONTEXT_DIR = DOCS_DIR / "evolution" / "context"

# Ensure directories exist
INTEL_DIR.mkdir(parents=True, exist_ok=True)
CONTEXT_DIR.mkdir(parents=True, exist_ok=True)


def load_india_data() -> Dict[str, pd.DataFrame]:
    """
    Loads all canonical India proxy data.
    """
    data_dir = PROJECT_ROOT / "data" / "india"
    
    data = {}
    for name in ["NIFTY50", "BANKNIFTY", "INDIAVIX", "IN10Y"]:
        path = data_dir / f"{name}.csv"
        if path.exists():
            df = pd.read_csv(path)
            df.columns = [c.title() for c in df.columns]
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date').sort_index()
            data[name] = df
            print(f"Loaded {name}: {len(df)} rows")
        else:
            print(f"WARNING: {name} not found at {path}")
    
    return data


def compute_regime(nifty: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes regime state from NIFTY50.
    """
    if nifty is None or len(nifty) < 50:
        return {"regime_code": "UNKNOWN", "regime_label": "Insufficient Data"}
    
    # Use SMA50 vs SMA200 crossover logic
    nifty['SMA50'] = nifty['Close'].rolling(50).mean()
    nifty['SMA200'] = nifty['Close'].rolling(200).mean()
    
    latest = nifty.iloc[-1]
    sma50 = latest.get('SMA50', 0)
    sma200 = latest.get('SMA200', 0)
    close = latest.get('Close', 0)
    
    if pd.isna(sma50) or pd.isna(sma200):
        return {"regime_code": "NEUTRAL", "regime_label": "Calculating (Insufficient SMA History)"}
    
    if close > sma50 > sma200:
        return {"regime_code": "BULLISH", "regime_label": "Bullish Trend"}
    elif close < sma50 < sma200:
        return {"regime_code": "BEARISH", "regime_label": "Bearish Trend"}
    else:
        return {"regime_code": "NEUTRAL", "regime_label": "Range-Bound / Mixed"}


def compute_volatility(indiavix: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes volatility state from India VIX.
    """
    if indiavix is None or len(indiavix) < 10:
        return {"level": 0, "state": "unknown"}
    
    latest_vix = indiavix['Close'].iloc[-1]
    
    if latest_vix > 30:
        state = "extreme"
    elif latest_vix > 20:
        state = "elevated"
    elif latest_vix > 12:
        state = "normal"
    else:
        state = "low"
    
    return {"level": float(latest_vix), "state": state}


def compute_liquidity(in10y: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes liquidity state from IN10Y yield.
    """
    if in10y is None or len(in10y) < 10:
        return {"level": 0, "state": "unknown"}
    
    latest_yield = in10y['Close'].iloc[-1]
    
    # Higher yields generally indicate tighter conditions
    if latest_yield > 8.0:
        state = "tight"
    elif latest_yield > 7.0:
        state = "neutral"
    else:
        state = "loose"
    
    return {"level": float(latest_yield), "state": state}


def compute_breadth(nifty: pd.DataFrame, banknifty: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes breadth state from NIFTY50 vs BANKNIFTY relative strength.
    """
    if nifty is None or banknifty is None or len(nifty) < 20 or len(banknifty) < 20:
        return {"state": "unknown"}
    
    # Calculate 20-day returns
    nifty_ret = (nifty['Close'].iloc[-1] / nifty['Close'].iloc[-20]) - 1
    bank_ret = (banknifty['Close'].iloc[-1] / banknifty['Close'].iloc[-20]) - 1
    
    if bank_ret > nifty_ret + 0.02:
        state = "bank_lead"  # Financials leading
    elif nifty_ret > bank_ret + 0.02:
        state = "broad_lead"  # Broad market leading
    else:
        state = "neutral"
    
    return {"state": state, "nifty_20d_ret": float(nifty_ret), "bank_20d_ret": float(bank_ret)}


def build_factor_context(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Builds the complete factor context for India.
    """
    regime = compute_regime(data.get("NIFTY50"))
    volatility = compute_volatility(data.get("INDIAVIX"))
    liquidity = compute_liquidity(data.get("IN10Y"))
    breadth = compute_breadth(data.get("NIFTY50"), data.get("BANKNIFTY"))
    
    return {
        "factor_context": {
            "market": "INDIA",
            "computed_at": datetime.now().isoformat(),
            "factors": {
                "momentum": {
                    "state": regime["regime_code"].lower(),
                    "confidence": 0.8
                },
                "volatility": volatility,
                "liquidity": liquidity,
                "breadth": breadth
            },
            "regime_input": regime,
            "sufficiency": {
                "equity": True,
                "volatility": True,
                "rates": True,
                "sector": True
            },
            "version": "1.0.0-INDIA-CANONICAL"
        }
    }


def build_regime_context(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Builds the regime context for India.
    """
    regime = compute_regime(data.get("NIFTY50"))
    
    return {
        "regime_context": {
            "market": "INDIA",
            "computed_at": datetime.now().isoformat(),
            "regime_code": regime["regime_code"],
            "regime_label": regime["regime_label"],
            "inputs": ["NIFTY50"],
            "viability": "CANONICAL",
            "version": "1.0.0-INDIA"
        }
    }


def evaluate_decision_policy(factor_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates India decision policy based on factor context.
    """
    factors = factor_context.get("factor_context", {}).get("factors", {})
    regime = factor_context.get("factor_context", {}).get("regime_input", {})
    
    regime_code = regime.get("regime_code", "UNKNOWN")
    liq_state = factors.get("liquidity", {}).get("state", "unknown")
    vol_state = factors.get("volatility", {}).get("state", "unknown")
    
    permissions = []
    blocks = []
    reasons = []
    status = "ACTIVE"
    
    # Liquidity Gate
    if liq_state == "tight":
        blocks.extend(["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY"])
        reasons.append("Liquidity TIGHT. New entries blocked.")
        status = "RESTRICTED"
    
    # Regime Logic
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
            reasons.append("Regime UNKNOWN. System halted.")
    
    # Default if empty
    if not permissions:
        permissions.append("OBSERVE_ONLY")
        status = "RESTRICTED"
    
    return {
        "policy_decision": {
            "market": "INDIA",
            "computed_at": datetime.now().isoformat(),
            "policy_state": status,
            "permissions": permissions,
            "blocked_actions": blocks,
            "reason": " | ".join(reasons) if reasons else "Default policy.",
            "epistemic_health": {
                "grade": "CANONICAL",
                "proxy_status": "CANONICAL"
            },
            "version": "1.0.0-INDIA"
        }
    }


def evaluate_fragility_policy(decision_policy: Dict[str, Any], factor_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates India fragility policy (permission subtraction).
    """
    base_permissions = set(decision_policy.get("policy_decision", {}).get("permissions", []))
    factors = factor_context.get("factor_context", {}).get("factors", {})
    
    vol_level = factors.get("volatility", {}).get("level", 0)
    liq_state = factors.get("liquidity", {}).get("state", "neutral")
    
    revocations = set()
    stress_state = "NORMAL"
    reasons = []
    
    # Volatility Check
    if vol_level > 25:
        stress_state = "SYSTEMIC_STRESS"
        revocations.update(["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY", "ALLOW_REBALANCING"])
        reasons.append(f"CRITICAL VOLATILITY (India VIX: {vol_level:.2f} > 25).")
    elif vol_level > 18:
        stress_state = "ELEVATED_STRESS"
        reasons.append(f"Elevated Volatility (India VIX: {vol_level:.2f}).")
    
    # Liquidity Crisis
    if liq_state == "crisis":
        stress_state = "SYSTEMIC_STRESS"
        revocations.update(["ALLOW_LONG_ENTRY", "ALLOW_SHORT_ENTRY"])
        reasons.append("Liquidity CRISIS.")
    
    # Apply subtraction
    final_permissions = base_permissions - revocations
    if not final_permissions:
        final_permissions.add("OBSERVE_ONLY")
    
    return {
        "fragility_context": {
            "market": "INDIA",
            "computed_at": datetime.now().isoformat(),
            "stress_state": stress_state,
            "constraints_applied": list(revocations),
            "final_authorized_intents": list(final_permissions),
            "reason": " | ".join(reasons) if reasons else "Nominal Conditions.",
            "version": "1.0.0-INDIA-SUBTRACTIVE"
        }
    }


def main():
    print("=" * 60)
    print("INDIA POLICY & FRAGILITY EVALUATION")
    print("=" * 60)
    print()
    
    # 1. Load Data
    print("[1/5] Loading India canonical data...")
    data = load_india_data()
    print()
    
    # 2. Build Factor Context
    print("[2/5] Building Factor Context...")
    factor_context = build_factor_context(data)
    factor_path = CONTEXT_DIR / "factor_context_INDIA.json"
    with open(factor_path, 'w', encoding='utf-8') as f:
        json.dump(factor_context, f, indent=2)
    print(f"  Saved: {factor_path}")
    print()
    
    # 3. Build Regime Context
    print("[3/5] Building Regime Context...")
    regime_context = build_regime_context(data)
    regime_path = CONTEXT_DIR / "regime_context_INDIA.json"
    with open(regime_path, 'w', encoding='utf-8') as f:
        json.dump(regime_context, f, indent=2)
    print(f"  Saved: {regime_path}")
    print()
    
    # 4. Evaluate Decision Policy
    print("[4/5] Evaluating Decision Policy...")
    decision_policy = evaluate_decision_policy(factor_context)
    decision_path = INTEL_DIR / "decision_policy_INDIA.json"
    with open(decision_path, 'w', encoding='utf-8') as f:
        json.dump(decision_policy, f, indent=2)
    print(f"  Saved: {decision_path}")
    print(f"  Status: {decision_policy['policy_decision']['policy_state']}")
    print(f"  Permissions: {decision_policy['policy_decision']['permissions']}")
    print()
    
    # 5. Evaluate Fragility Policy
    print("[5/5] Evaluating Fragility Policy...")
    fragility = evaluate_fragility_policy(decision_policy, factor_context)
    fragility_path = INTEL_DIR / "fragility_context_INDIA.json"
    with open(fragility_path, 'w', encoding='utf-8') as f:
        json.dump(fragility, f, indent=2)
    print(f"  Saved: {fragility_path}")
    print(f"  Stress State: {fragility['fragility_context']['stress_state']}")
    print(f"  Final Intents: {fragility['fragility_context']['final_authorized_intents']}")
    print()
    
    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    
    return decision_policy, fragility


if __name__ == "__main__":
    main()
