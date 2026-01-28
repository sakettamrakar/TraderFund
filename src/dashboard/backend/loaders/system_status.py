import datetime
from typing import Dict, Any
from dashboard.backend.utils.filesystem import get_latest_tick_dir, read_markdown_safe, read_json_safe, LEDGER_DIR

def load_system_status() -> Dict[str, Any]:
    latest_tick = get_latest_tick_dir()
    
    last_tick_ts = "N/A"
    status = "IDLE"
    reason = "No data detected"
    last_ingestion = "N/A" # TODO: track this in artifacts
    
    if latest_tick:
        try:
             ts_str = latest_tick.name.replace("tick_", "")
             dt = datetime.datetime.fromtimestamp(int(ts_str))
             last_tick_ts = dt.isoformat()
             last_ingestion = dt.date().isoformat() # Approx for now
        except:
             last_tick_ts = latest_tick.name

        exp_data = read_json_safe(latest_tick / "expansion_transition.json")
        dis_data = read_json_safe(latest_tick / "dispersion_breakout.json")
        
        exp_state = exp_data.get("expansion_transition", {}).get("state", "NONE")
        dis_state = dis_data.get("dispersion_breakout", {}).get("state", "NONE")
        
        if exp_state != "NONE" or dis_state != "NONE":
            status = "OBSERVING"
            reason = f"Expansion: {exp_state}, Dispersion: {dis_state}"
        else:
            status = "IDLE"
            reason = "No expansion or dispersion detected (Stagnation)"

    return {
        "system_state": status,
        "reason": reason,
        "last_ev_tick": last_tick_ts,
        "last_ingestion": last_ingestion,
        "governance_status": "CLEAN" 
    }
