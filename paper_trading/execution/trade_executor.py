"""
##############################################################################
## PAPER TRADING ONLY - NO REAL ORDERS
##############################################################################
Paper Trade Executor

Main orchestrator for paper trading execution.
Consumes Momentum Engine signals only.
NO REAL BROKER SDK IMPORTS.
##############################################################################
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

from .order_simulator import simulate_entry, simulate_exit, SimulatedFill
from .position_tracker import PositionTracker
from .pnl_calculator import calculate_gross_pnl, TradePnL
from .trade_logger import TradeLogger

logger = logging.getLogger(__name__)


@dataclass
class MomentumSignal:
    """Expected signal format from Momentum Engine.

    This is a data contract - the actual signals must conform to this.
    """
    symbol: str
    price: float
    confidence: float
    reason: str
    timestamp: datetime


class PaperTradeExecutor:
    """Orchestrates paper trade execution.

    This class:
    - Consumes Momentum Engine signals
    - Simulates entries/exits
    - Tracks positions
    - Logs all trades

    It does NOT:
    - Place real orders
    - Connect to any broker API
    - Use any API keys
    """

    def __init__(
        self,
        slippage_pct: float = 0.0,
        default_quantity: int = 1,
        exit_minutes: float = 5.0,
        session_name: str = "default",
        log_dir: Optional[Path] = None,
    ):
        """Initialize the executor.

        Args:
            slippage_pct: Slippage percentage for simulation (0-100).
            default_quantity: Default shares per trade.
            exit_minutes: Time-based exit in minutes.
            session_name: Session name for logging.
            log_dir: Directory for trade logs.
        """
        self.slippage_pct = slippage_pct
        self.default_quantity = default_quantity
        self.exit_minutes = exit_minutes

        self.position_tracker = PositionTracker()
        self.trade_logger = TradeLogger(log_dir=log_dir, session_name=session_name)
        self.trades: List[TradePnL] = []

        logger.info(
            f"PaperTradeExecutor initialized: slippage={slippage_pct}%, "
            f"exit_minutes={exit_minutes}, session={session_name}"
        )

    def execute_signal(
        self,
        signal: MomentumSignal,
        quantity: Optional[int] = None,
    ) -> Optional[SimulatedFill]:
        """Execute a momentum signal.

        Args:
            signal: MomentumSignal from the Momentum Engine.
            quantity: Override default quantity.

        Returns:
            SimulatedFill if entry was made, None if skipped.
        """
        symbol = signal.symbol.upper()
        qty = quantity or self.default_quantity

        # Check if already in position
        if self.position_tracker.has_position(symbol):
            logger.warning(f"Already in position for {symbol}, skipping signal")
            return None

        # Simulate entry
        fill = simulate_entry(symbol, signal.price, qty, self.slippage_pct)

        # Track position
        self.position_tracker.open_position(
            symbol=symbol,
            entry_price=fill.fill_price,
            quantity=qty,
            signal_confidence=signal.confidence,
            signal_reason=signal.reason,
        )

        logger.info(
            f"PAPER ENTRY: {symbol} @ {fill.fill_price} "
            f"(requested {signal.price}, slippage {fill.slippage})"
        )
        return fill

    def exit_position(
        self,
        symbol: str,
        exit_price: float,
        exit_reason: str = "manual",
    ) -> Optional[TradePnL]:
        """Exit an open position.

        Args:
            symbol: Symbol to exit.
            exit_price: Current price for exit.
            exit_reason: Why exiting.

        Returns:
            TradePnL for the closed trade.
        """
        symbol = symbol.upper()
        if not self.position_tracker.has_position(symbol):
            logger.warning(f"No position for {symbol}, cannot exit")
            return None

        position = self.position_tracker.get_position(symbol)

        # Simulate exit
        fill = simulate_exit(symbol, exit_price, position.quantity, self.slippage_pct)

        # Close position
        closed = self.position_tracker.close_position(symbol, fill.fill_price, exit_reason)

        # Calculate P&L
        gross_pnl = calculate_gross_pnl(
            closed["entry_price"],
            fill.fill_price,
            closed["quantity"]
        )

        # For net P&L, slippage is already in fill prices
        net_pnl = gross_pnl  # Slippage already reflected

        trade_pnl = TradePnL(
            symbol=symbol,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            entry_slippage=0,  # Already in entry price
            exit_slippage=fill.slippage,
            quantity=position.quantity,
        )
        self.trades.append(trade_pnl)

        # Log the trade
        self.trade_logger.log_from_closed_position(closed, gross_pnl, net_pnl)

        logger.info(
            f"PAPER EXIT: {symbol} @ {fill.fill_price}, "
            f"P&L={net_pnl:.2f}, reason={exit_reason}"
        )
        return trade_pnl

    def check_time_exits(self, current_prices: Dict[str, float]) -> List[TradePnL]:
        """Check and execute time-based exits.

        Args:
            current_prices: Dict of symbol -> current price.

        Returns:
            List of closed trades.
        """
        symbols_to_exit = self.position_tracker.get_positions_for_time_exit(self.exit_minutes)
        closed_trades = []

        for symbol in symbols_to_exit:
            price = current_prices.get(symbol)
            if price is None:
                logger.warning(f"No price for {symbol}, cannot exit")
                continue

            trade = self.exit_position(symbol, price, f"time_exit_{self.exit_minutes}min")
            if trade:
                closed_trades.append(trade)

        return closed_trades

    def get_summary(self) -> Dict:
        """Get session summary."""
        from .pnl_calculator import calculate_cumulative_metrics

        metrics = calculate_cumulative_metrics(self.trades)
        return {
            "total_trades": metrics.total_trades,
            "winning_trades": metrics.winning_trades,
            "losing_trades": metrics.losing_trades,
            "win_rate": metrics.win_rate,
            "total_pnl": metrics.total_net_pnl,
            "avg_pnl": metrics.avg_pnl,
            "open_positions": len(self.position_tracker.open_positions),
        }

    def print_summary(self) -> None:
        """Print session summary to stdout."""
        summary = self.get_summary()
        print("\n" + "=" * 60)
        print("## PAPER TRADING SESSION SUMMARY ##")
        print("=" * 60)
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Winning: {summary['winning_trades']} | Losing: {summary['losing_trades']}")
        print(f"Win Rate: {summary['win_rate']:.1f}%")
        print(f"Total P&L: {summary['total_pnl']:.2f}")
        print(f"Avg P&L: {summary['avg_pnl']:.2f}")
        print(f"Open Positions: {summary['open_positions']}")
        print("=" * 60)
        print("⚠️  This is SIMULATED. Results do NOT prove real performance.")
        print("=" * 60 + "\n")
