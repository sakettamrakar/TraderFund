"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Unit tests for the metrics module.
##############################################################################
"""

import pytest
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


# Minimal Trade mock for testing metrics without importing engine
@dataclass
class MockTrade:
    pnl: float
    r_multiple: float
    is_closed: bool = True
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    symbol: str = "TEST"
    side: str = "LONG"
    entry_price: float = 100.0
    exit_price: float = 100.0
    quantity: int = 1


class TestCalculateWinRate:
    def test_no_trades(self):
        from research_modules.backtesting.metrics import calculate_win_rate
        assert calculate_win_rate([]) == 0.0

    def test_all_winners(self):
        from research_modules.backtesting.metrics import calculate_win_rate
        trades = [MockTrade(pnl=100, r_multiple=1.0), MockTrade(pnl=50, r_multiple=0.5)]
        assert calculate_win_rate(trades) == 1.0

    def test_all_losers(self):
        from research_modules.backtesting.metrics import calculate_win_rate
        trades = [MockTrade(pnl=-100, r_multiple=-1.0), MockTrade(pnl=-50, r_multiple=-0.5)]
        assert calculate_win_rate(trades) == 0.0

    def test_mixed(self):
        from research_modules.backtesting.metrics import calculate_win_rate
        trades = [
            MockTrade(pnl=100, r_multiple=1.0),
            MockTrade(pnl=-50, r_multiple=-0.5),
            MockTrade(pnl=25, r_multiple=0.25),
            MockTrade(pnl=-25, r_multiple=-0.25),
        ]
        assert calculate_win_rate(trades) == 0.5


class TestCalculateExpectancy:
    def test_no_trades(self):
        from research_modules.backtesting.metrics import calculate_expectancy
        assert calculate_expectancy([]) == 0.0

    def test_positive_expectancy(self):
        from research_modules.backtesting.metrics import calculate_expectancy
        trades = [
            MockTrade(pnl=200, r_multiple=2.0),  # Win
            MockTrade(pnl=-50, r_multiple=-0.5),  # Loss
        ]
        # Win Rate: 0.5, Avg Win: 200, Loss Rate: 0.5, Avg Loss: 50
        # Expectancy = (0.5 * 200) - (0.5 * 50) = 100 - 25 = 75
        assert calculate_expectancy(trades) == 75.0


class TestCalculateMaxDrawdown:
    def test_no_drawdown(self):
        from research_modules.backtesting.metrics import calculate_max_drawdown
        equity = [100, 110, 120, 130, 140]
        assert calculate_max_drawdown(equity) == 0.0

    def test_with_drawdown(self):
        from research_modules.backtesting.metrics import calculate_max_drawdown
        equity = [100, 120, 110, 130, 100]  # Peak 130, trough 100 = 23.08% DD
        dd = calculate_max_drawdown(equity)
        assert 23.0 < dd < 24.0

    def test_empty(self):
        from research_modules.backtesting.metrics import calculate_max_drawdown
        assert calculate_max_drawdown([]) == 0.0


class TestCalculateAvgR:
    def test_no_trades(self):
        from research_modules.backtesting.metrics import calculate_avg_r
        assert calculate_avg_r([]) == 0.0

    def test_positive_avg(self):
        from research_modules.backtesting.metrics import calculate_avg_r
        trades = [
            MockTrade(pnl=100, r_multiple=2.0),
            MockTrade(pnl=50, r_multiple=1.0),
        ]
        assert calculate_avg_r(trades) == 1.5

    def test_negative_avg(self):
        from research_modules.backtesting.metrics import calculate_avg_r
        trades = [
            MockTrade(pnl=-100, r_multiple=-2.0),
            MockTrade(pnl=-50, r_multiple=-1.0),
        ]
        assert calculate_avg_r(trades) == -1.5
