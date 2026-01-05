"""
##############################################################################
## PAPER TRADING ANALYTICS - READ ONLY
##############################################################################
Aggregations

Signal quality and time-based aggregations.
DESCRIPTIVE ONLY - no recommendations.
##############################################################################
"""

import pandas as pd
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ConfidenceBucket:
    """Metrics for a confidence bucket."""
    bucket: str
    trade_count: int
    win_rate: float
    avg_pnl: float
    total_pnl: float


@dataclass
class TimeBucket:
    """Metrics for a time bucket."""
    bucket: str
    trade_count: int
    win_rate: float
    avg_pnl: float


def aggregate_by_confidence(df: pd.DataFrame) -> List[ConfidenceBucket]:
    """Aggregate performance by signal confidence bucket.

    Buckets: Low (0-0.3), Medium (0.3-0.6), High (0.6-1.0)

    Args:
        df: Trade DataFrame with signal_confidence column.

    Returns:
        List of ConfidenceBucket results.
    """
    if df.empty or "signal_confidence" not in df.columns:
        return []

    # Define buckets
    def bucket_label(conf):
        if conf < 0.3:
            return "Low (0-0.3)"
        elif conf < 0.6:
            return "Medium (0.3-0.6)"
        else:
            return "High (0.6-1.0)"

    df = df.copy()
    df["conf_bucket"] = df["signal_confidence"].apply(bucket_label)

    results = []
    for bucket in ["Low (0-0.3)", "Medium (0.3-0.6)", "High (0.6-1.0)"]:
        bucket_df = df[df["conf_bucket"] == bucket]
        if len(bucket_df) == 0:
            continue

        winners = bucket_df[bucket_df["net_pnl"] > 0]
        win_rate = len(winners) / len(bucket_df) * 100

        results.append(ConfidenceBucket(
            bucket=bucket,
            trade_count=len(bucket_df),
            win_rate=round(win_rate, 1),
            avg_pnl=round(bucket_df["net_pnl"].mean(), 2),
            total_pnl=round(bucket_df["net_pnl"].sum(), 2),
        ))

    return results


def aggregate_by_time_of_day(df: pd.DataFrame) -> List[TimeBucket]:
    """Aggregate performance by time of day.

    Buckets: Morning (9-11), Midday (11-14), Afternoon (14-16)

    Args:
        df: Trade DataFrame with timestamp column.

    Returns:
        List of TimeBucket results.
    """
    if df.empty or "timestamp" not in df.columns:
        return []

    df = df.copy()
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour

    def time_bucket(hour):
        if 9 <= hour < 11:
            return "Morning (9-11)"
        elif 11 <= hour < 14:
            return "Midday (11-14)"
        elif 14 <= hour < 16:
            return "Afternoon (14-16)"
        else:
            return "Other"

    df["time_bucket"] = df["hour"].apply(time_bucket)

    results = []
    for bucket in ["Morning (9-11)", "Midday (11-14)", "Afternoon (14-16)", "Other"]:
        bucket_df = df[df["time_bucket"] == bucket]
        if len(bucket_df) == 0:
            continue

        winners = bucket_df[bucket_df["net_pnl"] > 0]
        win_rate = len(winners) / len(bucket_df) * 100 if len(bucket_df) > 0 else 0

        results.append(TimeBucket(
            bucket=bucket,
            trade_count=len(bucket_df),
            win_rate=round(win_rate, 1),
            avg_pnl=round(bucket_df["net_pnl"].mean(), 2),
        ))

    return results


def aggregate_by_signal_reason(df: pd.DataFrame) -> Dict[str, Dict]:
    """Aggregate performance by signal reason.

    Args:
        df: Trade DataFrame with signal_reason column.

    Returns:
        Dict mapping reason to metrics.
    """
    if df.empty or "signal_reason" not in df.columns:
        return {}

    results = {}
    for reason in df["signal_reason"].unique():
        reason_df = df[df["signal_reason"] == reason]
        winners = reason_df[reason_df["net_pnl"] > 0]
        win_rate = len(winners) / len(reason_df) * 100 if len(reason_df) > 0 else 0

        results[reason] = {
            "trade_count": len(reason_df),
            "win_rate": round(win_rate, 1),
            "avg_pnl": round(reason_df["net_pnl"].mean(), 2),
            "total_pnl": round(reason_df["net_pnl"].sum(), 2),
        }

    return results
