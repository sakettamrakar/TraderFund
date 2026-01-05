"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Context Runner

Orchestrates volatility and context calculations to produce a ContextSnapshot.
##############################################################################
"""

import logging
from datetime import datetime, date
from typing import Optional

import pandas as pd

from .context_snapshot import ContextSnapshot, VolatilityMetrics, RegimeLabels
from .calculators.atr import calculate_atr
from .calculators.daily_range import (
    calculate_daily_range,
    calculate_daily_range_pct,
    calculate_avg_range,
    calculate_range_expansion,
)
from .calculators.volatility_regime import (
    classify_volatility,
    classify_trend,
    classify_range_state,
    calculate_rolling_std,
)

logger = logging.getLogger(__name__)


class ContextRunner:
    """Orchestrates context analysis for a symbol.

    This runner produces OBSERVATIONS, not RECOMMENDATIONS.
    Outputs should be used for research analysis only.
    """

    def __init__(
        self,
        atr_period: int = 14,
        lookback_period: int = 20,
    ):
        """Initialize the runner.

        Args:
            atr_period: Period for ATR calculation.
            lookback_period: Period for historical comparisons.
        """
        self.atr_period = atr_period
        self.lookback_period = lookback_period

    def analyze(
        self,
        df: pd.DataFrame,
        symbol: str,
        high_col: str = "high",
        low_col: str = "low",
        close_col: str = "close",
        notes: Optional[str] = None,
    ) -> ContextSnapshot:
        """Analyze market context for a symbol.

        Args:
            df: DataFrame with OHLC data (must be sorted by date).
            symbol: Instrument symbol.
            high_col: Column name for high prices.
            low_col: Column name for low prices.
            close_col: Column name for close prices.
            notes: Optional analyst notes.

        Returns:
            ContextSnapshot with volatility metrics and regime labels.
        """
        if df.empty:
            raise ValueError("Cannot analyze empty DataFrame")

        # Ensure sorted
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp")
        elif "date" in df.columns:
            df = df.sort_values("date")

        # Get latest values
        latest = df.iloc[-1]
        latest_high = float(latest[high_col])
        latest_low = float(latest[low_col])
        latest_close = float(latest[close_col])

        # Calculate ATR
        atr_series = calculate_atr(df, period=self.atr_period, high_col=high_col, low_col=low_col, close_col=close_col)
        current_atr = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0
        atr_pct = (current_atr / latest_close * 100) if latest_close > 0 else 0.0

        # Calculate daily range
        daily_range = calculate_daily_range(latest_high, latest_low)
        daily_range_pct = calculate_daily_range_pct(latest_high, latest_low, latest_close)

        # Calculate rolling std
        rolling_std = calculate_rolling_std(df[close_col], period=self.lookback_period)
        current_std = float(rolling_std.iloc[-1]) if not rolling_std.empty and pd.notna(rolling_std.iloc[-1]) else None

        # Calculate range expansion
        avg_range = calculate_avg_range(df, period=self.lookback_period, high_col=high_col, low_col=low_col)
        current_avg_range = float(avg_range.iloc[-1]) if not avg_range.empty and pd.notna(avg_range.iloc[-1]) else 1.0
        range_expansion = calculate_range_expansion(daily_range, current_avg_range)

        # Classify volatility
        historical_atr = atr_series.tail(self.lookback_period * 2)
        atr_mean = float(historical_atr.mean()) if not historical_atr.empty else current_atr
        atr_std = float(historical_atr.std()) if not historical_atr.empty else 0.0
        volatility_label = classify_volatility(current_atr, atr_mean, atr_std)

        # Classify trend
        trend_label = classify_trend(df[close_col], lookback=self.lookback_period)

        # Classify range state
        range_label = classify_range_state(daily_range, current_avg_range)

        # Build snapshot
        volatility_metrics = VolatilityMetrics(
            atr=current_atr,
            atr_pct=atr_pct,
            daily_range=daily_range,
            daily_range_pct=daily_range_pct,
            rolling_std_20d=current_std,
            range_expansion_ratio=range_expansion,
        )

        regime_labels = RegimeLabels(
            volatility=volatility_label,
            trend=trend_label,
            range_state=range_label,
        )

        # Determine snapshot date
        if "timestamp" in df.columns:
            snapshot_date = pd.to_datetime(latest["timestamp"]).date()
        elif "date" in df.columns:
            snapshot_date = pd.to_datetime(latest["date"]).date()
        else:
            snapshot_date = date.today()

        return ContextSnapshot(
            symbol=symbol,
            snapshot_date=snapshot_date,
            snapshot_time=datetime.now(),
            volatility_metrics=volatility_metrics,
            regime_labels=regime_labels,
            data_lookback_days=self.lookback_period,
            notes=notes,
        )

    def print_snapshot(self, snapshot: ContextSnapshot) -> None:
        """Print a formatted snapshot to stdout."""
        print("\n" + "=" * 60)
        print("## RESEARCH CONTEXT SNAPSHOT ##")
        print("=" * 60)
        print(f"Symbol: {snapshot.symbol}")
        print(f"Date: {snapshot.snapshot_date}")
        print("-" * 60)
        print("VOLATILITY METRICS:")
        print(f"  ATR: {snapshot.volatility_metrics.atr:.4f}")
        print(f"  ATR %: {snapshot.volatility_metrics.atr_pct:.2f}%")
        print(f"  Daily Range: {snapshot.volatility_metrics.daily_range:.4f}")
        print(f"  Daily Range %: {snapshot.volatility_metrics.daily_range_pct:.2f}%")
        if snapshot.volatility_metrics.range_expansion_ratio:
            print(f"  Range Expansion: {snapshot.volatility_metrics.range_expansion_ratio:.2f}x")
        print("-" * 60)
        print("REGIME LABELS:")
        print(f"  Volatility: {snapshot.regime_labels.volatility}")
        print(f"  Trend: {snapshot.regime_labels.trend}")
        print(f"  Range State: {snapshot.regime_labels.range_state}")
        print("=" * 60)
        print("⚠️  These labels are OBSERVATIONS, not trade recommendations.")
        print("=" * 60 + "\n")
