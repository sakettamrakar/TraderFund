"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Risk Simulator

Orchestrates risk calculations to produce RiskSnapshots.
This is a SIMULATION tool, not a live trading system.
##############################################################################
"""

import logging
from datetime import datetime
from typing import Optional

from .risk_snapshot import RiskSnapshot
from .models.fixed_risk import calculate_position_size, calculate_risk_amount
from .models.atr_based import calculate_atr_stop, calculate_position_from_atr
from .models.percent_equity import calculate_max_shares
from .risk_metrics import calculate_worst_case_loss, calculate_capital_at_risk

logger = logging.getLogger(__name__)


class RiskSimulator:
    """Orchestrates risk simulations.

    This simulator produces RESEARCH-ONLY snapshots.
    Outputs must NOT be used for live trading without governance approval.
    """

    def __init__(self, capital: float, default_risk_pct: float = 1.0):
        """Initialize the simulator.

        Args:
            capital: Total available capital for simulations.
            default_risk_pct: Default risk percentage per trade (0-100).
        """
        self.capital = capital
        self.default_risk_pct = default_risk_pct

    def simulate_fixed_risk(
        self,
        symbol: str,
        entry_price: float,
        stop_price: float,
        risk_pct: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> RiskSnapshot:
        """Simulate position sizing using fixed fractional risk.

        Args:
            symbol: Instrument symbol.
            entry_price: Planned entry price.
            stop_price: Planned stop-loss price.
            risk_pct: Risk percentage (uses default if not provided).
            notes: Optional notes.

        Returns:
            RiskSnapshot with simulated position.
        """
        risk_pct = risk_pct or self.default_risk_pct

        position_size = calculate_position_size(
            capital=self.capital,
            risk_pct=risk_pct,
            entry_price=entry_price,
            stop_price=stop_price,
        )

        max_loss = calculate_worst_case_loss(position_size, entry_price, stop_price)
        actual_risk_pct = calculate_capital_at_risk(
            position_size, entry_price, stop_price, self.capital
        )

        return RiskSnapshot(
            symbol=symbol,
            entry_price=entry_price,
            stop_price=stop_price,
            position_size=position_size,
            max_loss=max_loss,
            risk_pct=actual_risk_pct,
            model_used="fixed_fractional",
            notes=notes,
        )

    def simulate_atr_risk(
        self,
        symbol: str,
        entry_price: float,
        atr: float,
        atr_multiplier: float = 2.0,
        risk_pct: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> RiskSnapshot:
        """Simulate position sizing using ATR-based stop.

        Args:
            symbol: Instrument symbol.
            entry_price: Planned entry price.
            atr: Current ATR value.
            atr_multiplier: ATR multiplier for stop distance.
            risk_pct: Risk percentage.
            notes: Optional notes.

        Returns:
            RiskSnapshot with simulated position.
        """
        risk_pct = risk_pct or self.default_risk_pct

        stop_price = calculate_atr_stop(
            entry_price=entry_price,
            atr=atr,
            multiplier=atr_multiplier,
            direction="LONG",
        )

        position_size = calculate_position_from_atr(
            capital=self.capital,
            risk_pct=risk_pct,
            entry_price=entry_price,
            atr=atr,
            multiplier=atr_multiplier,
        )

        max_loss = calculate_worst_case_loss(position_size, entry_price, stop_price)
        actual_risk_pct = calculate_capital_at_risk(
            position_size, entry_price, stop_price, self.capital
        )

        return RiskSnapshot(
            symbol=symbol,
            entry_price=entry_price,
            stop_price=stop_price,
            position_size=position_size,
            max_loss=max_loss,
            risk_pct=actual_risk_pct,
            model_used="atr_based",
            notes=f"ATR={atr}, Mult={atr_multiplier}. {notes or ''}".strip(),
        )

    def print_snapshot(self, snapshot: RiskSnapshot) -> None:
        """Print a formatted snapshot to stdout."""
        print("\n" + "=" * 60)
        print("## RESEARCH RISK SIMULATION ##")
        print("=" * 60)
        print(f"Symbol: {snapshot.symbol}")
        print(f"Model: {snapshot.model_used}")
        print("-" * 60)
        print("TRADE PARAMETERS (SIMULATED):")
        print(f"  Entry Price: {snapshot.entry_price:.2f}")
        print(f"  Stop Price: {snapshot.stop_price:.2f}")
        print(f"  Stop Distance: {abs(snapshot.entry_price - snapshot.stop_price):.2f}")
        print("-" * 60)
        print("POSITION SIZING (SIMULATED):")
        print(f"  Position Size: {snapshot.position_size} shares")
        print(f"  Position Value: {snapshot.position_size * snapshot.entry_price:,.2f}")
        print("-" * 60)
        print("RISK ANALYSIS:")
        print(f"  Max Loss: {snapshot.max_loss:,.2f}")
        print(f"  Capital at Risk: {snapshot.risk_pct:.2f}%")
        print("=" * 60)
        print("⚠️  This is a SIMULATION. Do NOT use for live trading.")
        print("=" * 60 + "\n")
