"""
##############################################################################
## PAPER TRADING ANALYTICS - READ ONLY
##############################################################################
Analytics Dashboard for Paper Trading

This module provides POST-TRADE analysis of paper trading logs.
It is for REFLECTION, not optimization.

Status: PHASE 6 ONLY
NO FEEDBACK TO EXECUTION
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
            f"PHASE LOCK: Paper Trading Analytics requires {REQUIRED_PHASE}. "
            f"Current phase is {ACTIVE_PHASE}."
        )


# Check on import
_check_phase_lock()

from .data_loader import load_trade_logs
from .metrics import calculate_execution_metrics, calculate_performance_metrics
from .dashboard import generate_summary

__all__ = [
    "load_trade_logs",
    "calculate_execution_metrics",
    "calculate_performance_metrics",
    "generate_summary",
]
