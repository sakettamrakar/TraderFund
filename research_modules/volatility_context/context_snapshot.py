"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Context Snapshot

Read-only data container for market context analysis results.
This is an OBSERVATION, not a RECOMMENDATION.
##############################################################################
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any, Literal


@dataclass(frozen=True)
class VolatilityMetrics:
    """Container for volatility measurements."""
    atr: float
    atr_pct: float  # ATR as % of price
    daily_range: float
    daily_range_pct: float
    rolling_std_20d: Optional[float] = None
    range_expansion_ratio: Optional[float] = None


@dataclass(frozen=True)
class RegimeLabels:
    """Container for regime classifications.

    These are LABELS only, not trade recommendations.
    """
    volatility: Literal["LOW", "NORMAL", "HIGH"]
    trend: Literal["TRENDING", "RANGING", "UNCLEAR"]
    range_state: Literal["EXPANSION", "NORMAL", "COMPRESSION"]


@dataclass(frozen=True)
class ContextSnapshot:
    """Complete market context snapshot.

    This is a READ-ONLY observation of market conditions.
    It does NOT recommend any trading action.

    IMPORTANT: This snapshot must NEVER be auto-attached to signals.
    It is for research analysis only.

    Attributes:
        symbol: Instrument symbol.
        snapshot_date: Date of the snapshot.
        snapshot_time: Timestamp when snapshot was generated.
        volatility_metrics: Calculated volatility measurements.
        regime_labels: Classified market regime labels.
        data_lookback_days: Number of days of data used for calculations.
        notes: Optional analyst notes.
    """
    symbol: str
    snapshot_date: date
    snapshot_time: datetime
    volatility_metrics: VolatilityMetrics
    regime_labels: RegimeLabels
    data_lookback_days: int = 20
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary representation."""
        return {
            "symbol": self.symbol,
            "snapshot_date": self.snapshot_date.isoformat(),
            "snapshot_time": self.snapshot_time.isoformat(),
            "volatility_metrics": {
                "atr": self.volatility_metrics.atr,
                "atr_pct": self.volatility_metrics.atr_pct,
                "daily_range": self.volatility_metrics.daily_range,
                "daily_range_pct": self.volatility_metrics.daily_range_pct,
                "rolling_std_20d": self.volatility_metrics.rolling_std_20d,
                "range_expansion_ratio": self.volatility_metrics.range_expansion_ratio,
            },
            "regime_labels": {
                "volatility": self.regime_labels.volatility,
                "trend": self.regime_labels.trend,
                "range_state": self.regime_labels.range_state,
            },
            "data_lookback_days": self.data_lookback_days,
            "notes": self.notes,
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"ContextSnapshot({self.symbol} @ {self.snapshot_date})\n"
            f"  Volatility: {self.regime_labels.volatility} (ATR: {self.volatility_metrics.atr:.2f})\n"
            f"  Trend: {self.regime_labels.trend}\n"
            f"  Range: {self.regime_labels.range_state}"
        )
