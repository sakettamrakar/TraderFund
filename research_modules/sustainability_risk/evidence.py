"""Stage 5: Sustainability & Risk - Evidence (Risk-focused, higher = more risk)"""
import logging
from typing import Optional
import numpy as np
import pandas as pd
from . import config

logger = logging.getLogger(__name__)

# EXTENSION RISK (higher = more extended = more risk)
def calculate_distance_from_base(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["long"]:
        return None
    base = df["close"].iloc[-config.LOOKBACK["long"]:-config.LOOKBACK["short"]].mean()
    current = df["close"].iloc[-1]
    extension = (current - base) / base
    return max(0.0, min(1.0, abs(extension) * 5))

def calculate_mean_deviation(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    ma = df["close"].tail(config.LOOKBACK["medium"]).mean()
    current = df["close"].iloc[-1]
    deviation = abs(current - ma) / ma
    return max(0.0, min(1.0, deviation * 10))

def calculate_speed_of_move(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"]:
        return None
    recent_move = abs(df["close"].iloc[-1] - df["close"].iloc[-config.LOOKBACK["short"]]) / df["close"].iloc[-config.LOOKBACK["short"]]
    return max(0.0, min(1.0, recent_move * 10))

# PARTICIPATION QUALITY (inverted: poor quality = high risk)
def calculate_volume_consistency(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"] or "volume" not in df.columns:
        return None
    recent_vol = df["volume"].tail(config.LOOKBACK["short"]).mean()
    prior_vol = df["volume"].tail(config.LOOKBACK["medium"]).mean()
    if prior_vol == 0:
        return 0.5
    ratio = recent_vol / prior_vol
    # Declining volume = risk
    return max(0.0, min(1.0, 1.5 - ratio))

def calculate_pullback_support(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"]:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    lower_wicks = recent.apply(lambda r: min(r["open"], r["close"]) - r["low"], axis=1).sum()
    upper_wicks = recent.apply(lambda r: r["high"] - max(r["open"], r["close"]), axis=1).sum()
    # More upper wicks = rejection = risk
    total = lower_wicks + upper_wicks
    if total == 0:
        return 0.5
    return upper_wicks / total

def calculate_distribution_pattern(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"] or "volume" not in df.columns:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    down_volume = recent[recent["close"] < recent["open"]]["volume"].sum()
    total_volume = recent["volume"].sum()
    return down_volume / total_volume if total_volume > 0 else 0.5

# VOLATILITY COMPATIBILITY (higher = more chaotic = risk)
def calculate_volatility_spike(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["long"]:
        return None
    recent_vol = df["close"].tail(config.LOOKBACK["short"]).pct_change().std()
    hist_vol = df["close"].tail(config.LOOKBACK["long"]).pct_change().std()
    if hist_vol == 0:
        return 0.5
    return max(0.0, min(1.0, (recent_vol / hist_vol - 1)))

def calculate_range_instability(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    ranges = recent["high"] - recent["low"]
    cv = ranges.std() / ranges.mean() if ranges.mean() > 0 else 0
    return min(1.0, cv)

def calculate_chaos_score(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"]:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    reversals = 0
    for i in range(1, len(recent)):
        prev_dir = 1 if recent["close"].iloc[i-1] > recent["open"].iloc[i-1] else -1
        curr_dir = 1 if recent["close"].iloc[i] > recent["open"].iloc[i] else -1
        if prev_dir != curr_dir:
            reversals += 1
    return reversals / (config.LOOKBACK["short"] - 1)

# MOMENTUM DECAY (higher = more decay = risk)
def calculate_follow_through_decay(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    first_half = df.iloc[-config.LOOKBACK["medium"]:-config.LOOKBACK["short"]]
    second_half = df.tail(config.LOOKBACK["short"])
    first_move = abs(first_half["close"].iloc[-1] - first_half["close"].iloc[0])
    second_move = abs(second_half["close"].iloc[-1] - second_half["close"].iloc[0])
    if first_move == 0:
        return 0.5
    decay = 1.0 - (second_move / first_move)
    return max(0.0, min(1.0, decay))

def calculate_persistence_decline(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    first_half = df.iloc[-config.LOOKBACK["medium"]:-config.LOOKBACK["short"]]
    second_half = df.tail(config.LOOKBACK["short"])
    first_up = (first_half["close"] > first_half["open"]).sum() / len(first_half)
    second_up = (second_half["close"] > second_half["open"]).sum() / len(second_half)
    decline = first_up - second_up
    return max(0.0, min(1.0, decline + 0.5))

def calculate_progress_stall(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    progress = abs(recent["close"].iloc[-1] - recent["close"].iloc[0]) / recent["close"].iloc[0]
    # Less progress = stall = risk
    return max(0.0, min(1.0, 1.0 - progress * 20))
