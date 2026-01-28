import json
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent # c:\GIT\TraderFund

def _read_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def load_macro_context() -> Dict[str, Any]:
    """
    Loads the latest persisted macro context.
    """
    macro_path = PROJECT_ROOT / "docs" / "macro" / "context" / "macro_context.json"
    if not macro_path.exists():
        return {"error": "Macro context not found", "timestamp": None}
        
    return _read_json_safe(macro_path)
