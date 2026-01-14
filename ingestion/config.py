"""Ingestion Central Configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_BASE_DIR = PROJECT_ROOT.parent / "data"

# Global API Limits
GLOBAL_DAILY_BUDGET = 50
KEYS_ENV_VAR = "ALPHA_VANTAGE_KEYS"

# Default fallback key (legacy support)
LEGACY_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# State Persistence
CONFIG_DIR = DATA_BASE_DIR / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
API_USAGE_STATE_FILE = CONFIG_DIR / "api_key_usage.json"
