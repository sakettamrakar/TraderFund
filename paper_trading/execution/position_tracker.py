"""
##############################################################################
## PAPER TRADING ONLY - NO REAL ORDERS
##############################################################################
Position Tracker

Tracks open positions in paper trading.
Long-only, one position per symbol.
##############################################################################
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """A simulated open position."""
    symbol: str
    entry_price: float
    quantity: int
    entry_time: datetime
    signal_confidence: float = 0.0
    signal_reason: str = ""

    @property
    def holding_seconds(self) -> float:
        return (datetime.now() - self.entry_time).total_seconds()

    @property
    def holding_minutes(self) -> float:
        return self.holding_seconds / 60


class PositionTracker:
    """Tracks simulated positions.

    Rules:
    - One position per symbol
    - Long-only
    - Explicit exit required (time-based or manual)
    """

    def __init__(self):
        self._positions: Dict[str, Position] = {}
        self._closed_positions: List[Dict] = []

    def has_position(self, symbol: str) -> bool:
        """Check if a position exists for symbol."""
        return symbol.upper() in self._positions

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for symbol."""
        return self._positions.get(symbol.upper())

    def open_position(
        self,
        symbol: str,
        entry_price: float,
        quantity: int,
        signal_confidence: float = 0.0,
        signal_reason: str = "",
    ) -> Position:
        """Open a new position.

        Args:
            symbol: Instrument symbol.
            entry_price: Simulated entry price.
            quantity: Number of shares.
            signal_confidence: Confidence from momentum signal.
            signal_reason: Reason from momentum signal.

        Returns:
            Created Position.

        Raises:
            ValueError: If position already exists for symbol.
        """
        symbol = symbol.upper()
        if self.has_position(symbol):
            raise ValueError(f"Position already exists for {symbol}")

        position = Position(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=datetime.now(),
            signal_confidence=signal_confidence,
            signal_reason=signal_reason,
        )
        self._positions[symbol] = position
        logger.info(f"Opened position: {symbol} @ {entry_price} x {quantity}")
        return position

    def close_position(
        self,
        symbol: str,
        exit_price: float,
        exit_reason: str = "manual",
    ) -> Dict:
        """Close an existing position.

        Args:
            symbol: Instrument symbol.
            exit_price: Simulated exit price.
            exit_reason: Why the position was closed.

        Returns:
            Dict with closed position details.

        Raises:
            ValueError: If no position exists.
        """
        symbol = symbol.upper()
        if not self.has_position(symbol):
            raise ValueError(f"No position exists for {symbol}")

        position = self._positions.pop(symbol)
        closed = {
            "symbol": symbol,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "quantity": position.quantity,
            "entry_time": position.entry_time,
            "exit_time": datetime.now(),
            "holding_minutes": position.holding_minutes,
            "signal_confidence": position.signal_confidence,
            "signal_reason": position.signal_reason,
            "exit_reason": exit_reason,
        }
        self._closed_positions.append(closed)
        logger.info(f"Closed position: {symbol} @ {exit_price}, reason={exit_reason}")
        return closed

    def get_positions_for_time_exit(self, max_minutes: float) -> List[str]:
        """Get symbols that have exceeded holding time.

        Args:
            max_minutes: Maximum holding time in minutes.

        Returns:
            List of symbols to exit.
        """
        symbols_to_exit = []
        for symbol, position in self._positions.items():
            if position.holding_minutes >= max_minutes:
                symbols_to_exit.append(symbol)
        return symbols_to_exit

    @property
    def open_positions(self) -> Dict[str, Position]:
        return self._positions.copy()

    @property
    def closed_positions(self) -> List[Dict]:
        return self._closed_positions.copy()
