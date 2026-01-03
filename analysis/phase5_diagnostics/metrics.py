"""Phase 5 Diagnostics: Core Metrics.

Computes signal quality metrics from Phase-4 observation logs.
"""

import logging
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SignalMetrics:
    """Computes core metrics for signal quality analysis."""

    def __init__(self, df: pd.DataFrame):
        """Initialize with loaded signal log DataFrame."""
        self.df = df

    def total_signals(self) -> int:
        """Total number of signals."""
        return len(self.df)

    def ab_ratio(self) -> float:
        """Ratio of A/B signals to total classified signals.

        Returns:
            Ratio (0.0 to 1.0) or NaN if no data.
        """
        classified = self.df[self.df["classification"].isin(["A", "B", "C", "D"])]
        if classified.empty:
            return float("nan")
        ab_count = classified["classification"].isin(["A", "B"]).sum()
        return ab_count / len(classified)

    def cd_ratio(self) -> float:
        """Ratio of C/D signals to total classified signals."""
        return 1.0 - self.ab_ratio()

    def frequency_by_day(self) -> pd.Series:
        """Signal count per calendar day."""
        if "timestamp" not in self.df.columns or self.df["timestamp"].isna().all():
            return pd.Series(dtype=int)
        return self.df.groupby(self.df["timestamp"].dt.date).size()

    def frequency_by_symbol(self) -> pd.Series:
        """Signal count per symbol."""
        return self.df["symbol"].value_counts()

    def confidence_by_class(self) -> pd.Series:
        """Average confidence grouped by classification."""
        return self.df.groupby("classification")["confidence"].mean()

    def signal_density_by_hour(self) -> pd.Series:
        """Signal count grouped by hour of the day."""
        if "timestamp" not in self.df.columns or self.df["timestamp"].isna().all():
            return pd.Series(dtype=int)
        return self.df.groupby(self.df["timestamp"].dt.hour).size()

    def summary(self) -> Dict[str, Any]:
        """Generate a summary dictionary of all metrics."""
        return {
            "total_signals": self.total_signals(),
            "ab_ratio": round(self.ab_ratio(), 3) if not pd.isna(self.ab_ratio()) else None,
            "cd_ratio": round(self.cd_ratio(), 3) if not pd.isna(self.cd_ratio()) else None,
            "frequency_by_day": self.frequency_by_day().to_dict(),
            "frequency_by_symbol": self.frequency_by_symbol().to_dict(),
            "confidence_by_class": self.confidence_by_class().to_dict(),
            "signal_density_by_hour": self.signal_density_by_hour().to_dict(),
        }
