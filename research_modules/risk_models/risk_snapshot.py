"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Risk Snapshot

Read-only data container for simulated risk analysis.
This is a SIMULATION result, not a live trading instruction.
##############################################################################
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class RiskSnapshot:
    """Simulated risk analysis snapshot.

    This is a READ-ONLY container for risk simulation results.
    It does NOT represent a live order or trading instruction.

    IMPORTANT: This snapshot must NEVER be used to place live trades
    without completing the full governance activation process.
    """
    symbol: str
    entry_price: float
    stop_price: float
    position_size: int
    max_loss: float
    risk_pct: float
    r_multiple_target: Optional[float] = None
    target_price: Optional[float] = None
    model_used: str = "unknown"
    snapshot_time: datetime = None
    notes: Optional[str] = None

    def __post_init__(self):
        # Set snapshot_time if not provided (workaround for frozen dataclass)
        if self.snapshot_time is None:
            object.__setattr__(self, 'snapshot_time', datetime.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "symbol": self.symbol,
            "entry_price": self.entry_price,
            "stop_price": self.stop_price,
            "position_size": self.position_size,
            "max_loss": self.max_loss,
            "risk_pct": self.risk_pct,
            "r_multiple_target": self.r_multiple_target,
            "target_price": self.target_price,
            "model_used": self.model_used,
            "snapshot_time": self.snapshot_time.isoformat() if self.snapshot_time else None,
            "notes": self.notes,
        }

    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"RiskSnapshot({self.symbol})\n"
            f"  Entry: {self.entry_price:.2f}, Stop: {self.stop_price:.2f}\n"
            f"  Position: {self.position_size} shares\n"
            f"  Max Loss: {self.max_loss:.2f} ({self.risk_pct:.2f}%)\n"
            f"  Model: {self.model_used}"
        )


@dataclass(frozen=True)
class PortfolioRiskSnapshot:
    """Aggregate risk snapshot for a portfolio of positions."""
    total_positions: int
    total_capital_at_risk: float
    total_capital_at_risk_pct: float
    max_single_position_risk: float
    avg_position_risk: float
    snapshot_time: datetime = None

    def __post_init__(self):
        if self.snapshot_time is None:
            object.__setattr__(self, 'snapshot_time', datetime.now())
