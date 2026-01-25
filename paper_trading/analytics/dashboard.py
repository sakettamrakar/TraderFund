"""
##############################################################################
## PAPER TRADING ANALYTICS - READ ONLY
##############################################################################
Dashboard

Manager-style one-screen summary for paper trading review.
DESCRIPTIVE ONLY - no recommendations.
##############################################################################
"""

import pandas as pd
from dataclasses import dataclass
from typing import List, Optional

from .metrics import calculate_execution_metrics, calculate_performance_metrics
from .aggregations import aggregate_by_confidence, aggregate_by_time_of_day


@dataclass
class DashboardSummary:
    """One-screen dashboard summary."""
    session_summary: str
    positives: List[str]
    issues: List[str]
    observations: List[str]


def generate_summary(df: pd.DataFrame) -> DashboardSummary:
    """Generate a manager-style summary from trade data.

    Args:
        df: Trade DataFrame.

    Returns:
        DashboardSummary with insights.
    """
    if df.empty:
        return DashboardSummary(
            session_summary="No trades to analyze.",
            positives=[],
            issues=["No trade data available."],
            observations=[],
        )

    exec_metrics = calculate_execution_metrics(df)
    perf_metrics = calculate_performance_metrics(df)
    conf_buckets = aggregate_by_confidence(df)
    time_buckets = aggregate_by_time_of_day(df)

    # Build session summary
    session_summary = (
        f"Analyzed {exec_metrics.total_trades} trades across {exec_metrics.total_symbols} symbols. "
        f"Win rate: {perf_metrics.win_rate}%. Total P&L: {perf_metrics.total_pnl:+.2f}"
    )

    positives = []
    issues = []
    observations = []

    # Identify positives
    if perf_metrics.win_rate >= 50:
        positives.append(f"Win rate above 50%: {perf_metrics.win_rate}%")

    if perf_metrics.expectancy > 0:
        positives.append(f"Positive expectancy: {perf_metrics.expectancy:.2f}")

    if perf_metrics.profit_factor > 1.5:
        positives.append(f"Profit factor above 1.5: {perf_metrics.profit_factor:.2f}")

    # Check high confidence performance
    for bucket in conf_buckets:
        if "High" in bucket.bucket and bucket.win_rate > 60:
            positives.append(f"High confidence trades win at {bucket.win_rate}%")

    # Identify issues
    if perf_metrics.win_rate < 40:
        issues.append(f"Win rate below 40%: {perf_metrics.win_rate}%")

    if perf_metrics.expectancy < 0:
        issues.append(f"Negative expectancy: {perf_metrics.expectancy:.2f}")

    if perf_metrics.max_drawdown > abs(perf_metrics.total_pnl) * 0.5:
        issues.append(f"Max drawdown significant: {perf_metrics.max_drawdown:.2f}")

    # Check low confidence performance
    for bucket in conf_buckets:
        if "Low" in bucket.bucket and bucket.trade_count > 5:
            if bucket.win_rate > 50:
                issues.append(f"Low confidence trades shouldn't win often ({bucket.win_rate}%)")

    # Neutral observations
    observations.append(f"Average holding time: {exec_metrics.avg_holding_minutes:.1f} minutes")
    observations.append(f"Most traded: {exec_metrics.most_traded_symbol} ({exec_metrics.most_traded_count} trades)")

    for bucket in time_buckets:
        if bucket.trade_count >= 3:
            observations.append(f"{bucket.bucket}: {bucket.trade_count} trades, {bucket.win_rate}% wins")

    # Limit to top 3 each
    return DashboardSummary(
        session_summary=session_summary,
        positives=positives[:3],
        issues=issues[:3],
        observations=observations[:3],
    )


def print_dashboard(df: pd.DataFrame) -> None:
    """Print the dashboard to console."""
    summary = generate_summary(df)

    print("\n" + "=" * 70)
    print("## PAPER TRADING ANALYTICS DASHBOARD ##")
    print("=" * 70)
    print(f"\n{summary.session_summary}\n")

    print("-" * 70)
    print("✅ POSITIVES")
    if summary.positives:
        for p in summary.positives:
            print(f"   • {p}")
    else:
        print("   (None identified)")

    print("-" * 70)
    print("⚠️  ISSUES")
    if summary.issues:
        for i in summary.issues:
            print(f"   • {i}")
    else:
        print("   (None identified)")

    print("-" * 70)
    print("📊 OBSERVATIONS")
    if summary.observations:
        for o in summary.observations:
            print(f"   • {o}")
    else:
        print("   (None)")

    print("=" * 70)
    print("⚠️  This is PAPER data. Do NOT assume real performance.")
    print("=" * 70 + "\n")
