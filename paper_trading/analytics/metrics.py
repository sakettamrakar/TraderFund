"""
##############################################################################
## PAPER TRADING ANALYTICS - READ ONLY
##############################################################################
Analytics Metrics

Pure functions for calculating trading metrics.
DESCRIPTIVE ONLY - no recommendations.
##############################################################################
"""

import pandas as pd
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionMetrics:
    """Execution-related metrics."""
    total_trades: int
    trades_per_day: float
    avg_holding_minutes: float
    total_symbols: int
    most_traded_symbol: str
    most_traded_count: int


@dataclass
class PerformanceMetrics:
    """Performance-related metrics (PAPER ONLY)."""
    win_rate: float
    avg_win: float
    avg_loss: float
    expectancy: float
    total_pnl: float
    max_drawdown: float
    profit_factor: float


def calculate_execution_metrics(df: pd.DataFrame) -> ExecutionMetrics:
    """Calculate execution metrics from trade data.

    Args:
        df: Trade DataFrame.

    Returns:
        ExecutionMetrics dataclass.
    """
    if df.empty:
        return ExecutionMetrics(
            total_trades=0,
            trades_per_day=0.0,
            avg_holding_minutes=0.0,
            total_symbols=0,
            most_traded_symbol="N/A",
            most_traded_count=0,
        )

    total_trades = len(df)

    # Trades per day
    if "timestamp" in df.columns:
        unique_days = df["timestamp"].dt.date.nunique()
        trades_per_day = total_trades / unique_days if unique_days > 0 else total_trades
    else:
        trades_per_day = total_trades

    # Average holding time
    avg_holding = df["holding_minutes"].mean() if "holding_minutes" in df.columns else 0.0

    # Symbol stats
    total_symbols = df["symbol"].nunique() if "symbol" in df.columns else 0
    if "symbol" in df.columns and not df.empty:
        symbol_counts = df["symbol"].value_counts()
        most_traded = symbol_counts.index[0]
        most_traded_count = symbol_counts.iloc[0]
    else:
        most_traded = "N/A"
        most_traded_count = 0

    return ExecutionMetrics(
        total_trades=total_trades,
        trades_per_day=round(trades_per_day, 1),
        avg_holding_minutes=round(avg_holding, 1),
        total_symbols=total_symbols,
        most_traded_symbol=most_traded,
        most_traded_count=most_traded_count,
    )


def calculate_performance_metrics(df: pd.DataFrame) -> PerformanceMetrics:
    """Calculate performance metrics from trade data.

    These are PAPER metrics only - not proof of real performance.

    Args:
        df: Trade DataFrame.

    Returns:
        PerformanceMetrics dataclass.
    """
    if df.empty or "net_pnl" not in df.columns:
        return PerformanceMetrics(
            win_rate=0.0,
            avg_win=0.0,
            avg_loss=0.0,
            expectancy=0.0,
            total_pnl=0.0,
            max_drawdown=0.0,
            profit_factor=0.0,
        )

    pnl = df["net_pnl"]
    winners = df[pnl > 0]
    losers = df[pnl <= 0]

    # Win rate
    win_rate = len(winners) / len(df) * 100 if len(df) > 0 else 0

    # Average win/loss
    avg_win = winners["net_pnl"].mean() if len(winners) > 0 else 0
    avg_loss = abs(losers["net_pnl"].mean()) if len(losers) > 0 else 0

    # Expectancy
    win_prob = len(winners) / len(df) if len(df) > 0 else 0
    loss_prob = 1 - win_prob
    expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)

    # Total P&L
    total_pnl = pnl.sum()

    # Max drawdown
    cumulative = pnl.cumsum()
    peak = cumulative.expanding().max()
    drawdown = cumulative - peak
    max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0

    # Profit factor
    gross_profit = winners["net_pnl"].sum() if len(winners) > 0 else 0
    gross_loss = abs(losers["net_pnl"].sum()) if len(losers) > 0 else 1
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

    return PerformanceMetrics(
        win_rate=round(win_rate, 1),
        avg_win=round(avg_win, 2),
        avg_loss=round(avg_loss, 2),
        expectancy=round(expectancy, 2),
        total_pnl=round(total_pnl, 2),
        max_drawdown=round(max_drawdown, 2),
        profit_factor=round(profit_factor, 2),
    )
