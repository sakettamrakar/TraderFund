"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
ATR-Based Risk Model

Calculates stop distance and position size using Average True Range.
This is a SIMULATION, not a live trading instruction.
##############################################################################
"""

from typing import Optional


def calculate_atr_stop(
    entry_price: float,
    atr: float,
    multiplier: float = 2.0,
    direction: str = "LONG",
) -> float:
    """Calculate stop price based on ATR.

    Args:
        entry_price: Planned entry price.
        atr: Current ATR value.
        multiplier: ATR multiplier for stop distance (default: 2.0).
        direction: Trade direction ("LONG" or "SHORT").

    Returns:
        Calculated stop price.
    """
    stop_distance = atr * multiplier

    if direction.upper() == "LONG":
        return entry_price - stop_distance
    else:
        return entry_price + stop_distance


def calculate_atr_stop_distance(atr: float, multiplier: float = 2.0) -> float:
    """Calculate stop distance in price terms.

    Args:
        atr: Current ATR value.
        multiplier: ATR multiplier.

    Returns:
        Stop distance in price units.
    """
    return atr * multiplier


def calculate_position_from_atr(
    capital: float,
    risk_pct: float,
    entry_price: float,
    atr: float,
    multiplier: float = 2.0,
) -> int:
    """Calculate position size using ATR-based stop.

    Args:
        capital: Total available capital.
        risk_pct: Percentage of capital to risk (0-100 scale).
        entry_price: Planned entry price.
        atr: Current ATR value.
        multiplier: ATR multiplier for stop distance.

    Returns:
        Number of shares (rounded down).
    """
    if capital <= 0 or risk_pct <= 0 or atr <= 0:
        return 0

    stop_distance = calculate_atr_stop_distance(atr, multiplier)
    if stop_distance == 0:
        return 0

    risk_amount = capital * (risk_pct / 100)
    position_size = risk_amount / stop_distance

    return int(position_size)


def calculate_risk_reward_ratio(
    entry_price: float,
    stop_price: float,
    target_price: float,
) -> float:
    """Calculate risk-reward ratio.

    Args:
        entry_price: Planned entry price.
        stop_price: Planned stop-loss price.
        target_price: Planned target price.

    Returns:
        Risk-reward ratio (e.g., 2.0 means 2:1 reward:risk).
    """
    risk = abs(entry_price - stop_price)
    reward = abs(target_price - entry_price)

    if risk == 0:
        return 0.0

    return reward / risk
