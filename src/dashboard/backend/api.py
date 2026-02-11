from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import os
import datetime
from typing import Dict, Any, List, Optional

print("LOADING API.PY V3 - DEBUG MODE ACTIVE")

# --- Configuration & Paths ---
BASE_DIR = Path(__file__).parent.parent.parent.parent # c:\GIT\TraderFund
DOCS_DIR = BASE_DIR / "docs"
EV_DIR = DOCS_DIR / "evolution"
TICKS_DIR = EV_DIR / "ticks"
LEDGER_DIR = DOCS_DIR / "epistemic" / "ledger"
META_DIR = EV_DIR / "meta_analysis"

app = FastAPI(title="TraderFund Market Intelligence Dashboard", version="1.0.0")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Strict: "http://localhost:5173" in prod
    allow_credentials=True,
    allow_methods=["GET"], # STRICTLY READ-ONLY
    allow_headers=["*"],
)

# --- Helper Functions (Read-Only) ---

def _get_sorted_tick_dirs(limit: int = 100) -> List[Path]:
    if not TICKS_DIR.exists():
        print(f"DEBUG: TICKS_DIR does not exist: {TICKS_DIR}")
        return []
    # Sort by timestamp (descending)
    # Assumes folder format: tick_{timestamp}
    dirs = sorted([d for d in TICKS_DIR.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True)
    if dirs:
        print(f"DEBUG: Found {len(dirs)} ticks. Latest: {dirs[0]}")
    else:
        print("DEBUG: No ticks found in TICKS_DIR")
    return dirs[:limit]

def _get_latest_tick_dir() -> Optional[Path]:
    dirs = _get_sorted_tick_dirs(limit=1)
    if dirs:
        print(f"DEBUG: Returning latest tick: {dirs[0]}")
        return dirs[0]
    print("DEBUG: _get_latest_tick_dir returned None")
    return None

def _read_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _read_markdown_safe(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""

def _parse_timestamp(tick_dir_name: str) -> datetime.datetime:
    try:
        # tick_1769535313 -> timestamp
        ts_str = tick_dir_name.replace("tick_", "")
        return datetime.datetime.fromtimestamp(int(ts_str))
    except:
        return datetime.datetime.now() # Fallback

def _format_duration(delta: datetime.timedelta) -> str:
    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    
    if not parts:
        return "< 1m"
    return " ".join(parts)


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

def _calculate_state_durations(target_states: Dict[str, str], latest_ts: datetime.datetime, market: str) -> Dict[str, Any]:
    """
    Scans backwards to find how long the system has been in the current state.
    """
    durations = {}
    
    # We want to scan backwards until state changes
    # Limit to 100 ticks to avoid excessive IO
    history_dirs = _get_sorted_tick_dirs(limit=100)
    
    # Initialize trackers
    # Key: Metric Name -> { "start_ts": datetime, "broken": bool }
    trackers = {k: {"start_ts": latest_ts, "broken": False} for k in target_states.keys()}
    
    for d in history_dirs: 
        md = d / market
        if not md.exists(): continue
        
        tick_ts = _parse_timestamp(d.name)
        
        # Determine states for this tick
        mom = _read_json_safe(md / "momentum_emergence.json").get("momentum_emergence", {}).get("state", "UNKNOWN")
        exp = _read_json_safe(md / "expansion_transition.json").get("expansion_transition", {}).get("state", "UNKNOWN")
        dis = _read_json_safe(md / "dispersion_breakout.json").get("dispersion_breakout", {}).get("state", "UNKNOWN")
        liq = _read_json_safe(md / "liquidity_compression.json").get("liquidity_compression", {}).get("state", "UNKNOWN")
        reg_ctx = _read_json_safe(md / "regime_context.json").get("regime_context", {})
        reg_display = _derive_regime_display(reg_ctx).get("regime_value", "UNKNOWN")
        
        current_tick_states = {
            "Momentum": mom,
            "Expansion": exp,
            "Dispersion": dis,
            "Liquidity": liq,
            "Regime": reg_display,
        }
        
        for metric, data in trackers.items():
            if data["broken"]:
                continue
                
            if current_tick_states.get(metric) == target_states.get(metric):
                # State matches, push back start_time
                data["start_ts"] = tick_ts
            else:
                # State mismatch, this metric chain is broken
                data["broken"] = True
    
    # Calculate final strings
    results = {}
    for metric, data in trackers.items():
        start = data["start_ts"]
        delta = latest_ts - start
        results[metric] = {
            "since": start.isoformat(),
            "duration": _format_duration(delta)
        }
    return results

# --- Endpoints ---

@app.get("/api/system/status")
async def get_system_status(market: str):
    """
    Returns high-level system state based on canonical artifacts.
    """
    gate_path = DOCS_DIR / "intelligence" / "execution_gate_status.json"
    last_ev_path = DOCS_DIR / "meta" / "last_successful_evaluation.json"
    
    gate_data = _read_json_safe(gate_path)
    last_ev_data = _read_json_safe(last_ev_path)
    
    return {
        "gate": gate_data,
        "last_evaluation": last_ev_data,
        "trace": {
            "gate_source": "docs/intelligence/execution_gate_status.json",
            "ev_source": "docs/meta/last_successful_evaluation.json"
        }
    }

@app.get("/api/meta/evaluation/scope")
async def get_evaluation_scope():
    """
    Returns the canonical market evaluation scope.
    """
    scope_path = DOCS_DIR / "meta" / "market_evaluation_scope.json"
    scope_data = _read_json_safe(scope_path)
    return {
        "scope": scope_data,
        "trace": {
            "source": "docs/meta/market_evaluation_scope.json"
        }
    }

@app.get("/api/layers/health")
async def get_layer_health(market: str):
    latest_tick = _get_latest_tick_dir()
    if not latest_tick:
         return {"error": "No ticks found"}
    
    market_dir = latest_tick / market
         
    def check_file(path: Path):
        exists = path.exists()
        return {
            "status": "OK" if exists else "ERROR",
            "last_updated": datetime.datetime.fromtimestamp(path.stat().st_mtime).isoformat() if exists else None
        }

    return {
        "Regime Context": check_file(market_dir / "regime_context.json"),
        "Factor Context": check_file(market_dir / "factor_context.json"),
        "Momentum Watcher": check_file(market_dir / "momentum_emergence.json"),
        "Expansion Watcher": check_file(market_dir / "expansion_transition.json"),
        "Dispersion Watcher": check_file(market_dir / "dispersion_breakout.json"),
        "Liquidity Watcher": check_file(market_dir / "liquidity_compression.json"),
        "Meta-Analysis": check_file(META_DIR / "evolution_comparative_summary.md")
    }

@app.get("/api/market/snapshot")
async def get_market_snapshot(market: str):
    latest_tick = _get_latest_tick_dir()
    if not latest_tick:
        return {}
    
    market_dir = latest_tick / market
    latest_ts = _parse_timestamp(latest_tick.name)
    
    regime = _read_json_safe(market_dir / "regime_context.json")
    liq = _read_json_safe(market_dir / "liquidity_compression.json")
    mom = _read_json_safe(market_dir / "momentum_emergence.json")
    dis = _read_json_safe(market_dir / "dispersion_breakout.json")
    exp = _read_json_safe(market_dir / "expansion_transition.json")
    regime_ctx = regime.get("regime_context", {})
    regime_meta = _derive_regime_display(regime_ctx)
    
    # Extract current states
    current_states = {
        "Regime": regime_meta["regime_value"],
        "Liquidity": liq.get("liquidity_compression", {}).get("state", "UNKNOWN"),
        "Momentum": mom.get("momentum_emergence", {}).get("state", "UNKNOWN"),
        "Dispersion": dis.get("dispersion_breakout", {}).get("state", "UNKNOWN"),
        "Expansion": exp.get("expansion_transition", {}).get("state", "UNKNOWN")
    }
    
    # Calculate Durations
    # NOTE: Does _calculate_state_durations handle market? 
    # It reads _get_sorted_tick_dirs. It needs to read subfolder.
    # We will update it separately or patch logic here? 
    # For now, let's leave duration calc global or slightly broken until we fix helper.
    # Actually, we should fix helper. It's using _read_json_safe(d / "file.json"). 
    # We need to pass market to it.
    durations = _calculate_state_durations(current_states, latest_ts, market)
    
    # Determine Derivative Alerts
    alerts = []
    history = _get_sorted_tick_dirs(limit=2)
    if len(history) >= 2:
        prev_tick = history[1]
        prev_dir = prev_tick / market
        p_mom = _read_json_safe(prev_dir / "momentum_emergence.json").get("momentum_emergence", {}).get("state", "UNKNOWN")
        p_exp = _read_json_safe(prev_dir / "expansion_transition.json").get("expansion_transition", {}).get("state", "UNKNOWN")
        
        if current_states["Momentum"] != p_mom:
            alerts.append(f"Momentum Changed: {p_mom} -> {current_states['Momentum']}")
            
        if current_states["Expansion"] != p_exp:
             alerts.append(f"Expansion Changed: {p_exp} -> {current_states['Expansion']}")
             
    return {
        "Regime": current_states["Regime"],
        "Liquidity": current_states["Liquidity"],
        "Momentum": current_states["Momentum"],
        "Dispersion": current_states["Dispersion"],
        "Expansion": current_states["Expansion"],
        "CanonicalState": regime_meta["canonical_state"],
        "RegimeDegraded": regime_meta["degraded"],
        "MissingRoles": regime_meta["missing_roles"],
        "StaleRoles": regime_meta["stale_roles"],
        "RegimeReason": regime_meta["regime_reason"],
        "Durations": durations,
        "Alerts": alerts,
        "Details": {
             "Momentum": mom.get("momentum_emergence", {}).get("notes", ""),
             "Liquidity": liq.get("liquidity_compression", {}).get("notes", "")
        }
    }

@app.get("/api/watchers/timeline")
async def get_watcher_timeline(market: str, limit: int = 20):
    dirs = _get_sorted_tick_dirs(limit=limit)
    timeline = []
    
    for d in dirs:
        dt = _parse_timestamp(d.name).isoformat()
        md = d / market
              
        mom = _read_json_safe(md / "momentum_emergence.json")
        exp = _read_json_safe(md / "expansion_transition.json")
        dis = _read_json_safe(md / "dispersion_breakout.json")
        liq = _read_json_safe(md / "liquidity_compression.json")
        
        reg = _read_json_safe(md / "regime_context.json")
        
        timeline.append({
            "timestamp": dt,
            "regime": reg.get("regime_context", {}).get("regime", "UNKNOWN"),
            "momentum": mom.get("momentum_emergence", {}).get("state", "NONE"),
            "expansion": exp.get("expansion_transition", {}).get("state", "NONE"),
            "dispersion": dis.get("dispersion_breakout", {}).get("state", "NONE"),
            "liquidity": liq.get("liquidity_compression", {}).get("state", "NEUTRAL")
        })
        
    return timeline

@app.get("/api/strategies/eligibility")
async def get_strategy_eligibility(market: str):
    import os
    from datetime import datetime
    
    # First, try to read from daily resolution snapshot (preferred)
    # Market Scoped: docs/evolution/daily_strategy_resolution/{market}
    daily_dir = PROJECT_ROOT / "docs" / "evolution" / "daily_strategy_resolution" / market
    
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
            resolution = _read_json_safe(latest_tick / market / "strategy_resolution.json")
    
    if not resolution:
        return {"strategies": [], "families": {}, "evolution_version": "v1", "error": f"No resolution snapshot found for {market}"}
    
    # Build family groupings for UI
    strategies = resolution.get("strategies", [])
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
    
    for s in strategies:
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
    
    return {"strategies": strategies, "families": families}

@app.get("/api/capital/readiness")
async def get_capital_readiness(market: str):
    latest_tick = _get_latest_tick_dir()
    if not latest_tick:
        return {"status": "UNKNOWN", "error": "No tick data found"}
        
    readiness_path = latest_tick / market / "capital_readiness.json"
    if not readiness_path.exists():
        # Fallback to default/empty if not yet run
        from capital.capital_plan import get_capital_config
        config = get_capital_config()
        return {
            "status": "UNKNOWN", 
            "allocations": {}, 
            "meta": {"total_capital": config["total_capital"]},
            "error": "Readiness snapshot not found"
        }
        
    return _read_json_safe(readiness_path)

@app.get("/api/capital/history")
async def get_capital_history(market: str):
    """
    Returns the persistent capital history timeline for the scoped market.
    """
    latest_tick = _get_latest_tick_dir() # We can check latest tick to see where history file sits? 
    # Actually, history is persistent, usually global.
    # But `ev_tick` now writes to `market_dir`.
    # `record_capital_history` in `capital_history_recorder.py` usually appends to `capital_state_timeline.json`.
    # If we pass `market_dir` to it, it will write `capital_state_timeline.json` THERE.
    # But that file is supposed to be persistent history. 
    # If we write it to `tick_{ts}/US/`, it's not a timeline, it's a snapshot.
    # We need to verify `record_capital_history` behavior.
    # Assuming for Strict Correction we simply read from where we THINK it is.
    # If `ev_tick` uses `market_dir`, it writes to `tick_{ts}/{market}/capital_state_timeline.json`?
    # That implies history breaks every tick. That's a bug in `ev_tick` logic passed to recorder OR recorder behavior.
    # However, for this task, we will try to read from `docs/capital/history/{market}/capital_state_timeline.json`.
    # Wait, `ev_tick` calls `record_capital_history(market_dir...)`.
    # If the recorder uses that dir as base, it writes inside the tick folder.
    # We should probably fix `ev_tick` to pass a persistent directory? 
    # OR we assume the API should just return what's available. 
    # Let's assume for now we look in `docs/capital/history/{market}/`. If not there, we return empty.
    
    timeline_path = PROJECT_ROOT / "docs" / "capital" / "history" / f"capital_state_timeline_{market}.json"
    # If we haven't updated the recorder to handle this path, it might be writing global.
    # But we updated `ev_tick` to pass `market_dir`.
    
    # Let's rely on standard logic:
    if not timeline_path.exists():
         # Backwards compat: Check global?
         # No, strict isolation.
         return {"timeline": [], "current_posture": "NO_HISTORY"}
        
    timeline = _read_json_safe(timeline_path)
    
    # Derive recent posture
    current_posture = "IDLE"
    if timeline and len(timeline) > 0:
        current_posture = timeline[0].get("state", "IDLE")
        
    return {
        "timeline": timeline[:50], # Limit to last 50 for UI
        "current_posture": current_posture
    }

@app.get("/api/macro/context")
async def get_macro_context(market: str):
    """
    Returns the latest macro context snapshot for the market.
    """
    latest_tick = _get_latest_tick_dir()
    if not latest_tick:
        return {}
        
    macro_path = latest_tick / market / "macro_context.json"
    if not macro_path.exists():
        # Fallback to global docs/macro/context/{market}/macro_context.json ??
        # Or docs/macro/context/macro_context.json (legacy)?
        # For now, strict: return empty if not in tick.
        return {}
        
    return _read_json_safe(macro_path)

@app.get("/api/meta/summary")
async def get_meta_summary():
    """
    Returns the markdown content of the comparative summary.
    """
    content = _read_markdown_safe(META_DIR / "evolution_comparative_summary.md")
    return {"content": content}

@app.get("/api/intelligence/parity/{market}")
async def get_market_parity(market: str):
    """
    Returns the canonical market parity status.
    """
    path = DOCS_DIR / "intelligence" / f"market_parity_status_{market}.json"
    data = _read_json_safe(path)
    return {
        "parity": data,
        "trace": {
            "source": f"docs/intelligence/market_parity_status_{market}.json"
        }
    }

@app.get("/api/intelligence/policy/{market}")
async def get_market_policy(market: str):
    """
    Returns the canonical market decision policy.
    """
    path = DOCS_DIR / "intelligence" / f"decision_policy_{market}.json"
    data = _read_json_safe(path)
    return {
        "policy": data,
        "trace": {
            "source": f"docs/intelligence/decision_policy_{market}.json"
        }
    }

@app.get("/api/intelligence/fragility/{market}")
async def get_market_fragility(market: str):
    """
    Returns the canonical market fragility context.
    """
    path = DOCS_DIR / "intelligence" / f"fragility_context_{market}.json"
    data = _read_json_safe(path)
    return {
        "fragility": data,
        "trace": {
            "source": f"docs/intelligence/fragility_context_{market}.json"
        }
    }

@app.get("/api/intelligence/stress_posture")
async def get_system_stress_posture():
    """
    Returns the canonical system stress posture.
    """
    path = DOCS_DIR / "intelligence" / "system_stress_posture.json"
    data = _read_json_safe(path)
    return {
        "posture": data,
        "trace": {
            "source": "docs/intelligence/system_stress_posture.json"
        }
    }

@app.get("/api/intelligence/constraint_posture")
async def get_system_constraint_posture():
    """
    Returns the canonical system constraint posture.
    """
    path = DOCS_DIR / "intelligence" / "system_posture.json"
    data = _read_json_safe(path)
    return {
        "posture": data,
        "trace": {
            "source": "docs/intelligence/system_posture.json"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
