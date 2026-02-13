"""
Intent Loader
=============
Loads the appropriate human intent file for execution.
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("intent_loader")

RUNS_DIR = Path("automation/runs")

def find_latest_intent() -> Optional[Path]:
    """Finds the most recent human_intent.json in automation/runs."""
    if not RUNS_DIR.exists():
        return None

    # Get all run directories
    run_dirs = [d for d in RUNS_DIR.iterdir() if d.is_dir()]

    # Sort by modification time (newest first)
    run_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)

    for run_dir in run_dirs:
        intent_path = run_dir / "human_intent.json"
        if intent_path.exists():
            return intent_path

    return None

def load_intent(intent_path: Path) -> Dict[str, Any]:
    """Loads and validates the intent file."""
    if not intent_path.exists():
        logger.error(f"Intent file {intent_path} not found.")
        return {}

    try:
        return json.loads(intent_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load intent file: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="Intent Loader")
    parser.add_argument("--find-latest", action="store_true", help="Find latest intent file path")
    parser.add_argument("--load", help="Load intent from specific path")
    args = parser.parse_args()

    if args.find_latest:
        path = find_latest_intent()
        if path:
            print(str(path))
        else:
            logger.warning("No intent file found.")

    if args.load:
        intent = load_intent(Path(args.load))
        print(json.dumps(intent, indent=2))

if __name__ == "__main__":
    main()
