"""Stage 4: Momentum Confirmation - Evidence"""
import logging
from typing import Optional
import numpy as np
import pandas as pd
from . import config

logger = logging.getLogger(__name__)

# DIRECTIONAL PERSISTENCE
def calculate_consecutive_closes(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    directions = (recent["close"] > recent["open"]).astype(int)
    max_streak = 0
    current = 0
    for d in directions:
        if d == 1:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 0
    return max_streak / config.LOOKBACK["medium"]

def calculate_net_movement(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    net = (recent["close"].iloc[-1] - recent["close"].iloc[0]) / recent["close"].iloc[0]
    return max(0.0, min(1.0, (net + 0.05) / 0.1))

def calculate_counter_reduction(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    down_days = (recent["close"] < recent["open"]).sum()
    return 1.0 - (down_days / config.LOOKBACK["medium"])

# FOLLOW-THROUGH
def calculate_gain_holding(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    gains = (recent["close"] - recent["open"]).clip(lower=0).sum()
    total_range = (recent["high"] - recent["low"]).sum()
    return gains / total_range if total_range > 0 else 0.5

def calculate_pullback_depth(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"]:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    high = recent["high"].max()
    current = recent["close"].iloc[-1]
    pullback = (high - current) / high if high > 0 else 0
    return max(0.0, 1.0 - pullback * 10)

def calculate_level_acceptance(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    prior = df.iloc[-config.LOOKBACK["medium"]:-config.LOOKBACK["short"]]
    recent = df.tail(config.LOOKBACK["short"])
    prior_high = prior["high"].max()
    recent_closes_above = (recent["close"] > prior_high).sum()
    return recent_closes_above / config.LOOKBACK["short"]

# RELATIVE STRENGTH
def calculate_vol_adjusted_return(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    ret = (recent["close"].iloc[-1] - recent["close"].iloc[0]) / recent["close"].iloc[0]
    vol = recent["close"].pct_change().std()
    if vol == 0:
        return 0.5
    sharpe = ret / vol
    return max(0.0, min(1.0, (sharpe + 1) / 2))

def calculate_recent_outperformance(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["long"]:
        return None
    recent_ret = (df["close"].iloc[-1] - df["close"].iloc[-config.LOOKBACK["short"]]) / df["close"].iloc[-config.LOOKBACK["short"]]
    baseline_ret = (df["close"].iloc[-config.LOOKBACK["short"]] - df["close"].iloc[-config.LOOKBACK["long"]]) / df["close"].iloc[-config.LOOKBACK["long"]]
    outperformance = recent_ret - baseline_ret
    return max(0.0, min(1.0, (outperformance + 0.05) / 0.1))

def calculate_persistence_ratio(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    up_days = (recent["close"] > recent["open"]).sum()
    return up_days / config.LOOKBACK["medium"]

# MOMENTUM STABILITY
def calculate_smooth_progression(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    returns = recent["close"].pct_change().dropna()
    positive = (returns > 0).sum()
    return positive / len(returns) if len(returns) > 0 else 0.5

def calculate_controlled_volatility(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["long"]:
        return None
    recent_vol = df["close"].tail(config.LOOKBACK["short"]).pct_change().std()
    hist_vol = df["close"].tail(config.LOOKBACK["long"]).pct_change().std()
    if hist_vol == 0:
        return 0.5
    ratio = recent_vol / hist_vol
    return max(0.0, min(1.0, 1.5 - ratio))

def calculate_reversal_absence(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    recent = df.tail(config.LOOKBACK["medium"])
    big_reversals = 0
    for i in range(1, len(recent)):
        prev_dir = 1 if recent["close"].iloc[i-1] > recent["open"].iloc[i-1] else -1
        curr_dir = 1 if recent["close"].iloc[i] > recent["open"].iloc[i] else -1
        if prev_dir != curr_dir:
            move = abs(recent["close"].iloc[i] - recent["open"].iloc[i]) / recent["open"].iloc[i]
            if move > 0.02:
                big_reversals += 1
    return 1.0 - (big_reversals / config.LOOKBACK["medium"])
