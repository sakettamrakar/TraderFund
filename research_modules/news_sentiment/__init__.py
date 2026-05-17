"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
News & Sentiment Analysis Module (Module D)

This module ingests news and generates sentiment observations.
It does NOT make trade decisions or override price/volume signals.

Status: RESEARCH-ONLY
Activation Phase: 9+
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
    active_phase = int(os.environ.get("TRADERFUND_ACTIVE_PHASE", "5"))
    if active_phase < MINIMUM_ACTIVATION_PHASE:
        raise RuntimeError(
            f"PHASE LOCK: News Sentiment module requires Phase {MINIMUM_ACTIVATION_PHASE}+. "
            f"Current phase is {active_phase}. This module is RESEARCH-ONLY."
        )


# Phase lock moved to runtime entrypoints (e.g., SentimentRunner.__init__)

from .sentiment_snapshot import SentimentSnapshot
from .runner import SentimentRunner

__all__ = [
    "SentimentSnapshot",
    "SentimentRunner",
]
