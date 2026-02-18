import os as _os
import sys as _sys
from typing import Dict, Any, List
from .capital_plan import get_capital_config, TOTAL_PAPER_CAPITAL

_CAP_PROJECT_ROOT = _os.path.abspath(
    _os.path.join(_os.path.dirname(__file__), "..", "..", "..")
)
if _CAP_PROJECT_ROOT not in _sys.path:
    _sys.path.insert(0, _CAP_PROJECT_ROOT)

try:
    from automation.invariants.layer_integrations import gate_l8_risk_caps as _gate_l8
except ImportError:  # pragma: no cover
    import logging as _logging
    _logging.getLogger(__name__).critical(
        "CATASTROPHIC FIREWALL UNAVAILABLE — L8 invariant gate disabled"
    )
    raise

def check_capital_readiness(eligibility_resolution: Dict[str, Any], regime: str = "NEUTRAL") -> Dict[str, Any]:
    """
    Validates if the current eligible strategies respect risk envelopes.
    Returns a READ-ONLY status.
    """
    config = get_capital_config()
    buckets = config["buckets"]
    
    # 1. Kill Switch Check (Mock - assume Disarmed for now)
    kill_switch = {
        "global": "DISARMED",
        "families": {}
    }
    
    # 2. Drawdown Check (Mock - assume 0% DD)
    current_drawdown = 0.0
    dd_state = "NORMAL"
    if current_drawdown > config["drawdown_triggers"]["FROZEN"]:
        dd_state = "FROZEN"
    elif current_drawdown > config["drawdown_triggers"]["CRITICAL"]:
        dd_state = "CRITICAL"
    elif current_drawdown > config["drawdown_triggers"]["WARNING"]:
        dd_state = "WARNING"
        
    # 3. Simulate Allocation (Greedy/Naive for validation)
    # Count eligible per family
    family_counts = {}
    for strat in eligibility_resolution.get("strategies", []):
        if strat.get("eligible"):
            fam = strat.get("family", "unknown")
            family_counts[fam] = family_counts.get(fam, 0) + 1
            
    # Check Buckets
    allocations = {}
    violations = []
    
    for fam, count in family_counts.items():
        if count > 0:
            # Symbolic: Assign 5% per strategy
            needed = count * 0.05
            ceiling = buckets.get(fam, 0.0)
            
            # Regime modifiers
            if regime == "BEAR_RISK_OFF" and fam == "momentum":
                ceiling = 0.10
            
            if needed > ceiling:
                violations.append(f"Family '{fam}' needs {needed*100}% but ceiling is {ceiling*100}%")
                allocations[fam] = ceiling # Cap at ceiling
            else:
                allocations[fam] = needed
                
    total_alloc = sum(allocations.values())
    
    readiness_status = "READY"
    if dd_state == "FROZEN" or kill_switch["global"] == "ARMED":
        readiness_status = "NOT_READY"
    
    result = {
        "status": readiness_status,
        "drawdown_state": dd_state,
        "kill_switch": kill_switch,
        "allocations": allocations,
        "total_exposure": total_alloc,
        "violations": violations,
        "meta": {
            "total_capital": TOTAL_PAPER_CAPITAL,
            "regime": regime
        }
    }
    # ── L8 Catastrophic Invariant Gate ──────────────────────────────────────
    _gate_l8(total_alloc, max_exposure=1.0)
    return result
