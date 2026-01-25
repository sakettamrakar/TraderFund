"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Percent of Equity Risk Model

Calculates maximum position size as a percentage of total equity.
This is a SIMULATION, not a live trading instruction.
##############################################################################
"""


def calculate_max_position_value(
    equity: float,
    max_position_pct: float = 10.0,
) -> float:
    """Calculate maximum position value based on equity percentage.

    Args:
        equity: Total account equity.
        max_position_pct: Maximum percentage of equity for a single position (0-100).

    Returns:
        Maximum position value in dollars.
    """
    if equity <= 0 or max_position_pct <= 0:
        return 0.0
    return equity * (max_position_pct / 100)


def calculate_max_shares(
    equity: float,
    price: float,
    max_position_pct: float = 10.0,
) -> int:
    """Calculate maximum shares based on equity percentage.

    Args:
        equity: Total account equity.
        price: Current/entry price per share.
        max_position_pct: Maximum percentage of equity for a single position.

    Returns:
        Maximum number of shares (rounded down).
    """
    if equity <= 0 or price <= 0 or max_position_pct <= 0:
        return 0

    max_value = calculate_max_position_value(equity, max_position_pct)
    return int(max_value / price)


def calculate_portfolio_concentration(
    position_value: float,
    total_equity: float,
) -> float:
    """Calculate position concentration as percentage of portfolio.

    Args:
        position_value: Value of the position.
        total_equity: Total portfolio equity.

    Returns:
        Concentration percentage (0-100).
    """
    if total_equity <= 0:
        return 0.0
    return (position_value / total_equity) * 100


def check_concentration_limit(
    position_value: float,
    total_equity: float,
    max_concentration_pct: float = 10.0,
) -> bool:
    """Check if position would exceed concentration limit.

    Args:
        position_value: Proposed position value.
        total_equity: Total portfolio equity.
        max_concentration_pct: Maximum allowed concentration.

    Returns:
        True if within limit, False if would exceed.
    """
    concentration = calculate_portfolio_concentration(position_value, total_equity)
    return concentration <= max_concentration_pct
