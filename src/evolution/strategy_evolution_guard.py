"""
Strategy Evolution Guard.
Enforces read-only access to structural evolution artifacts.
EV-TICK may reference but never modify evolution outputs.

Version: 1.0
Date: 2026-01-29
"""
import os
from pathlib import Path

# Versioned evolution reference
STRATEGY_EVOLUTION_VERSION = "v1"
STRATEGY_EVOLUTION_FROZEN_DATE = "2026-01-29"

# Paths to frozen evolution artifacts (read-only)
PROJECT_ROOT = Path(__file__).parent.parent.parent
FROZEN_EVOLUTION_DIR = PROJECT_ROOT / "docs" / "strategy"

# Guard state
_evolution_invocation_attempted = False


class EvolutionViolationError(Exception):
    """Raised when EV-TICK attempts to invoke evolution logic."""
    pass


def get_evolution_version() -> str:
    """Returns the current frozen evolution version."""
    return STRATEGY_EVOLUTION_VERSION


def get_frozen_date() -> str:
    """Returns the date when evolution was frozen."""
    return STRATEGY_EVOLUTION_FROZEN_DATE


def mark_evolution_attempted():
    """Called when evolution logic is about to be invoked. Used for guard checks."""
    global _evolution_invocation_attempted
    _evolution_invocation_attempted = True


def assert_evolution_not_invoked():
    """
    Guard check: Fails if any evolution logic was invoked during this EV-TICK run.
    Call this at the end of EV-TICK to ensure safety invariants.
    """
    if _evolution_invocation_attempted:
        raise EvolutionViolationError(
            "EV-TICK SAFETY VIOLATION: Structural evolution logic was invoked. "
            "EV-TICK must only resolve eligibility, not run evolution."
        )
    return True


def reset_guard():
    """Resets the guard state (for testing)."""
    global _evolution_invocation_attempted
    _evolution_invocation_attempted = False


def get_frozen_contracts_path() -> Path:
    """Returns the path to frozen strategy contracts."""
    return FROZEN_EVOLUTION_DIR / "strategy_contracts.md"


def get_frozen_universe_path() -> Path:
    """Returns the path to frozen strategy universe."""
    return FROZEN_EVOLUTION_DIR / "strategy_universe.md"


def verify_frozen_artifacts_exist() -> bool:
    """Verifies that frozen evolution artifacts exist and are readable."""
    contracts_path = get_frozen_contracts_path()
    universe_path = get_frozen_universe_path()
    
    if not contracts_path.exists():
        print(f"  [GUARD WARNING] Missing frozen contracts: {contracts_path}")
        return False
    
    if not universe_path.exists():
        print(f"  [GUARD WARNING] Missing frozen universe: {universe_path}")
        return False
    
    return True
