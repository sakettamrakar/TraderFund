"""Incremental Update - Config"""
from pathlib import Path

DAILY_BUDGET = 50
DELAY_SECONDS = 13

DATA_ROOT = Path("data")
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"
BACKFILL_TRACKER = DATA_ROOT / "backfill" / "us" / "backfill_tracker.parquet"
UPDATE_TRACKER = DATA_ROOT / "update" / "us" / "update_tracker.parquet"

VERSION = "1.0.0"
