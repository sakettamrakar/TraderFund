"""Historical Backfill - Config"""
import os
from pathlib import Path

# Project Root Discovery
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"

# Budget limits
DAILY_BUDGET = 25  # Max symbols per run
DELAY_SECONDS = 13  # Between API calls

# Paths
SYMBOL_MASTER = DATA_ROOT / "master" / "us" / "symbol_master.parquet"
ELIGIBILITY_PATH = DATA_ROOT / "master" / "us" / "universe_eligibility.parquet"
TRACKER_PATH = DATA_ROOT / "backfill" / "us" / "backfill_tracker.parquet"
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"
RAW_PATH = DATA_ROOT / "raw" / "us"

# History requirements
MIN_HISTORY_DAYS = 60

VERSION = "1.0.0"
