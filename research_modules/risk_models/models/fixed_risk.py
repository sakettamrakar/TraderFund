"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Fixed Fractional Risk Model

Calculates position size based on a fixed percentage of capital at risk.
This is a SIMULATION, not a live trading instruction.
##############################################################################
"""

from typing import Optional


def calculate_risk_amount(capital: float, risk_pct: float) -> float:
    """Calculate the dollar amount to risk per trade.

    Args:
        capital: Total available capital.
        risk_pct: Percentage of capital to risk (0-100 scale).

    Returns:
        Dollar amount at risk.
    """
    if capital <= 0 or risk_pct <= 0:
        return 0.0
    return capital * (risk_pct / 100)


def calculate_position_size(
    capital: float,
    risk_pct: float,
    entry_price: float,
    stop_price: float,
) -> int:
    """Calculate position size (shares) based on fixed fractional risk.

    Formula: Position Size = Risk Amount / Stop Distance

    Args:
        capital: Total available capital.
        risk_pct: Percentage of capital to risk (0-100 scale).
        entry_price: Planned entry price.
        stop_price: Planned stop-loss price.

    Returns:
        Number of shares (rounded down to whole shares).
    """
    if capital <= 0 or risk_pct <= 0:
        return 0

    stop_distance = abs(entry_price - stop_price)
    if stop_distance == 0:
        return 0

    risk_amount = calculate_risk_amount(capital, risk_pct)
    position_size = risk_amount / stop_distance

    return int(position_size)


def calculate_position_value(
    capital: float,
    risk_pct: float,
    entry_price: float,
    stop_price: float,
) -> float:
    """Calculate total position value based on fixed fractional risk.

    Args:
        capital: Total available capital.
        risk_pct: Percentage of capital to risk.
        entry_price: Planned entry price.
        stop_price: Planned stop-loss price.

    Returns:
        Total position value (shares * entry_price).
    """
    shares = calculate_position_size(capital, risk_pct, entry_price, stop_price)
    return shares * entry_price
