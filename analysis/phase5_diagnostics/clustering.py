"""Phase 5 Diagnostics: Time-of-Day Clustering.

Groups signals into market session buckets and computes quality per bucket.
"""

import logging
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Define time buckets (IST)
TIME_BUCKETS = {
    "market_open": (9, 0, 9, 15),      # 9:00 - 9:15
    "momentum_window": (9, 15, 10, 30), # 9:15 - 10:30
    "midday": (10, 30, 13, 0),         # 10:30 - 13:00
    "afternoon": (13, 0, 14, 30),      # 13:00 - 14:30
    "closing_phase": (14, 30, 15, 30), # 14:30 - 15:30
}

class TimeOfDayClustering:
    """Analyzes signal quality by time-of-day buckets."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._assign_buckets()

    def _assign_buckets(self):
        """Assign each signal to a time bucket."""
        def get_bucket(ts):
            if pd.isna(ts):
                return "unknown"
            hour, minute = ts.hour, ts.minute
            time_val = hour * 60 + minute

            for name, (sh, sm, eh, em) in TIME_BUCKETS.items():
                start_val = sh * 60 + sm
                end_val = eh * 60 + em
                if start_val <= time_val < end_val:
                    return name
            return "outside_hours"

        if "timestamp" in self.df.columns:
            self.df["time_bucket"] = self.df["timestamp"].apply(get_bucket)
        else:
            self.df["time_bucket"] = "unknown"

    def bucket_summary(self) -> Dict[str, Dict[str, Any]]:
        """Compute summary stats for each time bucket.

        Returns:
            Dict mapping bucket name to stats (count, ab_ratio, avg_confidence).
        """
        results = {}
        for bucket in list(TIME_BUCKETS.keys()) + ["outside_hours", "unknown"]:
            bucket_df = self.df[self.df["time_bucket"] == bucket]
            if bucket_df.empty:
                continue

            classified = bucket_df[bucket_df["classification"].isin(["A", "B", "C", "D"])]
            ab_count = classified["classification"].isin(["A", "B"]).sum() if not classified.empty else 0
            total_classified = len(classified)

            results[bucket] = {
                "signal_count": len(bucket_df),
                "ab_ratio": round(ab_count / total_classified, 3) if total_classified > 0 else None,
                "avg_confidence": round(bucket_df["confidence"].mean(), 3) if not bucket_df["confidence"].isna().all() else None,
            }
        return results

    def failure_clusters(self) -> Dict[str, int]:
        """Identify where C/D signals cluster.

        Returns:
            Dict mapping time bucket to C/D count.
        """
        cd_df = self.df[self.df["classification"].isin(["C", "D"])]
        return cd_df["time_bucket"].value_counts().to_dict()
