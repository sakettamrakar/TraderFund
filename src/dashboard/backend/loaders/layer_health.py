import json
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

def load_layer_health(market: str = "US") -> Dict[str, Any]:
    """
    Loads System Layer Health (A0.1).
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / "system_layer_health.json"
    if not path.exists():
        return {
            "DATA": {"status": "UNKNOWN"},
            "FACTOR": {"status": "UNKNOWN"},
            "INTELLIGENCE": {"status": "UNKNOWN"},
            "GOVERNANCE": {"status": "UNKNOWN"},
            "error": "Artifact missing: docs/intelligence/system_layer_health.json"
        }
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Flatten to allow Object.entries in frontend if preferred, 
            # but let's return a simple dict.
            result = {}
            for name, status in data.get("layers", {}).items():
                result[name] = {
                    "status": status,
                    "last_updated": data.get("updated_at"),
                    "trace": data.get("trace", {}).get("source")
                }
            result["_meta"] = {
                "truth_epoch": data.get("truth_epoch"),
                "role_id": "A0.1"
            }
            return result
    except Exception as e:
        return {"error": str(e)}
