"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Average True Range (ATR) Calculator

Pure calculation functions for ATR. No thresholds, no trade rules.
##############################################################################
"""

from typing import Optional
import pandas as pd
import numpy as np


def calculate_true_range(
    high: float,
    low: float,
    prev_close: Optional[float] = None
) -> float:
    """Calculate True Range for a single candle.

    True Range = max(
        high - low,
        abs(high - prev_close),
        abs(low - prev_close)
    )

    Args:
        high: High price of current candle.
        low: Low price of current candle.
        prev_close: Close price of previous candle (optional for first candle).

    Returns:
        True Range value.
    """
    hl_range = high - low

    if prev_close is None:
        return hl_range

    hc_range = abs(high - prev_close)
    lc_range = abs(low - prev_close)

    return max(hl_range, hc_range, lc_range)


def calculate_atr(
    df: pd.DataFrame,
    period: int = 14,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    """Calculate Average True Range over a rolling period.

    Args:
        df: DataFrame with OHLC data.
        period: Lookback period for averaging (default: 14).
        high_col: Column name for high prices.
        low_col: Column name for low prices.
        close_col: Column name for close prices.

    Returns:
        Series of ATR values.
    """
    if df.empty:
        return pd.Series(dtype=float)

    high = df[high_col]
    low = df[low_col]
    close = df[close_col]
    prev_close = close.shift(1)

    # Calculate True Range
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calculate ATR as exponential moving average (Wilder's smoothing)
    atr = true_range.ewm(span=period, adjust=False).mean()

    return atr


def calculate_atr_simple(
    df: pd.DataFrame,
    period: int = 14,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    """Calculate ATR using simple moving average.

    Args:
        df: DataFrame with OHLC data.
        period: Lookback period for averaging.
        high_col: Column name for high prices.
        low_col: Column name for low prices.
        close_col: Column name for close prices.

    Returns:
        Series of ATR values (SMA-based).
    """
    if df.empty:
        return pd.Series(dtype=float)

    high = df[high_col]
    low = df[low_col]
    close = df[close_col]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return true_range.rolling(window=period).mean()
