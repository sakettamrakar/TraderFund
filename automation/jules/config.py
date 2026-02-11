"""
Jules Configuration
===================
Configuration for the Jules execution backend.
"""

import os

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
