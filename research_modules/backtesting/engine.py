"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Backtesting Engine Core

Event-driven backtesting engine for historical strategy validation.
##############################################################################
"""

import os
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Phase Lock
# ---------------------------------------------------------------------------
ACTIVE_PHASE = int(os.environ.get("TRADERFUND_ACTIVE_PHASE", "5"))
MINIMUM_ACTIVATION_PHASE = 6


def _check_phase_lock() -> None:
    """Fail fast if the current phase is below the activation threshold."""
    if ACTIVE_PHASE < MINIMUM_ACTIVATION_PHASE:
        raise RuntimeError(
            f"PHASE LOCK: Backtesting module requires Phase {MINIMUM_ACTIVATION_PHASE}+. "
            f"Current phase is {ACTIVE_PHASE}. This module is RESEARCH-ONLY."
        )


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------
@dataclass
class Trade:
    """Represents a single simulated trade."""
    entry_time: datetime
    exit_time: Optional[datetime]
    symbol: str
    side: str  # "LONG" only for now
    entry_price: float
    exit_price: Optional[float] = None
    quantity: int = 1
    pnl: float = 0.0
    r_multiple: float = 0.0
    is_closed: bool = False


@dataclass
class BacktestResult:
    """Container for backtest results."""
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    initial_capital: float = 100000.0
    final_capital: float = 100000.0


# ---------------------------------------------------------------------------
# Strategy Interface
# ---------------------------------------------------------------------------
class StrategyBase:
    """Abstract base class for backtestable strategies."""

    def on_candle(self, candle: Dict[str, Any], state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Called for each candle in the backtest.

        Args:
            candle: OHLCV candle data.
            state: Current portfolio state.

        Returns:
            An action dict with keys: {"action": "BUY"|"SELL"|None, "quantity": int}
            or None if no action.
        """
        raise NotImplementedError("Subclasses must implement on_candle")


# ---------------------------------------------------------------------------
# Backtest Engine
# ---------------------------------------------------------------------------
class BacktestEngine:
    """Event-driven backtesting engine.

    Attributes:
        initial_capital: Starting capital for the simulation.
        slippage_pct: Simulated slippage as a percentage.
        commission_per_trade: Fixed commission per trade.
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        slippage_pct: float = 0.05,
        commission_per_trade: float = 20.0,
    ):
        _check_phase_lock()
        self.initial_capital = initial_capital
        self.slippage_pct = slippage_pct
        self.commission_per_trade = commission_per_trade

    def run(
        self,
        strategy: StrategyBase,
        data: pd.DataFrame,
        risk_per_trade_pct: float = 1.0,
    ) -> BacktestResult:
        """Execute a backtest.

        Args:
            strategy: A StrategyBase implementation.
            data: DataFrame with columns: timestamp, open, high, low, close, volume.
            risk_per_trade_pct: Percentage of capital risked per trade for R calculation.

        Returns:
            BacktestResult with trade log and equity curve.
        """
        if data.empty:
            logger.warning("Empty data provided to backtest engine.")
            return BacktestResult(initial_capital=self.initial_capital)

        # Ensure sorted by timestamp
        data = data.sort_values("timestamp").reset_index(drop=True)

        result = BacktestResult(
            initial_capital=self.initial_capital,
            start_time=data["timestamp"].iloc[0],
            end_time=data["timestamp"].iloc[-1],
        )
        capital = self.initial_capital
        result.equity_curve.append(capital)

        state: Dict[str, Any] = {
            "position": None,  # Current Trade object or None
            "capital": capital,
        }

        for idx, row in data.iterrows():
            candle = row.to_dict()
            action = strategy.on_candle(candle, state)

            if action is None:
                pass
            elif action.get("action") == "BUY" and state["position"] is None:
                # Open a LONG position
                entry_price = candle["close"] * (1 + self.slippage_pct / 100)
                quantity = action.get("quantity", 1)
                trade = Trade(
                    entry_time=candle["timestamp"],
                    exit_time=None,
                    symbol=candle.get("symbol", "UNKNOWN"),
                    side="LONG",
                    entry_price=entry_price,
                    quantity=quantity,
                )
                state["position"] = trade
                state["capital"] -= self.commission_per_trade
                logger.debug(f"Opened LONG at {entry_price} on {candle['timestamp']}")

            elif action.get("action") == "SELL" and state["position"] is not None:
                # Close the LONG position
                trade = state["position"]
                exit_price = candle["close"] * (1 - self.slippage_pct / 100)
                trade.exit_price = exit_price
                trade.exit_time = candle["timestamp"]
                trade.pnl = (exit_price - trade.entry_price) * trade.quantity - self.commission_per_trade
                
                # Calculate R-multiple
                risk_amount = self.initial_capital * (risk_per_trade_pct / 100)
                if risk_amount > 0:
                    trade.r_multiple = trade.pnl / risk_amount
                
                trade.is_closed = True
                result.trades.append(trade)
                state["capital"] += trade.pnl
                state["position"] = None
                logger.debug(f"Closed LONG at {exit_price}, PnL: {trade.pnl:.2f}")

            # Update equity curve
            current_equity = state["capital"]
            if state["position"] is not None:
                # Mark-to-market
                unrealized = (candle["close"] - state["position"].entry_price) * state["position"].quantity
                current_equity += unrealized
            result.equity_curve.append(current_equity)

        result.final_capital = state["capital"]
        return result
