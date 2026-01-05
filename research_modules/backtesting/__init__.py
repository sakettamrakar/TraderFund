"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Backtesting Engine (Module A)

This module provides historical strategy validation capabilities.
It is strictly isolated from production execution and MUST NOT influence
live trading decisions.

Status: RESEARCH-ONLY
Activation Phase: 6+
##############################################################################
"""

from .engine import BacktestEngine
from .data_adapter import HistoricalDataAdapter
from .metrics import (
    calculate_win_rate,
    calculate_expectancy,
    calculate_max_drawdown,
    calculate_avg_r,
)
from .runner import BacktestRunner

__all__ = [
    "BacktestEngine",
    "HistoricalDataAdapter",
    "BacktestRunner",
    "calculate_win_rate",
    "calculate_expectancy",
    "calculate_max_drawdown",
    "calculate_avg_r",
]
