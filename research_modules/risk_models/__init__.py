"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Risk Modeling & Position Sizing Module (Module C)

This module simulates risk scenarios and position sizing.
It does NOT place trades or control live capital.

Status: RESEARCH-ONLY
Activation Phase: 8+
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
            f"PHASE LOCK: Risk Models module requires Phase {MINIMUM_ACTIVATION_PHASE}+. "
            f"Current phase is {ACTIVE_PHASE}. This module is RESEARCH-ONLY."
        )


# Check on import
_check_phase_lock()

from .risk_snapshot import RiskSnapshot
from .simulator import RiskSimulator

__all__ = [
    "RiskSnapshot",
    "RiskSimulator",
]
