"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Backtest Runner

Orchestrates the backtesting process by combining data loading, engine
execution, and metrics calculation.
##############################################################################
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Type
from pathlib import Path

import pandas as pd

from .engine import BacktestEngine, BacktestResult, StrategyBase
from .data_adapter import HistoricalDataAdapter
from .metrics import (
    calculate_win_rate,
    calculate_expectancy,
    calculate_max_drawdown,
    calculate_avg_r,
    calculate_profit_factor,
    calculate_trade_count,
)

logger = logging.getLogger(__name__)


@dataclass
class RunnerConfig:
    """Configuration for a backtest run."""
    data_path: str
    data_file: str
    initial_capital: float = 100000.0
    slippage_pct: float = 0.05
    commission_per_trade: float = 20.0
    risk_per_trade_pct: float = 1.0


@dataclass
class RunnerReport:
    """Complete report from a backtest run."""
    config: RunnerConfig
    result: BacktestResult
    metrics: Dict[str, Any] = field(default_factory=dict)


class BacktestRunner:
    """Orchestrates a complete backtest run.

    This class combines the data adapter, engine, and metrics calculation
    into a single, easy-to-use interface.
    """

    def __init__(self, config: RunnerConfig):
        """Initialize the runner.

        Args:
            config: RunnerConfig with data path and engine settings.
        """
        self.config = config
        self.adapter = HistoricalDataAdapter(config.data_path)
        self.engine = BacktestEngine(
            initial_capital=config.initial_capital,
            slippage_pct=config.slippage_pct,
            commission_per_trade=config.commission_per_trade,
        )

    def run(self, strategy: StrategyBase) -> RunnerReport:
        """Execute a full backtest run.

        Args:
            strategy: A StrategyBase implementation to test.

        Returns:
            RunnerReport with results and calculated metrics.
        """
        logger.info(f"Starting backtest with data: {self.config.data_file}")

        # Load data
        if self.config.data_file.endswith(".parquet"):
            data = self.adapter.load_parquet(self.config.data_file)
        else:
            data = self.adapter.load_csv(self.config.data_file)

        # Run engine
        result = self.engine.run(
            strategy=strategy,
            data=data,
            risk_per_trade_pct=self.config.risk_per_trade_pct,
        )

        # Calculate metrics
        metrics = {
            "trade_count": calculate_trade_count(result.trades),
            "win_rate": calculate_win_rate(result.trades),
            "expectancy": calculate_expectancy(result.trades),
            "max_drawdown_pct": calculate_max_drawdown(result.equity_curve),
            "avg_r": calculate_avg_r(result.trades),
            "profit_factor": calculate_profit_factor(result.trades),
            "total_pnl": result.final_capital - result.initial_capital,
            "return_pct": (result.final_capital - result.initial_capital) / result.initial_capital * 100,
        }

        logger.info(f"Backtest complete. Trades: {metrics['trade_count']}, PnL: {metrics['total_pnl']:.2f}")

        return RunnerReport(
            config=self.config,
            result=result,
            metrics=metrics,
        )

    def print_report(self, report: RunnerReport) -> None:
        """Print a formatted report to stdout.

        Args:
            report: RunnerReport to print.
        """
        print("\n" + "=" * 60)
        print("## RESEARCH BACKTEST REPORT ##")
        print("=" * 60)
        print(f"Data File: {report.config.data_file}")
        print(f"Initial Capital: {report.config.initial_capital:,.2f}")
        print(f"Final Capital: {report.result.final_capital:,.2f}")
        print("-" * 60)
        print(f"Trade Count: {report.metrics['trade_count']}")
        print(f"Win Rate: {report.metrics['win_rate']:.1%}")
        print(f"Expectancy: {report.metrics['expectancy']:.2f}")
        print(f"Avg R: {report.metrics['avg_r']:.2f}")
        print(f"Max Drawdown: {report.metrics['max_drawdown_pct']:.1f}%")
        print(f"Profit Factor: {report.metrics['profit_factor']:.2f}")
        print(f"Total PnL: {report.metrics['total_pnl']:,.2f}")
        print(f"Return: {report.metrics['return_pct']:.1f}%")
        print("=" * 60)
        print("⚠️  WARNING: These results are RESEARCH-ONLY.")
        print("    Do not use for live trading decisions.")
        print("=" * 60 + "\n")
