"""
Stage 1: Structural Capability - Evidence Providers

Individual evidence calculation functions.
Each function takes price DataFrame and returns a normalized score (0-1) or None if unavailable.
"""

import logging
from typing import Optional
import numpy as np
import pandas as pd

from . import config

logger = logging.getLogger(__name__)


# =============================================================================
# LONG-TERM BIAS EVIDENCE
# =============================================================================

def calculate_lt_trend_slope(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate long-term trend slope using linear regression.
    
    Returns:
        Normalized score 0-1 where:
        - 1.0 = strong positive slope
        - 0.5 = flat
        - 0.0 = strong negative slope
    """
    lookback = config.LOOKBACK["long_term"]
    if len(df) < lookback:
        return None
    
    prices = df["close"].tail(lookback).values
    x = np.arange(len(prices))
    
    # Linear regression
    slope, _ = np.polyfit(x, prices, 1)
    
    # Normalize: slope as % of mean price
    mean_price = np.mean(prices)
    slope_pct = (slope / mean_price) * 100  # Daily % change
    
    # Map to 0-1: -0.5% to +0.5% daily slope
    normalized = (slope_pct + 0.5) / 1.0
    return max(0.0, min(1.0, normalized))


def calculate_lt_position(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate price position relative to long-term moving average.
    
    Returns:
        Normalized score 0-1 where:
        - 1.0 = price way above MA
        - 0.5 = price at MA
        - 0.0 = price way below MA
    """
    lookback = config.LOOKBACK["long_term"]
    if len(df) < lookback:
        return None
    
    current_price = df["close"].iloc[-1]
    ma = df["close"].tail(lookback).mean()
    
    # Calculate position ratio
    ratio = current_price / ma
    
    # Map ratio (0.8 to 1.2) to (0 to 1)
    normalized = (ratio - 0.8) / 0.4
    return max(0.0, min(1.0, normalized))


def calculate_lt_stability(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate stability above long-term mean.
    
    Returns:
        Percentage of days price was above long-term mean (0-1).
    """
    lookback = config.LOOKBACK["long_term"]
    if len(df) < lookback:
        return None
    
    recent = df.tail(lookback)
    ma = recent["close"].mean()
    above_mean = (recent["close"] > ma).sum()
    
    return above_mean / lookback


# =============================================================================
# MEDIUM-TERM ALIGNMENT EVIDENCE
# =============================================================================

def calculate_mt_trend_slope(df: pd.DataFrame) -> Optional[float]:
    """Calculate medium-term trend slope."""
    lookback = config.LOOKBACK["medium_term"]
    if len(df) < lookback:
        return None
    
    prices = df["close"].tail(lookback).values
    x = np.arange(len(prices))
    
    slope, _ = np.polyfit(x, prices, 1)
    mean_price = np.mean(prices)
    slope_pct = (slope / mean_price) * 100
    
    # Map to 0-1: -1% to +1% daily slope for medium-term
    normalized = (slope_pct + 1.0) / 2.0
    return max(0.0, min(1.0, normalized))


def calculate_mt_lt_coherence(df: pd.DataFrame) -> Optional[float]:
    """
    Check if medium-term and long-term trends are coherent.
    
    Returns:
        1.0 = same direction, 0.5 = one flat, 0.0 = opposite
    """
    lt_lookback = config.LOOKBACK["long_term"]
    mt_lookback = config.LOOKBACK["medium_term"]
    
    if len(df) < lt_lookback:
        return None
    
    # Long-term direction
    lt_prices = df["close"].tail(lt_lookback).values
    lt_slope, _ = np.polyfit(np.arange(len(lt_prices)), lt_prices, 1)
    
    # Medium-term direction
    mt_prices = df["close"].tail(mt_lookback).values
    mt_slope, _ = np.polyfit(np.arange(len(mt_prices)), mt_prices, 1)
    
    # Both positive or both negative = coherent
    if (lt_slope > 0 and mt_slope > 0) or (lt_slope < 0 and mt_slope < 0):
        return 1.0
    elif abs(lt_slope) < 0.001 or abs(mt_slope) < 0.001:  # One is flat
        return 0.5
    else:
        return 0.0


def calculate_mt_channel_quality(df: pd.DataFrame) -> Optional[float]:
    """
    Measure tightness of recent price channel.
    
    Returns:
        1.0 = tight channel (low volatility), 0.0 = wide channel
    """
    lookback = config.LOOKBACK["medium_term"]
    if len(df) < lookback:
        return None
    
    recent = df.tail(lookback)
    high_range = recent["high"].max() - recent["low"].min()
    mean_price = recent["close"].mean()
    
    # Channel width as % of price
    channel_pct = (high_range / mean_price) * 100
    
    # Map: 0-20% channel to 1-0 score (tighter is better)
    normalized = 1.0 - (channel_pct / 20.0)
    return max(0.0, min(1.0, normalized))


# =============================================================================
# INSTITUTIONAL ACCEPTANCE EVIDENCE
# =============================================================================

def calculate_vwap_position(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate price position relative to VWAP.
    
    Returns:
        1.0 = above VWAP, 0.5 = at VWAP, 0.0 = below
    """
    lookback = config.LOOKBACK["medium_term"]
    if len(df) < lookback or "volume" not in df.columns:
        return None
    
    recent = df.tail(lookback)
    
    # Calculate VWAP
    typical_price = (recent["high"] + recent["low"] + recent["close"]) / 3
    vwap = (typical_price * recent["volume"]).sum() / recent["volume"].sum()
    
    current_price = df["close"].iloc[-1]
    ratio = current_price / vwap
    
    # Map (0.95 to 1.05) to (0 to 1)
    normalized = (ratio - 0.95) / 0.10
    return max(0.0, min(1.0, normalized))


def calculate_volume_trend(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate volume-weighted price trend.
    
    Returns:
        1.0 = volume increasing on up days
        0.0 = volume increasing on down days
    """
    lookback = config.LOOKBACK["medium_term"]
    if len(df) < lookback or "volume" not in df.columns:
        return None
    
    recent = df.tail(lookback).copy()
    recent["return"] = recent["close"].pct_change()
    recent = recent.dropna()
    
    # Volume on up days vs down days
    up_volume = recent[recent["return"] > 0]["volume"].sum()
    down_volume = recent[recent["return"] <= 0]["volume"].sum()
    
    total = up_volume + down_volume
    if total == 0:
        return 0.5
    
    return up_volume / total


def calculate_wick_ratio(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate lower wick vs upper wick ratio.
    
    Returns:
        1.0 = strong buying (lower wicks absorbed)
        0.0 = strong selling (upper wicks rejected)
    """
    lookback = config.LOOKBACK["medium_term"]
    if len(df) < lookback:
        return None
    
    recent = df.tail(lookback)
    
    # Lower wick = min(open, close) - low
    # Upper wick = high - max(open, close)
    lower_wicks = recent.apply(
        lambda r: min(r["open"], r["close"]) - r["low"], axis=1
    ).sum()
    
    upper_wicks = recent.apply(
        lambda r: r["high"] - max(r["open"], r["close"]), axis=1
    ).sum()
    
    total = lower_wicks + upper_wicks
    if total == 0:
        return 0.5
    
    # Higher lower wick ratio = more buying absorption
    return lower_wicks / total


# =============================================================================
# VOLATILITY SUITABILITY EVIDENCE
# =============================================================================

def calculate_atr_percentile(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate ATR percentile vs historical range.
    
    Returns:
        Score shaped like inverted U (mid-range volatility best)
    """
    lt_lookback = config.LOOKBACK["long_term"]
    mt_lookback = config.LOOKBACK["medium_term"]
    
    if len(df) < lt_lookback:
        return None
    
    # Calculate True Range
    df = df.copy()
    df["tr"] = df.apply(
        lambda r: max(
            r["high"] - r["low"],
            abs(r["high"] - r["close"]),
            abs(r["low"] - r["close"])
        ), axis=1
    )
    
    # Current ATR (medium-term)
    current_atr = df["tr"].tail(mt_lookback).mean()
    
    # Historical ATR range
    historical_atrs = df["tr"].rolling(mt_lookback).mean().dropna()
    
    if len(historical_atrs) == 0:
        return 0.5
    
    # Percentile
    percentile = (historical_atrs < current_atr).sum() / len(historical_atrs)
    
    # Inverted U: 0.5 percentile is best
    return 1.0 - abs(percentile - 0.5) * 2


def calculate_range_stability(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate coefficient of variation of daily ranges.
    
    Returns:
        1.0 = stable ranges, 0.0 = erratic ranges
    """
    lookback = config.LOOKBACK["medium_term"]
    if len(df) < lookback:
        return None
    
    recent = df.tail(lookback)
    ranges = recent["high"] - recent["low"]
    
    cv = ranges.std() / ranges.mean() if ranges.mean() > 0 else 0
    
    # Map CV (0-1) to (1-0) - lower CV = more stable
    normalized = 1.0 - min(cv, 1.0)
    return normalized


def calculate_gap_frequency(df: pd.DataFrame) -> Optional[float]:
    """
    Calculate frequency of gaps > 2%.
    
    Returns:
        1.0 = no gaps, 0.0 = frequent gaps
    """
    lookback = config.LOOKBACK["medium_term"]
    if len(df) < lookback:
        return None
    
    recent = df.tail(lookback)
    
    # Gap = (open - prev_close) / prev_close
    gaps = (recent["open"].iloc[1:].values - recent["close"].iloc[:-1].values) / recent["close"].iloc[:-1].values
    large_gaps = np.abs(gaps) > 0.02
    
    gap_rate = large_gaps.sum() / len(gaps) if len(gaps) > 0 else 0
    
    # Fewer gaps = better
    return 1.0 - min(gap_rate * 5, 1.0)  # Scale: 20% gaps = 0
