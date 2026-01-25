"""
Stage 2: Energy Setup

Evaluates stored potential energy via volatility compression, range balance,
mean adherence, and energy duration.

Philosophy: Energy ≠ Direction. Quiet stocks are often most interesting.
"""

from .models import EnergySetup, EnergyState
from .aggregator import EnergyAggregator
from .runner import run_energy_evaluation

__all__ = [
    "EnergySetup",
    "EnergyState",
    "EnergyAggregator",
    "run_energy_evaluation",
]
