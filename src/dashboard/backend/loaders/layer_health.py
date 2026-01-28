import datetime
from pathlib import Path
from typing import Dict, Any
from dashboard.backend.utils.filesystem import get_latest_tick_dir, META_DIR

def load_layer_health() -> Dict[str, Any]:
    latest_tick = get_latest_tick_dir()
    if not latest_tick:
         return {"layers": []}
         
    def check(name: str, path: Path):
        exists = path.exists()
        return {
            "name": name,
            "status": "OK" if exists else "ERROR",
            "last_updated": datetime.datetime.fromtimestamp(path.stat().st_mtime).isoformat() if exists else None
        }

    layers = [
        check("Regime Context", latest_tick / "regime_context.json"),
        check("Factor Context", latest_tick / "factor_context.json"),
        check("Momentum Watcher", latest_tick / "momentum_emergence.json"),
        check("Expansion Watcher", latest_tick / "expansion_transition.json"),
        check("Dispersion Watcher", latest_tick / "dispersion_breakout.json"),
        check("Liquidity Watcher", latest_tick / "liquidity_compression.json"),
        check("Meta-Analysis", META_DIR / "evolution_comparative_summary.md")
    ]
    return {"layers": layers}
