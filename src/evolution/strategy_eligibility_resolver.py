"""
Strategy Eligibility Resolver.
Resolves daily eligibility for all registered strategies using frozen contracts.
This is the RUNTIME resolver - it does NOT modify strategies or run evolution.

Version: 1.0
Date: 2026-01-29
"""
import datetime
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import frozen registry
from strategy.registry import STRATEGY_REGISTRY


# Factor state ordering for min/max comparisons
STATE_ORDER = {
    # Momentum
    "NONE": 0, "EMERGING": 1, "CONFIRMED": 2,
    # Expansion  
    "EARLY": 1,
    # Dispersion
    "BREAKOUT": 1,
    # Liquidity
    "NEUTRAL": 0, "COMPRESSED": 1, "STRESSED": 2
}


def _check_factor_contract(contract: dict, current_factors: dict) -> tuple:
    """
    Checks if current factor states satisfy the contract.
    Returns (passed: bool, blocking_reason: str or None)
    """
    if not contract:
        return True, None
    
    for factor_name, requirements in contract.items():
        # Skip external factors not in our watcher set
        if factor_name in ["yield_curve", "vrp"]:
            # External factors default to blocked until wired
            return False, f"{factor_name} not yet measured"
        
        current_state = current_factors.get(factor_name, "NONE")
        current_order = STATE_ORDER.get(current_state, 0)
        
        # Check min_state
        if "min_state" in requirements:
            required_order = STATE_ORDER.get(requirements["min_state"], 0)
            if current_order < required_order:
                return False, f"{factor_name}: {current_state} < {requirements['min_state']}"
        
        # Check max_state
        if "max_state" in requirements:
            max_order = STATE_ORDER.get(requirements["max_state"], 0)
            if current_order > max_order:
                return False, f"{factor_name}: {current_state} > {requirements['max_state']}"
        
        # Check exact_state
        if "exact_state" in requirements:
            if current_state != requirements["exact_state"]:
                return False, f"{factor_name}: {current_state} != {requirements['exact_state']}"
    
    return True, None


def _check_regime_contract(contract: dict, current_regime: str) -> tuple:
    """
    Checks if current regime satisfies the contract.
    Returns (passed: bool, blocking_reason: str or None)
    """
    if not contract:
        return True, None
    
    allowed = contract.get("allow", [])
    forbidden = contract.get("forbid", [])
    
    if forbidden and current_regime in forbidden:
        return False, f"Regime {current_regime} forbidden"
    
    if allowed and current_regime not in allowed:
        return False, f"Regime {current_regime} not allowed"
    
    return True, None


def resolve_strategy_eligibility(
    strategy_id: str,
    strategy_def: dict,
    current_regime: str,
    current_factors: dict,
    resolved_at: str
) -> dict:
    """
    Resolves eligibility for a single strategy.
    
    Returns:
        dict with strategy_id, eligibility_status, primary_blocker, blocking_reason, resolved_at
    """
    # Check regime contract
    regime_contract = strategy_def.get("regime_contract", {})
    regime_ok, regime_reason = _check_regime_contract(regime_contract, current_regime)
    
    # Check factor contract
    factor_contract = strategy_def.get("factor_contract", {})
    factor_ok, factor_reason = _check_factor_contract(factor_contract, current_factors)
    
    # Determine eligibility
    eligible = regime_ok and factor_ok
    
    # Determine status and blocker
    if eligible:
        eligibility_status = "ELIGIBLE"
        primary_blocker = None
        blocking_reason = None
    else:
        # Determine primary blocker
        if not regime_ok:
            primary_blocker = "REGIME"
            blocking_reason = regime_reason
        elif not factor_ok:
            primary_blocker = "FACTOR"
            blocking_reason = factor_reason
        else:
            primary_blocker = "SAFETY"
            blocking_reason = "Unknown constraint"
        
        # Determine if conditional or blocked
        if strategy_def.get("safety_behavior") == "degrade":
            eligibility_status = "CONDITIONAL"
        else:
            eligibility_status = "BLOCKED"
    
    return {
        "strategy_id": strategy_id,
        "strategy_name": strategy_def.get("name", strategy_id),
        "family": strategy_def.get("family", "unknown"),
        "eligibility_status": eligibility_status,
        "primary_blocker": primary_blocker,
        "blocking_reason": blocking_reason,
        "activation_hint": strategy_def.get("activation_hint", ""),
        "resolved_at": resolved_at
    }


def resolve_all_strategies(
    current_regime: str,
    current_factors: dict
) -> dict:
    """
    Resolves eligibility for ALL registered strategies.
    
    Args:
        current_regime: Current regime state (e.g., "NEUTRAL", "BULL_VOL")
        current_factors: Dict of current factor states
            {
                "momentum": "NONE" | "EMERGING" | "CONFIRMED",
                "expansion": "NONE" | "EARLY" | "CONFIRMED",
                "dispersion": "NONE" | "BREAKOUT",
                "liquidity": "NEUTRAL" | "COMPRESSED" | "STRESSED"
            }
    
    Returns:
        dict with resolution summary and per-strategy results
    """
    from evolution.strategy_evolution_guard import get_evolution_version, get_frozen_date
    
    resolved_at = datetime.datetime.now().isoformat()
    
    results = []
    summary = {
        "total": 0,
        "eligible": 0,
        "conditional": 0,
        "blocked": 0
    }
    
    for strat_id, strat_def in STRATEGY_REGISTRY.items():
        result = resolve_strategy_eligibility(
            strat_id, strat_def, current_regime, current_factors, resolved_at
        )
        results.append(result)
        summary["total"] += 1
        
        if result["eligibility_status"] == "ELIGIBLE":
            summary["eligible"] += 1
        elif result["eligibility_status"] == "CONDITIONAL":
            summary["conditional"] += 1
        else:
            summary["blocked"] += 1
    
    return {
        "evolution_version": get_evolution_version(),
        "evolution_frozen_date": get_frozen_date(),
        "resolved_at": resolved_at,
        "current_regime": current_regime,
        "current_factors": current_factors,
        "summary": summary,
        "strategies": results
    }


def persist_daily_resolution(resolution: dict, output_dir: Path) -> Path:
    """
    Persists the daily resolution snapshot to a JSON file.
    
    Args:
        resolution: The resolution dict from resolve_all_strategies()
        output_dir: Directory to write the snapshot
    
    Returns:
        Path to the written file
    """
    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Use date from resolved_at for filename
    resolved_at = resolution.get("resolved_at", datetime.datetime.now().isoformat())
    date_str = resolved_at.split("T")[0]  # YYYY-MM-DD
    
    filename = f"{date_str}.json"
    output_path = output_dir / filename
    
    with open(output_path, "w") as f:
        json.dump(resolution, f, indent=2)
    
    return output_path
