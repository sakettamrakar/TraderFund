from typing import Dict, Any, List, Optional
from dashboard.backend.utils.filesystem import get_latest_tick_dir, get_ticks_history, read_json_safe, PROJECT_ROOT

def _get_family_status_from_resolution(resolution: Dict[str, Any], family_id: str) -> str:
    strategies = resolution.get("strategies", [])
    family_strats = [s for s in strategies if s.get("family") == family_id]
    if not family_strats:
        return "UNKNOWN"
        
    has_eligible = any(s.get("eligibility_status") == "ELIGIBLE" for s in family_strats)
    if has_eligible:
        return "ELIGIBLE"
        
    has_conditional = any(s.get("eligibility_status") == "CONDITIONAL" for s in family_strats)
    if has_conditional:
        return "CONDITIONAL"
        
    return "GATED"

def _calculate_family_durations(families: Dict[str, Any], market: str) -> Dict[str, str]:
    history = get_ticks_history(limit=20)
    durations = {}
    current_statuses = {}
    
    # Target statuses based on current data
    for fid, fdoc in families.items():
        if fdoc['eligible_count'] > 0:
            current_statuses[fid] = "ELIGIBLE"
        elif any(s['eligibility_status'] == 'conditional' for s in fdoc['strategies']):
            current_statuses[fid] = "CONDITIONAL"
        else:
            current_statuses[fid] = "GATED"
            
    # Scan history
    for fid, current_status in current_statuses.items():
        count = 0
        for d in history:
            res_path = d / market / "strategy_resolution.json"
            if not res_path.exists():
                break
            
            res_data = read_json_safe(res_path)
            h_status = _get_family_status_from_resolution(res_data, fid)
            
            if h_status == current_status:
                count += 1
            else:
                break
        durations[fid] = f"{count} ticks"
        
    return durations


def load_strategy_eligibility(market: str = "US") -> Dict[str, Any]:
    """
    Returns daily strategy eligibility from persisted snapshot.
    Uses frozen Strategy Evolution v1 - no live recomputation.
    """
    # First, try to read from daily resolution snapshot (preferred)
    # TODO: Partition daily resolution by market?
    daily_dir = PROJECT_ROOT / "docs" / "evolution" / "daily_strategy_resolution"
    
    resolution = None
    # For now, daily resolution is global or assumed US?
    # Strict correction: we should read from tick if partitioned.
    
    # Try Tick First for Scoped Resolution
    latest_tick = get_latest_tick_dir()
    if latest_tick:
        resolution = read_json_safe(latest_tick / market / "strategy_resolution.json")
    
    if not resolution and daily_dir.exists():
        # Find the latest snapshot (fallback to global)
        snapshots = sorted([f for f in daily_dir.iterdir() if f.suffix == ".json"], reverse=True)
        if snapshots:
            resolution = read_json_safe(snapshots[0])
    
    if not resolution:
        return {"strategies": [], "families": {}, "evolution_version": "v1", "error": "No resolution snapshot found"}
    
    # Build family groupings for UI
    strategies_raw = resolution.get("strategies", [])
    families = {}
    
    FAMILY_EXPLANATIONS = {
        "momentum": "Momentum strategies activate when the market is expanding and directional conviction is confirmed.",
        "mean_reversion": "Mean reversion strategies activate in quiet, low-momentum environments when volatility is contracting.",
        "value": "Value strategies are regime-robust and always structurally eligible when evolution permits.",
        "quality": "Quality/Defensive strategies are regime-robust and always structurally eligible when evolution permits.",
        "carry": "Carry strategies activate in calm markets with positive yield curves and stable liquidity.",
        "volatility": "Volatility strategies depend on variance risk premium and expansion/contraction dynamics.",
        "spread": "Spread strategies require dispersion to create meaningful relative mispricings.",
        "stress": "Stress strategies only activate during crisis regimes with liquidity compression."
    }
    
    for s in strategies_raw:
        family = s.get("family", "unknown")
        if family not in families:
            families[family] = {
                "name": family.replace("_", " ").title(),
                "strategies": [],
                "eligible_count": 0,
                "total_count": 0,
                "explanation": FAMILY_EXPLANATIONS.get(family, "")
            }
        
        # Map to UI format
        ui_strategy = {
            "id": s.get("strategy_id"),
            "strategy": s.get("strategy_name"),
            "family": family,
            "intent": s.get("intent", ""),
            "regime_ok": s.get("primary_blocker") != "REGIME",
            "factor_ok": s.get("primary_blocker") != "FACTOR",
            "eligible": s.get("eligibility_status") == "ELIGIBLE",
            "eligibility_status": s.get("eligibility_status", "BLOCKED").lower(),
            "reason": s.get("blocking_reason"),
            "activation_hint": s.get("activation_hint", ""),
            "evolution_status": "EVOLUTION_ONLY"
        }
        
        families[family]["strategies"].append(ui_strategy)
        families[family]["total_count"] += 1
        if ui_strategy["eligible"]:
            families[family]["eligible_count"] += 1
            
    # Calculate durations for each family
    durations = _calculate_family_durations(families, market)
    print(f"DEBUG: Calculated durations for {market}: {durations}")
    for fid, duration_str in durations.items():
        families[fid]["duration"] = duration_str
    
    return {
        "strategies": [s for fam in families.values() for s in fam["strategies"]],
        "families": families,
        "current_regime": resolution.get("current_regime", "UNDEFINED"),
        "current_factors": resolution.get("current_factors", {}),
        "evolution_version": resolution.get("evolution_version", "v1"),
        "evolution_frozen_date": resolution.get("evolution_frozen_date", ""),
        "resolved_at": resolution.get("resolved_at", ""),
        "source": "daily_snapshot"
    }
