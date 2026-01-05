"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Backtest Metrics

Pure functions for calculating performance metrics from backtest results.
##############################################################################
"""

from typing import List, Optional
from dataclasses import dataclass

# Avoid circular import by using forward reference string
# The Trade class is defined in engine.py


def calculate_win_rate(trades: List["Trade"]) -> float:
    """Calculate the win rate from a list of closed trades.

    Args:
        trades: List of Trade objects.

    Returns:
        Win rate as a decimal (0.0 to 1.0).
    """
    closed_trades = [t for t in trades if t.is_closed]
    if not closed_trades:
        return 0.0
    wins = sum(1 for t in closed_trades if t.pnl > 0)
    return wins / len(closed_trades)


def calculate_expectancy(trades: List["Trade"]) -> float:
    """Calculate the expectancy (average PnL per trade).

    Expectancy = (Win Rate * Avg Win) - (Loss Rate * Avg Loss)

    Args:
        trades: List of Trade objects.

    Returns:
        Expectancy value.
    """
    closed_trades = [t for t in trades if t.is_closed]
    if not closed_trades:
        return 0.0

    wins = [t.pnl for t in closed_trades if t.pnl > 0]
    losses = [abs(t.pnl) for t in closed_trades if t.pnl < 0]

    total = len(closed_trades)
    win_rate = len(wins) / total if total > 0 else 0
    loss_rate = len(losses) / total if total > 0 else 0

    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0

    return (win_rate * avg_win) - (loss_rate * avg_loss)


def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """Calculate the maximum drawdown from an equity curve.

    Args:
        equity_curve: List of equity values over time.

    Returns:
        Maximum drawdown as a percentage (0.0 to 100.0).
    """
    if not equity_curve or len(equity_curve) < 2:
        return 0.0

    peak = equity_curve[0]
    max_dd = 0.0

    for value in equity_curve:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak * 100 if peak > 0 else 0.0
        if drawdown > max_dd:
            max_dd = drawdown

    return max_dd


def calculate_avg_r(trades: List["Trade"]) -> float:
    """Calculate the average R-multiple from a list of trades.

    Args:
        trades: List of Trade objects with r_multiple set.

    Returns:
        Average R-multiple.
    """
    closed_trades = [t for t in trades if t.is_closed]
    if not closed_trades:
        return 0.0
    return sum(t.r_multiple for t in closed_trades) / len(closed_trades)


def calculate_profit_factor(trades: List["Trade"]) -> float:
    """Calculate the profit factor (Gross Profits / Gross Losses).

    Args:
        trades: List of Trade objects.

    Returns:
        Profit factor. Returns float('inf') if no losses.
    """
    closed_trades = [t for t in trades if t.is_closed]
    if not closed_trades:
        return 0.0

    gross_profit = sum(t.pnl for t in closed_trades if t.pnl > 0)
    gross_loss = abs(sum(t.pnl for t in closed_trades if t.pnl < 0))

    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def calculate_trade_count(trades: List["Trade"]) -> int:
    """Count the number of closed trades.

    Args:
        trades: List of Trade objects.

    Returns:
        Number of closed trades.
    """
    return sum(1 for t in trades if t.is_closed)


# Type hint for Trade to allow forward reference
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .engine import Trade
