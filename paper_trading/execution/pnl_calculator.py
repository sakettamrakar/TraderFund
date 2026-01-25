"""
##############################################################################
## PAPER TRADING ONLY - NO REAL ORDERS
##############################################################################
P&L Calculator

Pure functions for calculating profit and loss.
##############################################################################
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TradePnL:
    """P&L for a single trade."""
    symbol: str
    gross_pnl: float
    net_pnl: float
    entry_slippage: float
    exit_slippage: float
    quantity: int

    @property
    def total_slippage(self) -> float:
        return self.entry_slippage + self.exit_slippage


def calculate_gross_pnl(
    entry_price: float,
    exit_price: float,
    quantity: int,
) -> float:
    """Calculate gross P&L (before slippage).

    Args:
        entry_price: Entry fill price.
        exit_price: Exit fill price.
        quantity: Number of shares.

    Returns:
        Gross P&L in currency units.
    """
    return (exit_price - entry_price) * quantity


def calculate_net_pnl(
    gross_pnl: float,
    entry_slippage: float,
    exit_slippage: float,
    quantity: int,
) -> float:
    """Calculate net P&L (after slippage).

    Slippage is already reflected in fill prices, so this
    just documents the impact.

    Args:
        gross_pnl: Gross P&L.
        entry_slippage: Entry slippage per share.
        exit_slippage: Exit slippage per share.
        quantity: Number of shares.

    Returns:
        Net P&L in currency units.
    """
    total_slippage_cost = (entry_slippage + exit_slippage) * quantity
    return gross_pnl - total_slippage_cost


def calculate_pnl_pct(
    pnl: float,
    entry_price: float,
    quantity: int,
) -> float:
    """Calculate P&L as percentage of entry capital.

    Args:
        pnl: P&L in currency units.
        entry_price: Entry price per share.
        quantity: Number of shares.

    Returns:
        P&L percentage.
    """
    capital = entry_price * quantity
    if capital == 0:
        return 0.0
    return (pnl / capital) * 100


@dataclass
class CumulativeMetrics:
    """Cumulative trading metrics."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_gross_pnl: float
    total_net_pnl: float
    total_slippage: float
    win_rate: float
    avg_pnl: float


def calculate_cumulative_metrics(trades: List[TradePnL]) -> CumulativeMetrics:
    """Calculate cumulative metrics from a list of trades.

    Args:
        trades: List of TradePnL objects.

    Returns:
        CumulativeMetrics summary.
    """
    if not trades:
        return CumulativeMetrics(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            total_gross_pnl=0.0,
            total_net_pnl=0.0,
            total_slippage=0.0,
            win_rate=0.0,
            avg_pnl=0.0,
        )

    winning = [t for t in trades if t.net_pnl > 0]
    losing = [t for t in trades if t.net_pnl <= 0]

    total_gross = sum(t.gross_pnl for t in trades)
    total_net = sum(t.net_pnl for t in trades)
    total_slip = sum(t.total_slippage * t.quantity for t in trades)

    return CumulativeMetrics(
        total_trades=len(trades),
        winning_trades=len(winning),
        losing_trades=len(losing),
        total_gross_pnl=total_gross,
        total_net_pnl=total_net,
        total_slippage=total_slip,
        win_rate=len(winning) / len(trades) * 100 if trades else 0,
        avg_pnl=total_net / len(trades) if trades else 0,
    )
