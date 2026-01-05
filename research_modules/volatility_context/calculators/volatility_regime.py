"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Volatility Regime Classifier

LABELS market conditions. Does NOT make trade recommendations.
Outputs are descriptive, not prescriptive.
##############################################################################
"""

import pandas as pd
import numpy as np
from typing import Literal, Optional


# Type aliases for regime labels
VolatilityLabel = Literal["LOW", "NORMAL", "HIGH"]
TrendLabel = Literal["TRENDING", "RANGING", "UNCLEAR"]


def calculate_rolling_std(
    series: pd.Series,
    period: int = 20,
) -> pd.Series:
    """Calculate rolling standard deviation.

    Args:
        series: Price series (typically close prices).
        period: Lookback period.

    Returns:
        Series of rolling standard deviations.
    """
    return series.rolling(window=period).std()


def calculate_rolling_std_pct(
    series: pd.Series,
    period: int = 20,
) -> pd.Series:
    """Calculate rolling standard deviation as percentage of mean.

    Args:
        series: Price series.
        period: Lookback period.

    Returns:
        Series of coefficient of variation values (std / mean * 100).
    """
    rolling_std = series.rolling(window=period).std()
    rolling_mean = series.rolling(window=period).mean()
    return (rolling_std / rolling_mean) * 100


def classify_volatility(
    current_atr: float,
    historical_atr_mean: float,
    historical_atr_std: float,
) -> VolatilityLabel:
    """Classify current volatility relative to historical distribution.

    Uses z-score approach:
    - LOW: Current ATR is more than 1 std below mean
    - HIGH: Current ATR is more than 1 std above mean
    - NORMAL: Within 1 std of mean

    This is a LABEL, not a trade recommendation.

    Args:
        current_atr: Current ATR value.
        historical_atr_mean: Historical mean ATR.
        historical_atr_std: Historical standard deviation of ATR.

    Returns:
        Volatility label: "LOW", "NORMAL", or "HIGH".
    """
    if historical_atr_std == 0:
        return "NORMAL"

    z_score = (current_atr - historical_atr_mean) / historical_atr_std

    if z_score < -1.0:
        return "LOW"
    elif z_score > 1.0:
        return "HIGH"
    else:
        return "NORMAL"


def classify_trend(
    prices: pd.Series,
    lookback: int = 20,
    threshold: float = 0.6,
) -> TrendLabel:
    """Classify whether the market is trending or ranging.

    Uses directional consistency: measures what fraction of periods
    moved in the dominant direction.

    This is a LABEL, not a trade recommendation.

    Args:
        prices: Price series (typically close prices).
        lookback: Number of periods to analyze.
        threshold: Minimum directional consistency for "TRENDING" label.

    Returns:
        Trend label: "TRENDING", "RANGING", or "UNCLEAR".
    """
    if len(prices) < lookback + 1:
        return "UNCLEAR"

    recent = prices.tail(lookback + 1)
    returns = recent.diff().dropna()

    if len(returns) == 0:
        return "UNCLEAR"

    up_moves = (returns > 0).sum()
    down_moves = (returns < 0).sum()
    total = len(returns)

    up_ratio = up_moves / total
    down_ratio = down_moves / total

    max_ratio = max(up_ratio, down_ratio)

    if max_ratio >= threshold:
        return "TRENDING"
    elif max_ratio <= 0.4:
        return "RANGING"
    else:
        return "UNCLEAR"


def classify_range_state(
    current_range: float,
    avg_range: float,
    expansion_threshold: float = 1.5,
    contraction_threshold: float = 0.5,
) -> Literal["EXPANSION", "NORMAL", "COMPRESSION"]:
    """Classify range expansion or contraction.

    This is a LABEL, not a trade recommendation.

    Args:
        current_range: Current period range.
        avg_range: Historical average range.
        expansion_threshold: Ratio above which = expansion.
        contraction_threshold: Ratio below which = compression.

    Returns:
        Range state label.
    """
    if avg_range == 0:
        return "NORMAL"

    ratio = current_range / avg_range

    if ratio >= expansion_threshold:
        return "EXPANSION"
    elif ratio <= contraction_threshold:
        return "COMPRESSION"
    else:
        return "NORMAL"
