from pathlib import Path
from typing import Dict, Any
import json

try:
    from governance.suppression_state import compute_suppression_for_market
except Exception:
    from src.governance.suppression_state import compute_suppression_for_market  # type: ignore

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _read_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_suppression_status(market: str = "US") -> Dict[str, Any]:
    market = market.upper()
    payload = compute_suppression_for_market(market)
    summary = payload.get("summary", {})
    registry = payload.get("registry", {})
    return {
        "suppression": summary,
        "registry": registry,
        "trace": {
            "state_source": f"docs/intelligence/suppression_state_{market}.json",
            "registry_source": f"docs/intelligence/suppression_reason_registry_{market}.json",
            "audit_source": "docs/audit/f5_suppression/suppression_state_transitions.jsonl",
        },
    }

