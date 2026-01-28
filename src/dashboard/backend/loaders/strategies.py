from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import os
from datetime import datetime

# PROJECT_ROOT setup
# This loader is in src/dashboard/backend/loaders/strategies.py
# Root is 4 levels up
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

def _read_json_safe(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _get_latest_tick_dir() -> Optional[Path]:
    ticks_dir = PROJECT_ROOT / "docs" / "evolution" / "ticks"
    if not ticks_dir.exists():
        return None
    
    ticks = [d for d in ticks_dir.iterdir() if d.is_dir() and d.name.startswith("tick_")]
    if not ticks:
        return None
        
    return sorted(ticks, key=lambda x: x.name, reverse=True)[0]

def load_strategy_eligibility() -> Dict[str, Any]:
    """
    Returns daily strategy eligibility from persisted snapshot.
    Uses frozen Strategy Evolution v1 - no live recomputation.
    """
    # First, try to read from daily resolution snapshot (preferred)
    daily_dir = PROJECT_ROOT / "docs" / "evolution" / "daily_strategy_resolution"
    
    resolution = None
    if daily_dir.exists():
        # Find the latest snapshot
        snapshots = sorted([f for f in daily_dir.iterdir() if f.suffix == ".json"], reverse=True)
        if snapshots:
            resolution = _read_json_safe(snapshots[0])
    
    # Fallback: try to read from latest tick directory
    if not resolution:
        latest_tick = _get_latest_tick_dir()
        if latest_tick:
            resolution = _read_json_safe(latest_tick / "strategy_resolution.json")
    
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
