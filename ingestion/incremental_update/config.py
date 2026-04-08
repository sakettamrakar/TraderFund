import os
from pathlib import Path

# Project Root Discovery
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"

DAILY_BUDGET = 50
DELAY_SECONDS = 13

STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"
BACKFILL_TRACKER = DATA_ROOT / "backfill" / "us" / "backfill_tracker.parquet"
UPDATE_TRACKER = DATA_ROOT / "update" / "us" / "update_tracker.parquet"

VERSION = "1.0.0"
