"""
Stage 0: Universe Hygiene

Deterministic universe reduction from ~7,000 to 1,000-2,000 eligible symbols
using only structural and liquidity criteria.

This stage does NOT compute indicators, detect momentum, or generate signals.
"""

from .models import EligibilityRecord, ExclusionReason
from .eligibility_filter import EligibilityFilter
from .eligibility_runner import run_eligibility_evaluation

__all__ = [
    "EligibilityRecord",
    "ExclusionReason", 
    "EligibilityFilter",
    "run_eligibility_evaluation",
]
