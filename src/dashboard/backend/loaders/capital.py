import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent # c:\GIT\TraderFund

def _read_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _get_latest_tick_dir() -> Optional[Path]:
    ticks_dir = PROJECT_ROOT / "docs" / "evolution" / "ticks"
    if not ticks_dir.exists():
        return None
    dirs = sorted([d for d in ticks_dir.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True)
    return dirs[0] if dirs else None

def load_capital_readiness(market: str = "US") -> Dict[str, Any]:
    latest_tick = _get_latest_tick_dir()
    if not latest_tick:
        return {"status": "UNKNOWN", "error": "No tick data found"}
        
    readiness_path = latest_tick / market / "capital_readiness.json"
    if not readiness_path.exists():
        return {"status": "UNKNOWN", "error": "Readiness snapshot not found"}
        
    return _read_json_safe(readiness_path)

def load_capital_history(market: str = "US") -> Dict[str, Any]:
    # Try reading from tick-specific history/narrative if available
    # Or assume global persistence is legacy.
    # ev_tick writes to history, but we need to verify where.
    # For now, let's assume strict isolation:
    # If ev_tick.py writes to tick_{ts}/{market}/capital_readiness.json, that's snapshot.
    # But it also calls _record_capital_history_step.
    # For now, we return empty if not found, or standard global if we haven't partitioned history yet.
    # Strict 9.5: Check tick folder first? No, history is time-series.
    # Let's default to empty for now to prove scope safety until we migrate history files.
    
    timeline_path = PROJECT_ROOT / "docs" / "capital" / "history" / f"capital_state_timeline_{market}.json"
    # If not existing, try global? No. Strict.
    if not timeline_path.exists():
        # Only fallback to global if market is US?
        if market == "US":
             timeline_path = PROJECT_ROOT / "docs" / "capital" / "history" / "capital_state_timeline.json"
        else:
             return {"timeline": [], "current_posture": f"NO_HISTORY ({market})"}

    if not timeline_path.exists():
        return {"timeline": [], "current_posture": "NO_HISTORY"}
        
    timeline = _read_json_safe(timeline_path)
    
    current_posture = "IDLE"
    if timeline and len(timeline) > 0:
        current_posture = timeline[0].get("state", "IDLE")
        
    return {
        "timeline": timeline[:50], 
        "current_posture": current_posture
    }
