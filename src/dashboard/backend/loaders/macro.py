from dashboard.backend.utils.filesystem import get_latest_tick_dir, read_json_safe
from typing import Dict, Any, Optional

def load_macro_context(market: str = "US") -> Dict[str, Any]:
    """
    Loads the latest persisted macro context.
    """
    latest_tick = get_latest_tick_dir()
    if not latest_tick:
        return {"error": "No tick data found"}
        
    macro_path = latest_tick / market / "macro_context.json"
    if not macro_path.exists():
        # Fallback to global if strict not enforced? No, strict.
        return {"error": "Macro context not found", "timestamp": None}
        
    return read_json_safe(macro_path)
