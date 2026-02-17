"""
Jules Configuration
===================
Configuration for the Jules execution backend.
"""

import os
from pathlib import Path

# Load .env from project root
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parents[2] / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass

# Jules API Endpoint
JULES_API_URL = os.environ.get("JULES_API_URL", "https://jules.googleapis.com/v1alpha")

# Jules API Key
JULES_API_KEY = os.environ.get("JULES_API_KEY", "")

# Routing Thresholds
JULES_MIN_FILES = 5  # Minimum number of files for Jules unless forced
JULES_MAX_FILES = 50 # Safety cap

# Timeouts
JULES_POLL_INTERVAL = 5  # Seconds
JULES_TIMEOUT = 300      # Seconds (5 minutes)

# Forbidden Paths for Jules
JULES_FORBIDDEN_PATHS = [
    "docs/memory",
    "automation/profiles",
    ".git",
]
