from dashboard.backend.utils.filesystem import get_latest_tick_dir, read_json_safe
from typing import Dict, Any, Optional
from dashboard.backend.loaders.provenance import attach_provenance

def load_macro_context(market: str = "US") -> Dict[str, Any]:
    """
    Loads the latest persisted macro context.
    """
    latest_tick = get_latest_tick_dir()
    if not latest_tick:
        return attach_provenance({"error": "No tick data found"}, "docs/evolution/ticks/<latest>/{market}/macro_context.json")
        
    macro_path = latest_tick / market / "macro_context.json"
    if not macro_path.exists():
        # Fallback to global if strict not enforced? No, strict.
        return attach_provenance({"error": "Macro context not found", "timestamp": None}, f"docs/evolution/ticks/{latest_tick.name}/{market}/macro_context.json")
        
    return attach_provenance(read_json_safe(macro_path), f"docs/evolution/ticks/{latest_tick.name}/{market}/macro_context.json")
