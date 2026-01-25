"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Maximum Loss Guard Model

Checks if a trade would exceed daily or per-trade loss limits.
This is a SIMULATION, not a live trading instruction.
##############################################################################
"""

from typing import NamedTuple


class LossGuardResult(NamedTuple):
    """Result of a loss guard check."""
    allowed: bool
    reason: str
    current_value: float
    limit_value: float


def check_daily_loss_limit(
    current_daily_loss: float,
    proposed_risk: float,
    max_daily_loss: float,
) -> LossGuardResult:
    """Check if a trade would exceed daily loss limit.

    Args:
        current_daily_loss: Realized loss so far today (positive number).
        proposed_risk: Risk amount of proposed trade.
        max_daily_loss: Maximum allowed daily loss.

    Returns:
        LossGuardResult indicating if trade is allowed.
    """
    projected_loss = current_daily_loss + proposed_risk

    if projected_loss > max_daily_loss:
        return LossGuardResult(
            allowed=False,
            reason=f"Would exceed daily loss limit: {projected_loss:.2f} > {max_daily_loss:.2f}",
            current_value=projected_loss,
            limit_value=max_daily_loss,
        )

    return LossGuardResult(
        allowed=True,
        reason="Within daily loss limit",
        current_value=projected_loss,
        limit_value=max_daily_loss,
    )


def check_trade_loss_limit(
    trade_risk: float,
    max_trade_risk: float,
) -> LossGuardResult:
    """Check if a single trade exceeds per-trade risk limit.

    Args:
        trade_risk: Risk amount of the proposed trade.
        max_trade_risk: Maximum allowed risk per trade.

    Returns:
        LossGuardResult indicating if trade is allowed.
    """
    if trade_risk > max_trade_risk:
        return LossGuardResult(
            allowed=False,
            reason=f"Trade risk exceeds limit: {trade_risk:.2f} > {max_trade_risk:.2f}",
            current_value=trade_risk,
            limit_value=max_trade_risk,
        )

    return LossGuardResult(
        allowed=True,
        reason="Within per-trade risk limit",
        current_value=trade_risk,
        limit_value=max_trade_risk,
    )


def check_drawdown_limit(
    current_drawdown_pct: float,
    max_drawdown_pct: float,
) -> LossGuardResult:
    """Check if current drawdown exceeds limit.

    Args:
        current_drawdown_pct: Current drawdown as percentage.
        max_drawdown_pct: Maximum allowed drawdown percentage.

    Returns:
        LossGuardResult indicating if trading should continue.
    """
    if current_drawdown_pct > max_drawdown_pct:
        return LossGuardResult(
            allowed=False,
            reason=f"Drawdown limit exceeded: {current_drawdown_pct:.1f}% > {max_drawdown_pct:.1f}%",
            current_value=current_drawdown_pct,
            limit_value=max_drawdown_pct,
        )

    return LossGuardResult(
        allowed=True,
        reason="Within drawdown limit",
        current_value=current_drawdown_pct,
        limit_value=max_drawdown_pct,
    )


def calculate_remaining_daily_risk(
    current_daily_loss: float,
    max_daily_loss: float,
) -> float:
    """Calculate remaining risk budget for the day.

    Args:
        current_daily_loss: Realized loss so far today.
        max_daily_loss: Maximum allowed daily loss.

    Returns:
        Remaining risk budget (can be negative if already exceeded).
    """
    return max_daily_loss - current_daily_loss
