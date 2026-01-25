"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Risk Metrics

Pure calculation functions for risk-related metrics.
##############################################################################
"""

from typing import List, Optional


def calculate_r_multiple(pnl: float, initial_risk: float) -> float:
    """Calculate R-multiple for a trade.

    R-multiple = PnL / Initial Risk
    - Positive R = profitable trade
    - Negative R = losing trade
    - R of 1.0 means you made what you risked

    Args:
        pnl: Profit/loss from the trade.
        initial_risk: Amount risked on entry (always positive).

    Returns:
        R-multiple value.
    """
    if initial_risk == 0:
        return 0.0
    return pnl / initial_risk


def calculate_worst_case_loss(
    position_size: int,
    entry_price: float,
    stop_price: float,
) -> float:
    """Calculate worst-case loss if stop is hit.

    Args:
        position_size: Number of shares.
        entry_price: Entry price per share.
        stop_price: Stop-loss price per share.

    Returns:
        Worst-case loss (always positive).
    """
    stop_distance = abs(entry_price - stop_price)
    return position_size * stop_distance


def calculate_capital_at_risk(
    position_size: int,
    entry_price: float,
    stop_price: float,
    capital: float,
) -> float:
    """Calculate capital at risk as percentage of total capital.

    Args:
        position_size: Number of shares.
        entry_price: Entry price per share.
        stop_price: Stop-loss price per share.
        capital: Total account capital.

    Returns:
        Percentage of capital at risk (0-100).
    """
    if capital <= 0:
        return 0.0
    worst_case = calculate_worst_case_loss(position_size, entry_price, stop_price)
    return (worst_case / capital) * 100


def calculate_expected_value(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
) -> float:
    """Calculate expected value per trade.

    EV = (Win Rate * Avg Win) - (Loss Rate * Avg Loss)

    Args:
        win_rate: Probability of winning (0-1).
        avg_win: Average winning trade amount.
        avg_loss: Average losing trade amount (positive number).

    Returns:
        Expected value per trade.
    """
    loss_rate = 1 - win_rate
    return (win_rate * avg_win) - (loss_rate * avg_loss)


def calculate_kelly_fraction(
    win_rate: float,
    win_loss_ratio: float,
) -> float:
    """Calculate Kelly Criterion fraction.

    Kelly % = W - [(1-W) / R]
    Where W = win rate, R = win/loss ratio

    Args:
        win_rate: Probability of winning (0-1).
        win_loss_ratio: Ratio of average win to average loss.

    Returns:
        Kelly fraction (0-1). Negative means don't bet.
    """
    if win_loss_ratio == 0:
        return 0.0

    kelly = win_rate - ((1 - win_rate) / win_loss_ratio)
    return max(0.0, kelly)  # Don't return negative


def calculate_max_consecutive_losses(capital: float, risk_per_trade: float) -> int:
    """Calculate how many consecutive losses before ruin.

    Args:
        capital: Starting capital.
        risk_per_trade: Fixed dollar risk per trade.

    Returns:
        Number of consecutive losses to deplete capital.
    """
    if risk_per_trade <= 0:
        return 0
    return int(capital / risk_per_trade)
