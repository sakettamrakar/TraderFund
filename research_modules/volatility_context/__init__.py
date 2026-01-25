"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Volatility & Market Context Module (Module B)

This module provides market environment classification and volatility metrics.
It LABELS conditions but does NOT make trade decisions.

Status: RESEARCH-ONLY
Activation Phase: 7+
##############################################################################
"""

import os

# ---------------------------------------------------------------------------
# Phase Lock
# ---------------------------------------------------------------------------
ACTIVE_PHASE = int(os.environ.get("TRADERFUND_ACTIVE_PHASE", "5"))
MINIMUM_ACTIVATION_PHASE = 6


def _check_phase_lock() -> None:
    """Fail fast if the current phase is below the activation threshold."""
    if ACTIVE_PHASE < MINIMUM_ACTIVATION_PHASE:
        raise RuntimeError(
            f"PHASE LOCK: Volatility Context module requires Phase {MINIMUM_ACTIVATION_PHASE}+. "
            f"Current phase is {ACTIVE_PHASE}. This module is RESEARCH-ONLY."
        )


# Check on import
_check_phase_lock()

from .context_snapshot import ContextSnapshot
from .runner import ContextRunner

__all__ = [
    "ContextSnapshot",
    "ContextRunner",
]
