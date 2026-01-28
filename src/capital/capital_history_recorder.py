import json
from pathlib import Path
from typing import Dict, Any, List
import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent

def record_capital_history(
    tick_dir: Path,
    readiness: Dict[str, Any],
    resolution: Dict[str, Any],
    regime: str
):
    """
    Appends the current capital state to the persistent timeline.
    """
    timeline_path = PROJECT_ROOT / "docs" / "capital" / "history" / "capital_state_timeline.json"
    
    # Load existing timeline or create new
    if timeline_path.exists():
        try:
            with open(timeline_path, 'r') as f:
                timeline = json.load(f)
        except:
            timeline = []
    else:
        timeline = []
        
    # Determine Primary Blocker & Reason
    state = readiness.get("status", "IDLE")
    eligible_count = resolution.get("summary", {}).get("eligible", 0)
    
    primary_blocker = "NONE"
    reason = "Capital is ready for deployment."
    
    # Logic for determining the narrative state
    if readiness.get("kill_switch", {}).get("global") == "ARMED":
        state = "FROZEN"
        primary_blocker = "KILL_SWITCH"
        reason = "Global Kill-Switch is ARMED."
    elif readiness.get("drawdown_state") != "NORMAL":
        state = "RESTRICTED"
        primary_blocker = "DRAWDOWN"
        reason = f"System is in {readiness.get('drawdown_state')} drawdown state."
    elif eligible_count == 0:
        state = "IDLE"
        primary_blocker = "STRATEGY"
        reason = "No strategies passed eligibility and factor requirements."
    elif regime == "BEAR_RISK_OFF" or regime == "UNDEFINED":
        state = "RESTRICTED"
        primary_blocker = "REGIME"
        reason = f"Regime '{regime}' restricts capital deployment."
    elif len(readiness.get("violations", [])) > 0:
        state = "RESTRICTED"
        primary_blocker = "RISK"
        reason = "Risk envelopes would be violated by current eligibility."
        
    # Construct Record
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tick_id": tick_dir.name,
        "state": state,
        "primary_blocker": primary_blocker,
        "eligible_strategies": eligible_count,
        "capital_ceiling_available": readiness.get("meta", {}).get("total_capital", 100),
        "reason": reason
    }
    
    # Append content
    timeline.insert(0, record) # Newest first
    
    # Cap timeline length (e.g., last 500 ticks)
    if len(timeline) > 500:
        timeline = timeline[:500]
        
    # Persist
    timeline_path.parent.mkdir(parents=True, exist_ok=True)
    with open(timeline_path, 'w') as f:
        json.dump(timeline, f, indent=2)
        
    return record
