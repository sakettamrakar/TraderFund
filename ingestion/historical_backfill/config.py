"""Historical Backfill - Config"""
from pathlib import Path

# Budget limits
DAILY_BUDGET = 25  # Max symbols per run
DELAY_SECONDS = 13  # Between API calls

# Paths
DATA_ROOT = Path("data")
SYMBOL_MASTER = DATA_ROOT / "master" / "us" / "symbol_master.parquet"
ELIGIBILITY_PATH = DATA_ROOT / "master" / "us" / "universe_eligibility.parquet"
TRACKER_PATH = DATA_ROOT / "backfill" / "us" / "backfill_tracker.parquet"
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"
RAW_PATH = DATA_ROOT / "raw" / "us"

# History requirements
MIN_HISTORY_DAYS = 60

VERSION = "1.0.0"
