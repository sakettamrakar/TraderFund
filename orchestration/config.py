"""Scheduler - Config"""
from pathlib import Path

# Paths
DATA_ROOT = Path("data")
LOG_PATH = DATA_ROOT / "logs" / "scheduler"
STATE_PATH = DATA_ROOT / "scheduler" / "state.parquet"
RUN_HISTORY_PATH = DATA_ROOT / "scheduler" / "run_history.parquet"

# Global Safe Mode
ENABLE_KILL_SWITCH = False  # Set Trie to disable all execution

VERSION = "1.0.0"
