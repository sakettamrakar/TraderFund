"""
Stage 2: Energy Setup - Evidence Providers

Energy-specific evidence calculations.
Each function returns normalized score (0-1) or None if unavailable.
"""

import logging
from typing import Optional
import numpy as np
import pandas as pd

from . import config

logger = logging.getLogger(__name__)


# =============================================================================
# VOLATILITY COMPRESSION EVIDENCE
# =============================================================================

def calculate_atr_compression(df: pd.DataFrame) -> Optional[float]:
    """
    Compare recent ATR to historical ATR.
    
    Returns:
        1.0 = highly compressed, 0.0 = expanded
    """
    short = config.LOOKBACK["short"]
    long = config.LOOKBACK["long"]
    
    if len(df) < long:
        return None
    
    # Calculate True Range
    df = df.copy()
    df["tr"] = df.apply(
        lambda r: max(r["high"] - r["low"], abs(r["high"] - r["close"]), abs(r["low"] - r["close"])),
        axis=1
    )
    
    recent_atr = df["tr"].tail(short).mean()
    historical_atr = df["tr"].tail(long).mean()
    
    if historical_atr == 0:
        return 0.5
    
    # Ratio < 1 = compression
    ratio = recent_atr / historical_atr
    
    # Invert: lower ratio = higher score
    score = max(0.0, min(1.0, 1.5 - ratio))
    return score


def calculate_range_squeeze(df: pd.DataFrame) -> Optional[float]:
    """
    Compare recent range to historical range.
    """
    short = config.LOOKBACK["short"]
    long = config.LOOKBACK["long"]
    
    if len(df) < long:
        return None
    
    recent_range = df.tail(short)["high"].max() - df.tail(short)["low"].min()
    historical_range = df.tail(long)["high"].max() - df.tail(long)["low"].min()
    
    if historical_range == 0:
        return 0.5
    
    ratio = recent_range / historical_range
    score = max(0.0, min(1.0, 1.0 - ratio))
    return score


def calculate_return_tightness(df: pd.DataFrame) -> Optional[float]:
    """
    Measure tightness of recent daily returns.
    """
    short = config.LOOKBACK["short"]
    long = config.LOOKBACK["long"]
    
    if len(df) < long:
        return None
    
    returns = df["close"].pct_change().dropna()
    
    recent_std = returns.tail(short).std()
    historical_std = returns.tail(long).std()
    
    if historical_std == 0:
        return 0.5
    
    ratio = recent_std / historical_std
    score = max(0.0, min(1.0, 1.5 - ratio))
    return score


# =============================================================================
# RANGE BALANCE EVIDENCE
# =============================================================================

def calculate_range_containment(df: pd.DataFrame) -> Optional[float]:
    """
    Measure how well price stays within its range.
    """
    medium = config.LOOKBACK["medium"]
    
    if len(df) < medium:
        return None
    
    recent = df.tail(medium)
    range_high = recent["high"].max()
    range_low = recent["low"].min()
    range_mid = (range_high + range_low) / 2
    range_span = range_high - range_low
    
    if range_span == 0:
        return 0.5
    
    # How close is current price to midpoint?
    current = df["close"].iloc[-1]
    deviation = abs(current - range_mid) / (range_span / 2)
    
    score = max(0.0, min(1.0, 1.0 - deviation))
    return score


def calculate_rejection_symmetry(df: pd.DataFrame) -> Optional[float]:
    """
    Balance of upper vs lower rejections (wicks).
    """
    medium = config.LOOKBACK["medium"]
    
    if len(df) < medium:
        return None
    
    recent = df.tail(medium)
    
    upper_wicks = recent.apply(
        lambda r: r["high"] - max(r["open"], r["close"]), axis=1
    ).sum()
    
    lower_wicks = recent.apply(
        lambda r: min(r["open"], r["close"]) - r["low"], axis=1
    ).sum()
    
    total = upper_wicks + lower_wicks
    if total == 0:
        return 0.5
    
    # Symmetry = balance between upper and lower
    ratio = min(upper_wicks, lower_wicks) / max(upper_wicks, lower_wicks) if max(upper_wicks, lower_wicks) > 0 else 1.0
    return ratio


def calculate_trend_neutrality(df: pd.DataFrame) -> Optional[float]:
    """
    Flatness of regression slope (neutral = high energy).
    """
    medium = config.LOOKBACK["medium"]
    
    if len(df) < medium:
        return None
    
    prices = df["close"].tail(medium).values
    x = np.arange(len(prices))
    
    slope, _ = np.polyfit(x, prices, 1)
    mean_price = np.mean(prices)
    
    # Slope as % of price
    slope_pct = abs(slope / mean_price) * 100
    
    # Flat = high score (daily slope < 0.1% is neutral)
    score = max(0.0, min(1.0, 1.0 - slope_pct * 5))
    return score


# =============================================================================
# MEAN ADHERENCE EVIDENCE
# =============================================================================

def calculate_mean_deviation(df: pd.DataFrame) -> Optional[float]:
    """
    Average distance from moving average.
    """
    medium = config.LOOKBACK["medium"]
    
    if len(df) < medium:
        return None
    
    recent = df.tail(medium)
    ma = recent["close"].mean()
    
    avg_deviation = (abs(recent["close"] - ma) / ma).mean() * 100
    
    # Low deviation = high score
    score = max(0.0, min(1.0, 1.0 - avg_deviation * 5))
    return score


def calculate_reversion_speed(df: pd.DataFrame) -> Optional[float]:
    """
    How fast price returns to mean after excursions.
    """
    medium = config.LOOKBACK["medium"]
    
    if len(df) < medium:
        return None
    
    recent = df.tail(medium).copy()
    ma = recent["close"].rolling(5).mean()
    
    # Calculate crossovers
    above = (recent["close"] > ma).astype(int)
    crossovers = abs(above.diff()).sum()
    
    # More crossovers = faster reversion
    score = min(1.0, crossovers / (medium / 3))
    return score


def calculate_wick_containment(df: pd.DataFrame) -> Optional[float]:
    """
    Wick length relative to body - smaller wicks = better containment.
    """
    medium = config.LOOKBACK["medium"]
    
    if len(df) < medium:
        return None
    
    recent = df.tail(medium)
    
    total_wick = recent.apply(
        lambda r: (r["high"] - max(r["open"], r["close"])) + (min(r["open"], r["close"]) - r["low"]),
        axis=1
    ).sum()
    
    total_body = recent.apply(
        lambda r: abs(r["close"] - r["open"]),
        axis=1
    ).sum()
    
    if total_body == 0:
        return 0.5
    
    ratio = total_wick / total_body
    # Lower wick ratio = better containment
    score = max(0.0, min(1.0, 1.0 - ratio / 2))
    return score


# =============================================================================
# ENERGY DURATION EVIDENCE
# =============================================================================

def calculate_compression_days(df: pd.DataFrame) -> Optional[float]:
    """
    Count consecutive low-volatility days.
    """
    medium = config.LOOKBACK["medium"]
    long = config.LOOKBACK["long"]
    
    if len(df) < long:
        return None
    
    # Daily range as % of close
    df = df.copy()
    df["range_pct"] = (df["high"] - df["low"]) / df["close"] * 100
    
    median_range = df["range_pct"].tail(long).median()
    
    # Count recent days with below-median range
    recent = df.tail(medium)
    compressed_days = (recent["range_pct"] < median_range).sum()
    
    score = compressed_days / medium
    return score


def calculate_setup_stability(df: pd.DataFrame) -> Optional[float]:
    """
    Consistency of compression state.
    """
    medium = config.LOOKBACK["medium"]
    long = config.LOOKBACK["long"]
    
    if len(df) < long:
        return None
    
    df = df.copy()
    df["range_pct"] = (df["high"] - df["low"]) / df["close"] * 100
    
    recent_ranges = df["range_pct"].tail(medium)
    
    # Low coefficient of variation = stable
    cv = recent_ranges.std() / recent_ranges.mean() if recent_ranges.mean() > 0 else 1.0
    
    score = max(0.0, min(1.0, 1.0 - cv))
    return score


def calculate_expansion_failures(df: pd.DataFrame) -> Optional[float]:
    """
    Count failed breakout attempts (quick reversals).
    """
    medium = config.LOOKBACK["medium"]
    
    if len(df) < medium:
        return None
    
    recent = df.tail(medium)
    
    # Count days where high was rejected (closed in lower half)
    failures = recent.apply(
        lambda r: 1 if r["close"] < (r["high"] + r["low"]) / 2 and (r["high"] - r["low"]) > 0 else 0,
        axis=1
    ).sum()
    
    # More failures = more stored energy
    score = min(1.0, failures / (medium * 0.5))
    return score
