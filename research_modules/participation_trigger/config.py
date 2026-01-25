"""Stage 3: Participation Trigger - Config"""
from pathlib import Path

BEHAVIOR_WEIGHTS = {
    "volume_expansion": 0.30,
    "range_expansion": 0.25,
    "directional_commitment": 0.25,
    "participation_continuity": 0.20,
}

LOOKBACK = {"short": 5, "medium": 20, "long": 50}

EVIDENCE_WEIGHTS = {
    "relative_volume": 0.40, "volume_streak": 0.30, "volume_spike": 0.30,
    "range_ratio": 0.35, "body_expansion": 0.35, "range_breakout": 0.30,
    "close_location": 0.35, "direction_bias": 0.35, "gap_follow": 0.30,
    "multi_day_expansion": 0.40, "fade_resistance": 0.30, "overlap_reduction": 0.30,
}

TRIGGER_STATE_THRESHOLDS = {"active": 60, "emerging": 30}
CONFIDENCE_THRESHOLDS = {"high": 0.70, "moderate": 0.40}

DATA_ROOT = Path("data")
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"
ENERGY_PATH = DATA_ROOT / "energy" / "us"
OUTPUT_PATH = DATA_ROOT / "participation" / "us"
VERSION = "1.0.0"
