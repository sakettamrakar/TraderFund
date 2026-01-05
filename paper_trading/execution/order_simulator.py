"""
##############################################################################
## PAPER TRADING ONLY - NO REAL ORDERS
##############################################################################
Order Simulator

Simulates market order fills with configurable slippage.
NO REAL BROKER SDK IMPORTS.
##############################################################################
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import random


@dataclass
class SimulatedFill:
    """Result of a simulated order execution."""
    symbol: str
    side: str  # "BUY" or "SELL"
    requested_price: float
    fill_price: float
    slippage: float
    quantity: int
    timestamp: datetime

    @property
    def slippage_pct(self) -> float:
        if self.requested_price == 0:
            return 0.0
        return ((self.fill_price - self.requested_price) / self.requested_price) * 100


def simulate_market_order(
    symbol: str,
    side: str,
    price: float,
    quantity: int,
    slippage_pct: float = 0.0,
    randomize_slippage: bool = False,
) -> SimulatedFill:
    """Simulate a market order fill.

    Args:
        symbol: Instrument symbol.
        side: "BUY" or "SELL".
        price: Requested price (e.g., LTP or next candle open).
        quantity: Number of shares.
        slippage_pct: Slippage percentage (0-100 scale).
        randomize_slippage: If True, randomize slippage between 0 and slippage_pct.

    Returns:
        SimulatedFill with fill details.
    """
    if slippage_pct < 0:
        slippage_pct = 0

    actual_slippage_pct = slippage_pct
    if randomize_slippage and slippage_pct > 0:
        actual_slippage_pct = random.uniform(0, slippage_pct)

    # Calculate slippage amount
    slippage_amount = price * (actual_slippage_pct / 100)

    # Apply slippage: adverse for the trader
    if side.upper() == "BUY":
        fill_price = price + slippage_amount  # Pay more
    else:
        fill_price = price - slippage_amount  # Receive less

    return SimulatedFill(
        symbol=symbol,
        side=side.upper(),
        requested_price=price,
        fill_price=round(fill_price, 2),
        slippage=round(slippage_amount, 2),
        quantity=quantity,
        timestamp=datetime.now(),
    )


def simulate_entry(
    symbol: str,
    price: float,
    quantity: int,
    slippage_pct: float = 0.0,
) -> SimulatedFill:
    """Simulate a BUY entry."""
    return simulate_market_order(symbol, "BUY", price, quantity, slippage_pct)


def simulate_exit(
    symbol: str,
    price: float,
    quantity: int,
    slippage_pct: float = 0.0,
) -> SimulatedFill:
    """Simulate a SELL exit."""
    return simulate_market_order(symbol, "SELL", price, quantity, slippage_pct)
