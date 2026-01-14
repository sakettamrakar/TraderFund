
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# Rate Limiting (Free Tier Defaults)
# 5 calls per minute is the standard free tier limit to be safe
MAX_CALLS_PER_MINUTE = 5
MAX_CALLS_PER_DAY = 500

# Token Bucket Settings
BUCKET_CAPACITY = 5
REFILL_RATE_SECONDS = 60.0 / MAX_CALLS_PER_MINUTE  # ~12 seconds per token

# Project Paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_BASE_DIR = PROJECT_ROOT / "data"

# US Market Data Paths
RAW_BASE_DIR = DATA_BASE_DIR / "raw" / "us"
STAGING_DIR = DATA_BASE_DIR / "staging" / "us"
ANALYTICS_DIR = DATA_BASE_DIR / "analytics" / "us"
MASTER_DIR = DATA_BASE_DIR / "master" / "us"

# Ensure directories exist
RAW_BASE_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR.mkdir(parents=True, exist_ok=True)
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
MASTER_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
SYMBOLS_CSV_PATH = MASTER_DIR / "symbols.csv"
METADATA_PARQUET_PATH = MASTER_DIR / "universe_metadata.parquet"

# Timezone
TIMEZONE = "UTC"
