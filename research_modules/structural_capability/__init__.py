"""
Stage 1: Structural Capability

Evaluates whether a stock is structurally healthy, directionally biased,
institutionally compatible, and volatility-appropriate.

BEHAVIOR-first design: Indicators are optional evidence providers.
"""

from .models import StructuralCapability, BehaviorScore, ConfidenceLevel
from .aggregator import StructuralAggregator
from .runner import run_structural_evaluation

__all__ = [
    "StructuralCapability",
    "BehaviorScore",
    "ConfidenceLevel",
    "StructuralAggregator",
    "run_structural_evaluation",
]
