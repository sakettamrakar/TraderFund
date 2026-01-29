from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import os
import datetime
from typing import Dict, Any, List, Optional

# --- Configuration & Paths ---
BASE_DIR = Path(__file__).parent.parent.parent.parent # c:\GIT\TraderFund
DOCS_DIR = BASE_DIR / "docs"
EV_DIR = DOCS_DIR / "evolution"
TICKS_DIR = EV_DIR / "ticks"
LEDGER_DIR = DOCS_DIR / "epistemic" / "ledger"
META_DIR = EV_DIR / "meta_analysis"

# India Research Paths
INDIA_RESEARCH_DIR = DOCS_DIR / "research" / "india"
INDIA_CTX_DIR = INDIA_RESEARCH_DIR / "context"

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
        return []
    # Sort by timestamp (descending)
    # Assumes folder format: tick_{timestamp}
    return sorted([d for d in TICKS_DIR.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True)[:limit]

def _get_latest_tick_dir() -> Optional[Path]:
    dirs = _get_sorted_tick_dirs(limit=1)
    return dirs[0] if dirs else None

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

def _calculate_state_durations(target_states: Dict[str, str], latest_ts: datetime.datetime) -> Dict[str, Any]:
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
        # Skip the very first one (it's the current one)? 
        # Actually loop includes current, so it verifies self consistency.
        
        tick_ts = _parse_timestamp(d.name)
        
        # Determine states for this tick
        mom = _read_json_safe(d / "momentum_emergence.json").get("momentum_emergence", {}).get("state", "UNKNOWN")
        exp = _read_json_safe(d / "expansion_transition.json").get("expansion_transition", {}).get("state", "UNKNOWN")
        dis = _read_json_safe(d / "dispersion_breakout.json").get("dispersion_breakout", {}).get("state", "UNKNOWN")
        liq = _read_json_safe(d / "liquidity_compression.json").get("liquidity_compression", {}).get("state", "UNKNOWN")
        
        current_tick_states = {
            "Momentum": mom,
            "Expansion": exp,
            "Dispersion": dis,
            "Liquidity": liq
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
async def get_system_status(market: str = "US"):
    """
    Returns high-level system state based on last tick and ledger.
    """
    if market.upper() in ["IN", "INDIA"]:
        # India System Status (Based on static context)
        regime_data = _read_json_safe(INDIA_CTX_DIR / "regime_context.json")
        regime = regime_data.get("regime_context", {}).get("regime", "UNKNOWN")

        status = "OBSERVING" if regime != "UNKNOWN" else "OFFLINE"
        reason = f"India Market Regime: {regime}"

        # Check timestamp
        ts = regime_data.get("regime_context", {}).get("evaluation_window", {}).get("start_date", "N/A")

        return {
            "status": status,
            "reason": reason,
            "last_ev_tick": ts,
            "governance_status": "CLEAN (India Adapter)"
        }

    latest_tick = _get_latest_tick_dir()
    
    last_tick_ts = "N/A"
    status = "IDLE"
    reason = "No data detected"
    
    if latest_tick:
        dt = _parse_timestamp(latest_tick.name)
        last_tick_ts = dt.isoformat()

        # Check latest artifacts for system state
        exp_data = _read_json_safe(latest_tick / "expansion_transition.json")
        dis_data = _read_json_safe(latest_tick / "dispersion_breakout.json")
        
        # Logic for Status
        exp_state = exp_data.get("expansion_transition", {}).get("state", "NONE")
        dis_state = dis_data.get("dispersion_breakout", {}).get("state", "NONE")
        
        if exp_state != "NONE" or dis_state != "NONE":
            status = "OBSERVING" # Something is moving
            reason = f"Expansion: {exp_state}, Dispersion: {dis_state}"
        else:
            status = "IDLE"
            reason = "No expansion or dispersion detected (Stagnation)"

    return {
        "status": status,
        "reason": reason,
        "last_ev_tick": last_tick_ts,
        "governance_status": "CLEAN" 
    }

@app.get("/api/layers/health")
async def get_layer_health():
    """
    Checks if critical artifacts exist and are fresh.
    """
    latest_tick = _get_latest_tick_dir()
    if not latest_tick:
         return {"error": "No ticks found"}
         
    def check_file(path: Path):
        exists = path.exists()
        return {
            "status": "OK" if exists else "ERROR",
            "last_updated": datetime.datetime.fromtimestamp(path.stat().st_mtime).isoformat() if exists else None
        }

    return {
        "Regime Context": check_file(latest_tick / "regime_context.json"),
        "Factor Context": check_file(latest_tick / "factor_context.json"),
        "Momentum Watcher": check_file(latest_tick / "momentum_emergence.json"),
        "Expansion Watcher": check_file(latest_tick / "expansion_transition.json"),
        "Dispersion Watcher": check_file(latest_tick / "dispersion_breakout.json"),
        "Liquidity Watcher": check_file(latest_tick / "liquidity_compression.json"),
        "Meta-Analysis": check_file(META_DIR / "evolution_comparative_summary.md")
    }

@app.get("/api/market/snapshot")
async def get_market_snapshot(market: str = "US"):
    """
    Aggregates diagnostic states from the latest tick with DURATION tracking.
    """
    if market.upper() in ["IN", "INDIA"]:
        # India Snapshot (Static)
        regime = _read_json_safe(INDIA_CTX_DIR / "regime_context.json")
        factor = _read_json_safe(INDIA_CTX_DIR / "factor_context.json")

        # Extract states from Factor Context
        factors = factor.get("factor_context", {}).get("factors", {})
        mom_state = factors.get("momentum", {}).get("level", {}).get("state", "UNKNOWN").upper()

        # Derive others or use defaults if not in factor context
        # In India Instantiation, we are reusing Factor Context structure.

        current_states = {
            "Regime": regime.get("regime_context", {}).get("regime", "UNKNOWN"),
            "Liquidity": factors.get("liquidity", {}).get("state", "NEUTRAL"), # Default or from factor
            "Momentum": mom_state,
            "Dispersion": "UNKNOWN", # Not yet in India Factor Context explicitly as top level
            "Expansion": "UNKNOWN"
        }

        return {
            "Regime": current_states["Regime"],
            "Liquidity": current_states["Liquidity"],
            "Momentum": current_states["Momentum"],
            "Dispersion": current_states["Dispersion"],
            "Expansion": current_states["Expansion"],
            "Durations": {}, # Not tracked for India yet
            "Alerts": [],
            "Details": {
                "Momentum": factors.get("momentum", {}).get("meta", {}).get("notes", "India Research"),
                "Liquidity": "Estimated"
            }
        }

    latest_tick = _get_latest_tick_dir()
    if not latest_tick:
        return {}
    
    latest_ts = _parse_timestamp(latest_tick.name)
    
    regime = _read_json_safe(latest_tick / "regime_context.json")
    liq = _read_json_safe(latest_tick / "liquidity_compression.json")
    mom = _read_json_safe(latest_tick / "momentum_emergence.json")
    dis = _read_json_safe(latest_tick / "dispersion_breakout.json")
    exp = _read_json_safe(latest_tick / "expansion_transition.json")
    
    # Extract current states
    current_states = {
        "Regime": regime.get("regime_context", {}).get("regime", "UNKNOWN"),
        "Liquidity": liq.get("liquidity_compression", {}).get("state", "UNKNOWN"),
        "Momentum": mom.get("momentum_emergence", {}).get("state", "UNKNOWN"),
        "Dispersion": dis.get("dispersion_breakout", {}).get("state", "UNKNOWN"),
        "Expansion": exp.get("expansion_transition", {}).get("state", "UNKNOWN")
    }
    
    # Calculate Durations
    # Note: We omit 'Regime' from strict duration tracking for now if it's external, but we'll include it.
    durations = _calculate_state_durations(current_states, latest_ts)
    
    # Determine Derivative Alerts (Change Detection)
    # Compare with previous tick (index 1 in history)
    alerts = []
    history = _get_sorted_tick_dirs(limit=2)
    if len(history) >= 2:
        prev_tick = history[1]
        p_mom = _read_json_safe(prev_tick / "momentum_emergence.json").get("momentum_emergence", {}).get("state", "UNKNOWN")
        p_exp = _read_json_safe(prev_tick / "expansion_transition.json").get("expansion_transition", {}).get("state", "UNKNOWN")
        
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
        "Durations": durations,
        "Alerts": alerts,
        "Details": {
             "Momentum": mom.get("momentum_emergence", {}).get("notes", ""),
             "Liquidity": liq.get("liquidity_compression", {}).get("notes", "")
        }
    }

@app.get("/api/watchers/timeline")
async def get_watcher_timeline(limit: int = 20):
    """
    Returns state history for charts.
    """
    dirs = _get_sorted_tick_dirs(limit=limit)
    timeline = []
    
    for d in dirs:
        dt = _parse_timestamp(d.name).isoformat()
              
        mom = _read_json_safe(d / "momentum_emergence.json")
        exp = _read_json_safe(d / "expansion_transition.json")
        dis = _read_json_safe(d / "dispersion_breakout.json")
        liq = _read_json_safe(d / "liquidity_compression.json")
        
        timeline.append({
            "timestamp": dt,
            "momentum": mom.get("momentum_emergence", {}).get("state", "NONE"),
            "expansion": exp.get("expansion_transition", {}).get("state", "NONE"),
            "dispersion": dis.get("dispersion_breakout", {}).get("state", "NONE"),
            "liquidity": liq.get("liquidity_compression", {}).get("state", "NEUTRAL")
        })
        
    return timeline

@app.get("/api/strategies/eligibility")
async def get_strategy_eligibility(market: str = "US"):
    """
    Returns daily strategy eligibility from persisted snapshot.
    Uses frozen Strategy Evolution v1 - no live recomputation.
    """
    import os
    from datetime import datetime
    
    resolution = None
    
    if market.upper() in ["IN", "INDIA"]:
        # Read from India static file
        res_path = INDIA_RESEARCH_DIR / "strategy_eligibility.json"
        if res_path.exists():
            resolution = _read_json_safe(res_path)
    else:
        # US Logic
        # First, try to read from daily resolution snapshot (preferred)
        daily_dir = PROJECT_ROOT / "docs" / "evolution" / "daily_strategy_resolution"

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
    
@app.get("/api/capital/readiness")
async def get_capital_readiness():
    """
    Returns the latest capital readiness assessment.
    """
    latest_tick = _get_latest_tick_dir()
    if not latest_tick:
        return {"status": "UNKNOWN", "error": "No tick data found"}
        
    readiness_path = latest_tick / "capital_readiness.json"
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
async def get_capital_history():
    """
    Returns the persistent capital history timeline.
    """
    timeline_path = PROJECT_ROOT / "docs" / "capital" / "history" / "capital_state_timeline.json"
    if not timeline_path.exists():
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

@app.get("/api/meta/summary")
async def get_meta_summary():
    """
    Returns the markdown content of the comparative summary.
    """
    content = _read_markdown_safe(META_DIR / "evolution_comparative_summary.md")
    return {"content": content}

@app.get("/api/macro/context")
async def get_macro_context(market: str = "US"):
    """
    Returns the latest Macro Context.
    """
    if market.upper() in ["IN", "INDIA"]:
        return _read_json_safe(INDIA_CTX_DIR / "macro_context.json")
    else:
        # US Macro Context
        MACRO_DIR = DOCS_DIR / "macro" / "context"
        return _read_json_safe(MACRO_DIR / "macro_context.json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
