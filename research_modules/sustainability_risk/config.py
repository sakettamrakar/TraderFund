"""Stage 5: Sustainability & Risk - Config"""
from pathlib import Path

BEHAVIOR_WEIGHTS = {
    "extension_risk": 0.25,
    "participation_quality": 0.30,
    "volatility_compatibility": 0.25,
    "momentum_decay": 0.20,
}

LOOKBACK = {"short": 5, "medium": 10, "long": 20}

EVIDENCE_WEIGHTS = {
    "distance_from_base": 0.35, "mean_deviation": 0.35, "speed_of_move": 0.30,
    "volume_consistency": 0.35, "pullback_support": 0.35, "distribution_pattern": 0.30,
    "volatility_spike": 0.35, "range_instability": 0.35, "chaos_score": 0.30,
    "follow_through_decay": 0.35, "persistence_decline": 0.35, "progress_stall": 0.30,
}

RISK_THRESHOLDS = {"high": 60, "moderate": 30}
POSTURE_MAP = {"low": "monitor", "moderate": "cautious", "high": "avoid"}

DATA_ROOT = Path("data")
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"
MOMENTUM_PATH = DATA_ROOT / "momentum" / "us"
OUTPUT_PATH = DATA_ROOT / "sustainability" / "us"
VERSION = "1.0.0"
