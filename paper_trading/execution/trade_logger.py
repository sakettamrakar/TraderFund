"""
##############################################################################
## PAPER TRADING ONLY - NO REAL ORDERS
##############################################################################
Trade Logger

Append-only CSV logging for simulated trades.
Human-readable format.
##############################################################################
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Default log directory
DEFAULT_LOG_DIR = Path("paper_trading/logs")


class TradeLogger:
    """Append-only trade logger.

    Logs each simulated trade to CSV for review.
    """

    FIELDS = [
        "timestamp",
        "symbol",
        "entry_price",
        "exit_price",
        "quantity",
        "holding_minutes",
        "gross_pnl",
        "net_pnl",
        "signal_confidence",
        "signal_reason",
        "exit_reason",
    ]

    def __init__(self, log_dir: Optional[Path] = None, session_name: str = "default"):
        """Initialize the logger.

        Args:
            log_dir: Directory for log files.
            session_name: Name for this trading session.
        """
        self.log_dir = log_dir or DEFAULT_LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y%m%d")
        self.log_file = self.log_dir / f"paper_trades_{session_name}_{date_str}.csv"

        # Write header if file is new
        if not self.log_file.exists():
            self._write_header()

        logger.info(f"Trade logger initialized: {self.log_file}")

    def _write_header(self) -> None:
        """Write CSV header."""
        with open(self.log_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.FIELDS)

    def log_trade(
        self,
        symbol: str,
        entry_price: float,
        exit_price: float,
        quantity: int,
        holding_minutes: float,
        gross_pnl: float,
        net_pnl: float,
        signal_confidence: float = 0.0,
        signal_reason: str = "",
        exit_reason: str = "",
    ) -> None:
        """Log a completed trade.

        Args:
            symbol: Instrument symbol.
            entry_price: Entry fill price.
            exit_price: Exit fill price.
            quantity: Number of shares.
            holding_minutes: Time held in minutes.
            gross_pnl: Gross P&L.
            net_pnl: Net P&L after slippage.
            signal_confidence: Confidence from momentum signal.
            signal_reason: Reason from momentum signal.
            exit_reason: Why the trade was exited.
        """
        row = [
            datetime.now().isoformat(),
            symbol,
            f"{entry_price:.2f}",
            f"{exit_price:.2f}",
            quantity,
            f"{holding_minutes:.2f}",
            f"{gross_pnl:.2f}",
            f"{net_pnl:.2f}",
            f"{signal_confidence:.2f}",
            signal_reason,
            exit_reason,
        ]

        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        logger.info(f"Logged trade: {symbol} P&L={net_pnl:.2f}")

    def log_from_closed_position(
        self,
        closed: Dict,
        gross_pnl: float,
        net_pnl: float,
    ) -> None:
        """Log from a closed position dict.

        Args:
            closed: Dict from PositionTracker.close_position().
            gross_pnl: Gross P&L.
            net_pnl: Net P&L.
        """
        self.log_trade(
            symbol=closed["symbol"],
            entry_price=closed["entry_price"],
            exit_price=closed["exit_price"],
            quantity=closed["quantity"],
            holding_minutes=closed["holding_minutes"],
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            signal_confidence=closed.get("signal_confidence", 0),
            signal_reason=closed.get("signal_reason", ""),
            exit_reason=closed.get("exit_reason", ""),
        )
