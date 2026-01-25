"""
##############################################################################
## PAPER TRADING ONLY - NO REAL ORDERS
##############################################################################
Paper Trading Execution Layer (Phase 6)

This module simulates trade execution without placing real orders.
It consumes Momentum Engine signals and logs simulated trades.

Status: PHASE 6 ONLY
NO REAL CAPITAL AT RISK
##############################################################################
"""

import os

# ---------------------------------------------------------------------------
# Phase Lock
# ---------------------------------------------------------------------------
ACTIVE_PHASE = os.environ.get("TRADERFUND_ACTIVE_PHASE", "5")
REQUIRED_PHASE = "PHASE_6_PAPER"


def _check_phase_lock() -> None:
    """Fail fast if not in Phase 6 Paper Trading."""
    if ACTIVE_PHASE != REQUIRED_PHASE:
        raise RuntimeError(
            f"PHASE LOCK: Paper Trading requires {REQUIRED_PHASE}. "
            f"Current phase is {ACTIVE_PHASE}. "
            "This module simulates trades - NO REAL ORDERS."
        )


# Check on import
_check_phase_lock()

from .trade_executor import PaperTradeExecutor
from .position_tracker import PositionTracker
from .pnl_calculator import calculate_gross_pnl, calculate_net_pnl

__all__ = [
    "PaperTradeExecutor",
    "PositionTracker",
    "calculate_gross_pnl",
    "calculate_net_pnl",
]
