"""Stage 3: Participation Trigger - Evidence"""
import logging
from typing import Optional
import numpy as np
import pandas as pd
from . import config

logger = logging.getLogger(__name__)

# VOLUME EXPANSION
def calculate_relative_volume(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"] or "volume" not in df.columns:
        return None
    recent_vol = df["volume"].tail(config.LOOKBACK["short"]).mean()
    avg_vol = df["volume"].tail(config.LOOKBACK["medium"]).mean()
    if avg_vol == 0:
        return 0.5
    ratio = recent_vol / avg_vol
    return max(0.0, min(1.0, (ratio - 0.5) / 1.5))

def calculate_volume_streak(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"] or "volume" not in df.columns:
        return None
    avg_vol = df["volume"].tail(config.LOOKBACK["medium"]).mean()
    recent = df["volume"].tail(config.LOOKBACK["short"]).values
    streak = sum(1 for v in recent if v > avg_vol)
    return streak / config.LOOKBACK["short"]

def calculate_volume_spike(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"] or "volume" not in df.columns:
        return None
    avg_vol = df["volume"].tail(config.LOOKBACK["medium"]).mean()
    max_recent = df["volume"].tail(config.LOOKBACK["short"]).max()
    if avg_vol == 0:
        return 0.5
    ratio = max_recent / avg_vol
    return max(0.0, min(1.0, (ratio - 1.0) / 2.0))

# RANGE EXPANSION
def calculate_range_ratio(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    df = df.copy()
    df["range"] = df["high"] - df["low"]
    recent = df["range"].tail(config.LOOKBACK["short"]).mean()
    avg = df["range"].tail(config.LOOKBACK["medium"]).mean()
    if avg == 0:
        return 0.5
    ratio = recent / avg
    return max(0.0, min(1.0, (ratio - 0.5) / 1.5))

def calculate_body_expansion(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    df = df.copy()
    df["body"] = abs(df["close"] - df["open"])
    recent = df["body"].tail(config.LOOKBACK["short"]).mean()
    avg = df["body"].tail(config.LOOKBACK["medium"]).mean()
    if avg == 0:
        return 0.5
    return max(0.0, min(1.0, (recent / avg - 0.5) / 1.5))

def calculate_range_breakout(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    prior = df.iloc[-config.LOOKBACK["medium"]:-config.LOOKBACK["short"]]
    recent_high = df["high"].tail(config.LOOKBACK["short"]).max()
    recent_low = df["low"].tail(config.LOOKBACK["short"]).min()
    prior_high = prior["high"].max()
    prior_low = prior["low"].min()
    if recent_high > prior_high or recent_low < prior_low:
        return 1.0
    return 0.0

# DIRECTIONAL COMMITMENT
def calculate_close_location(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"]:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    locs = recent.apply(
        lambda r: (r["close"] - r["low"]) / (r["high"] - r["low"]) if r["high"] != r["low"] else 0.5,
        axis=1
    )
    return locs.mean()

def calculate_direction_bias(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"]:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    up_days = (recent["close"] > recent["open"]).sum()
    return up_days / config.LOOKBACK["short"]

def calculate_gap_follow(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"]:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    gaps = recent["open"].values[1:] - recent["close"].values[:-1]
    closes = recent["close"].values[1:] - recent["open"].values[1:]
    follow = sum(1 for g, c in zip(gaps, closes) if (g > 0 and c > 0) or (g < 0 and c < 0))
    return follow / max(len(gaps), 1)

# PARTICIPATION CONTINUITY
def calculate_multi_day_expansion(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["medium"]:
        return None
    df = df.copy()
    df["range"] = df["high"] - df["low"]
    avg_range = df["range"].tail(config.LOOKBACK["medium"]).mean()
    recent = df["range"].tail(config.LOOKBACK["short"])
    expanded = (recent > avg_range).sum()
    return expanded / config.LOOKBACK["short"]

def calculate_fade_resistance(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"]:
        return None
    recent = df.tail(config.LOOKBACK["short"])
    fades = recent.apply(
        lambda r: 1 if r["close"] < r["open"] and r["open"] > r["close"] else 0,
        axis=1
    ).sum()
    return 1.0 - (fades / config.LOOKBACK["short"])

def calculate_overlap_reduction(df: pd.DataFrame) -> Optional[float]:
    if len(df) < config.LOOKBACK["short"] + 1:
        return None
    recent = df.tail(config.LOOKBACK["short"] + 1)
    overlaps = 0
    for i in range(1, len(recent)):
        curr_low, curr_high = recent["low"].iloc[i], recent["high"].iloc[i]
        prev_low, prev_high = recent["low"].iloc[i-1], recent["high"].iloc[i-1]
        overlap = max(0, min(curr_high, prev_high) - max(curr_low, prev_low))
        if overlap > 0:
            overlaps += 1
    return 1.0 - (overlaps / config.LOOKBACK["short"])
