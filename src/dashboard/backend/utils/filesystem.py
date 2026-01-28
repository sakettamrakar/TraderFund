from pathlib import Path
import json
import os
from typing import Dict, Any, Optional

# --- Configuration & Paths ---
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent # c:\GIT\TraderFund, assumes file is in src/dashboard/backend/utils
DOCS_DIR = PROJECT_ROOT / "docs"
EV_DIR = DOCS_DIR / "evolution"
TICKS_DIR = EV_DIR / "ticks"
LEDGER_DIR = DOCS_DIR / "epistemic" / "ledger"
META_DIR = EV_DIR / "meta_analysis"

def get_latest_tick_dir() -> Optional[Path]:
    if not TICKS_DIR.exists():
        return None
    dirs = sorted([d for d in TICKS_DIR.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True)
    if not dirs:
        return None
    return dirs[0]

def get_ticks_history(limit: int = 10) -> list[Path]:
    if not TICKS_DIR.exists():
        return []
    return sorted([d for d in TICKS_DIR.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True)[:limit]

def read_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def read_markdown_safe(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""
