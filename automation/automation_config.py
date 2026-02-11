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

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Global instance for easy import
config = AutomationConfig.get()
