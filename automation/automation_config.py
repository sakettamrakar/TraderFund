"""
Automation Configuration & Shared State
=======================================
Holds global configuration for the autonomous build loop,
including the DRY_RUN flag and the active RunJournal instance.
Also defines the SecurityViolation exception for safety guards.
"""

class SecurityViolation(Exception):
    """Raised when an autonomous agent attempts to violate a safety invariant."""
    pass

class AutomationConfig:
    _instance = None

    def __init__(self):
        self.dry_run = False
        self.journal = None
        self.test_router = False
        self.EXECUTOR_PRIORITY = ["JULES", "GEMINI"]
        self.HUMAN_SUPERVISED = False
        self.JULES_PR_POLICY = "WAIT_FOR_SEMANTIC"
        self.JULES_POLL_TIMEOUT_SECONDS = 1200
        self.JULES_POLL_INTERVAL_SECONDS = 20
        self.JULES_POLL_ERROR_THRESHOLD = 3
        self.SEMANTIC_REGRESSION_TOLERANCE = 0.03
        self.REGRESSION_PENALTY_WEIGHT = 0.15
        self.CLEAN_RECOVERY_THRESHOLD = 3
        self.RECOVERY_WEIGHT = 0.05
        # Phase AB: Visual Validation
        self.visual_validation_enabled = True
        self.base_url = "http://localhost:3000"
        self.screenshot_baseline_path = "automation/visual/baseline.png"

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Global instance for easy import os
from dotenv import load_dotenv, find_dotenv

# Load .env explicitly
load_dotenv(find_dotenv(usecwd=True))

config = AutomationConfig.get()
