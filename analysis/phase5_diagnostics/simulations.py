"""Phase 5 Diagnostics: What-If Simulations.

Runs analytical simulations on Phase-4 logs to evaluate hypothetical filters.
DOES NOT modify strategy parameters. Outputs trade-offs only.
"""

import logging
import pandas as pd
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class WhatIfSimulator:
    """Runs virtual filter simulations on signal logs."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def _compute_ab_ratio(self, subset: pd.DataFrame) -> float:
        """Compute A/B ratio for a subset."""
        classified = subset[subset["classification"].isin(["A", "B", "C", "D"])]
        if classified.empty:
            return float("nan")
        ab_count = classified["classification"].isin(["A", "B"]).sum()
        return ab_count / len(classified)

    def simulate_ignore_first_n_minutes(self, n_minutes: int = 15) -> Dict[str, Any]:
        """Simulate ignoring signals in the first N minutes of market open.

        Args:
            n_minutes: Minutes after 9:00 AM to ignore.

        Returns:
            Simulation results.
        """
        if "timestamp" not in self.df.columns or self.df["timestamp"].isna().all():
            return {"error": "No valid timestamps"}

        cutoff_hour = 9
        cutoff_minute = n_minutes

        filtered = self.df[
            (self.df["timestamp"].dt.hour > cutoff_hour) |
            ((self.df["timestamp"].dt.hour == cutoff_hour) & (self.df["timestamp"].dt.minute >= cutoff_minute))
        ]

        original_count = len(self.df)
        remaining_count = len(filtered)
        filtered_out_pct = (original_count - remaining_count) / original_count * 100 if original_count > 0 else 0

        return {
            "filter": f"Ignore first {n_minutes} minutes",
            "original_count": original_count,
            "remaining_count": remaining_count,
            "filtered_out_pct": round(filtered_out_pct, 1),
            "original_ab_ratio": round(self._compute_ab_ratio(self.df), 3),
            "new_ab_ratio": round(self._compute_ab_ratio(filtered), 3),
        }

    def simulate_raise_confidence_threshold(self, min_confidence: float = 0.7) -> Dict[str, Any]:
        """Simulate raising the minimum confidence threshold.

        Args:
            min_confidence: Minimum confidence required.

        Returns:
            Simulation results.
        """
        filtered = self.df[self.df["confidence"] >= min_confidence]

        original_count = len(self.df)
        remaining_count = len(filtered)
        filtered_out_pct = (original_count - remaining_count) / original_count * 100 if original_count > 0 else 0

        return {
            "filter": f"Confidence >= {min_confidence}",
            "original_count": original_count,
            "remaining_count": remaining_count,
            "filtered_out_pct": round(filtered_out_pct, 1),
            "original_ab_ratio": round(self._compute_ab_ratio(self.df), 3),
            "new_ab_ratio": round(self._compute_ab_ratio(filtered), 3),
        }

    def simulate_exclude_symbol(self, symbol: str) -> Dict[str, Any]:
        """Simulate excluding a specific symbol.

        Args:
            symbol: Symbol to exclude.

        Returns:
            Simulation results.
        """
        filtered = self.df[self.df["symbol"] != symbol]

        original_count = len(self.df)
        remaining_count = len(filtered)
        filtered_out_pct = (original_count - remaining_count) / original_count * 100 if original_count > 0 else 0

        return {
            "filter": f"Exclude {symbol}",
            "original_count": original_count,
            "remaining_count": remaining_count,
            "filtered_out_pct": round(filtered_out_pct, 1),
            "original_ab_ratio": round(self._compute_ab_ratio(self.df), 3),
            "new_ab_ratio": round(self._compute_ab_ratio(filtered), 3),
        }

    def run_all_simulations(self) -> List[Dict[str, Any]]:
        """Run a standard set of simulations.

        Returns:
            List of simulation results.
        """
        results = []
        results.append(self.simulate_ignore_first_n_minutes(15))
        results.append(self.simulate_ignore_first_n_minutes(30))
        results.append(self.simulate_raise_confidence_threshold(0.6))
        results.append(self.simulate_raise_confidence_threshold(0.8))
        return results
