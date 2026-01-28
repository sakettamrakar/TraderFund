from dashboard.backend.utils.filesystem import get_ticks_history, read_json_safe
import datetime
from typing import Dict, Any

def load_watcher_timeline(limit: int = 10) -> Dict[str, Any]:
    ticks = get_ticks_history(limit)
    history = []
    
    for d in ticks:
        try:
             ts_str = d.name.replace("tick_", "")
             dt = datetime.datetime.fromtimestamp(int(ts_str)).isoformat()
        except:
             dt = d.name
             
        mom = read_json_safe(d / "momentum_emergence.json").get("momentum_emergence", {})
        exp = read_json_safe(d / "expansion_transition.json").get("expansion_transition", {})
        dis = read_json_safe(d / "dispersion_breakout.json").get("dispersion_breakout", {})
        liq = read_json_safe(d / "liquidity_compression.json").get("liquidity_compression", {})
        
        history.append({
            "timestamp": dt,
            "momentum": mom.get("state", "NONE"),
            "expansion": exp.get("state", "NONE"),
            "dispersion": dis.get("state", "NONE"),
            "liquidity": liq.get("state", "NEUTRAL")
        })
        
    return {"history": history}
