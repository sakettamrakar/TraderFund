"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Daily Range Calculator

Pure calculation functions for daily range metrics. No thresholds, no trade rules.
##############################################################################
"""

import pandas as pd
import numpy as np
from typing import Union


def calculate_daily_range(high: float, low: float) -> float:
    """Calculate absolute daily range.

    Args:
        high: High price of the day.
        low: Low price of the day.

    Returns:
        Absolute range (high - low).
    """
    return high - low


def calculate_daily_range_pct(high: float, low: float, reference: float) -> float:
    """Calculate daily range as a percentage of reference price.

    Args:
        high: High price of the day.
        low: Low price of the day.
        reference: Reference price (typically close or open).

    Returns:
        Range as percentage (0-100 scale).
    """
    if reference == 0:
        return 0.0
    return ((high - low) / reference) * 100


def calculate_range_expansion(current_range: float, avg_range: float) -> float:
    """Calculate range expansion ratio.

    Values > 1.0 indicate range expansion (current > average).
    Values < 1.0 indicate range contraction (current < average).

    Args:
        current_range: Current period's range.
        avg_range: Historical average range.

    Returns:
        Expansion ratio.
    """
    if avg_range == 0:
        return 0.0
    return current_range / avg_range


def calculate_range_series(
    df: pd.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
) -> pd.Series:
    """Calculate range for each row in a DataFrame.

    Args:
        df: DataFrame with high/low columns.
        high_col: Column name for high prices.
        low_col: Column name for low prices.

    Returns:
        Series of range values.
    """
    return df[high_col] - df[low_col]


def calculate_range_pct_series(
    df: pd.DataFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    """Calculate range percentage for each row.

    Args:
        df: DataFrame with OHLC data.
        high_col: Column name for high prices.
        low_col: Column name for low prices.
        close_col: Column name for close prices (reference).

    Returns:
        Series of range percentage values.
    """
    if df.empty:
        return pd.Series(dtype=float)

    ranges = df[high_col] - df[low_col]
    return (ranges / df[close_col]) * 100


def calculate_avg_range(
    df: pd.DataFrame,
    period: int = 20,
    high_col: str = "high",
    low_col: str = "low",
) -> pd.Series:
    """Calculate rolling average range.

    Args:
        df: DataFrame with high/low columns.
        period: Lookback period.
        high_col: Column name for high prices.
        low_col: Column name for low prices.

    Returns:
        Series of average range values.
    """
    ranges = df[high_col] - df[low_col]
    return ranges.rolling(window=period).mean()
