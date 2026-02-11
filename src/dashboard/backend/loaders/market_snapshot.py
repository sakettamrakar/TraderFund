from dashboard.backend.utils.filesystem import get_latest_tick_dir, read_json_safe, get_ticks_history
from typing import Dict, Any, List
import datetime
from pathlib import Path

def _parse_timestamp(tick_name: str) -> datetime.datetime:
    ts_str = tick_name.replace("tick_", "")
    try:
        return datetime.datetime.fromtimestamp(int(ts_str))
    except:
        return datetime.datetime.now()


def _derive_regime_display(regime_ctx: Dict[str, Any]) -> Dict[str, Any]:
    canonical_state = regime_ctx.get("canonical_state", "UNKNOWN")
    missing_roles = regime_ctx.get("canonical_missing_roles", [])
    stale_roles = regime_ctx.get("canonical_stale_roles", [])
    regime_reason = regime_ctx.get("regime_reason", "")

    degraded = canonical_state != "CANONICAL_COMPLETE"
    regime_value = (
        "UNKNOWN (PARTIAL DATA)"
        if degraded
        else regime_ctx.get("regime", regime_ctx.get("regime_code", "UNKNOWN"))
    )

    return {
        "regime_value": regime_value,
        "canonical_state": canonical_state,
        "degraded": degraded,
        "missing_roles": missing_roles,
        "stale_roles": stale_roles,
        "regime_reason": regime_reason or ("Partial canonical inputs" if degraded else "Canonical-complete regime evaluation."),
    }

def _calculate_state_durations(current_states: Dict[str, str], latest_ts: datetime.datetime, market: str) -> Dict[str, Any]:
    """
    Scans history to see how long each factor has been in its current state.
    """
    history_dirs = get_ticks_history(limit=50) # Look back up to 50 ticks
    durations = {}
    
    for factor, current_state in current_states.items():
        count = 0
        first_tick_ts = latest_ts
        
        # Mapping from UI Factor Name to JSON filename
        FILE_MAP = {
            "Regime": "regime_context.json",
            "Liquidity": "liquidity_compression.json",
            "Momentum": "momentum_emergence.json",
            "Dispersion": "dispersion_breakout.json",
            "Expansion": "expansion_transition.json"
        }
        
        JSON_KEY_MAP = {
            "Regime": "regime_context",
            "Liquidity": "liquidity_compression",
            "Momentum": "momentum_emergence",
            "Dispersion": "dispersion_breakout",
            "Expansion": "expansion_transition"
        }
        
        STATE_KEY_MAP = {
            "Regime": "regime",
            "Liquidity": "state",
            "Momentum": "state",
            "Dispersion": "state",
            "Expansion": "state"
        }
        
        filename = FILE_MAP.get(factor)
        json_key = JSON_KEY_MAP.get(factor)
        state_key = STATE_KEY_MAP.get(factor)
        
        if not filename: continue
        
        for d in history_dirs:
            # FIX: Ensure we read from market specific path in history too
            market_d = d / market
            data = read_json_safe(market_d / filename).get(json_key, {})
            if factor == "Regime":
                state = _derive_regime_display(data).get("regime_value", "UNKNOWN")
            else:
                state = data.get(state_key, "UNKNOWN")
            
            if state == current_state:
                count += 1
                first_tick_ts = _parse_timestamp(d.name)
            else:
                break
        
        durations[factor.upper()] = {
            "ticks": count,
            "duration": f"{count} ticks",
            "since": first_tick_ts.isoformat()
        }
        
    return durations

def load_market_snapshot(market: str = "US") -> Dict[str, Any]:
    latest_tick = get_latest_tick_dir()
    if not latest_tick:
        return {}
        
    latest_ts = _parse_timestamp(latest_tick.name)
    market_dir = latest_tick / market
    
    regime = read_json_safe(market_dir / "regime_context.json").get("regime_context", {})
    liq = read_json_safe(market_dir / "liquidity_compression.json").get("liquidity_compression", {})
    mom = read_json_safe(market_dir / "momentum_emergence.json").get("momentum_emergence", {})
    dis = read_json_safe(market_dir / "dispersion_breakout.json").get("dispersion_breakout", {})
    exp = read_json_safe(market_dir / "expansion_transition.json").get("expansion_transition", {})
    regime_meta = _derive_regime_display(regime)

    current_states = {
        "Regime": regime_meta["regime_value"],
        "Liquidity": liq.get("state", "UNKNOWN"),
        "Momentum": mom.get("state", "UNKNOWN"),
        "Dispersion": dis.get("state", "UNKNOWN"),
        "Expansion": exp.get("state", "UNKNOWN")
    }
    
    durations = _calculate_state_durations(current_states, latest_ts, market)
    
    # Derivative Alerts
    alerts = []
    history = get_ticks_history(limit=2)
    if len(history) >= 2:
        prev_tick = history[1]
        prev_market_dir = prev_tick / market
        
        p_mom = read_json_safe(prev_market_dir / "momentum_emergence.json").get("momentum_emergence", {}).get("state", "UNKNOWN")
        p_exp = read_json_safe(prev_market_dir / "expansion_transition.json").get("expansion_transition", {}).get("state", "UNKNOWN")
        
        if current_states["Momentum"] != p_mom:
            alerts.append(f"Momentum Changed: {p_mom} -> {current_states['Momentum']}")
        if current_states["Expansion"] != p_exp:
            alerts.append(f"Expansion Changed: {p_exp} -> {current_states['Expansion']}")
            
    return {
        "Regime": current_states["Regime"], # Case match Frontend expectation
        "Liquidity": current_states["Liquidity"],
        "Momentum": current_states["Momentum"],
        "Expansion": current_states["Expansion"],
        "Dispersion": current_states["Dispersion"],
        "CanonicalState": regime_meta["canonical_state"],
        "RegimeDegraded": regime_meta["degraded"],
        "MissingRoles": regime_meta["missing_roles"],
        "StaleRoles": regime_meta["stale_roles"],
        "RegimeReason": regime_meta["regime_reason"],
        "Durations": durations,
        "Alerts": alerts,
        "Details": {
             "Momentum": mom.get("notes", ""), # Fix key access? mom has notes?
             "Liquidity": liq.get("notes", "")
        }
    }
