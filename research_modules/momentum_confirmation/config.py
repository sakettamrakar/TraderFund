"""Stage 4: Momentum Confirmation - Config"""
from pathlib import Path

BEHAVIOR_WEIGHTS = {
    "directional_persistence": 0.30,
    "follow_through": 0.25,
    "relative_strength": 0.25,
    "momentum_stability": 0.20,
}

LOOKBACK = {"short": 5, "medium": 10, "long": 20}

EVIDENCE_WEIGHTS = {
    "consecutive_closes": 0.35, "net_movement": 0.35, "counter_reduction": 0.30,
    "gain_holding": 0.40, "pullback_depth": 0.30, "level_acceptance": 0.30,
    "vol_adjusted_return": 0.40, "recent_outperformance": 0.30, "persistence_ratio": 0.30,
    "smooth_progression": 0.35, "controlled_volatility": 0.35, "reversal_absence": 0.30,
}

STATE_THRESHOLDS = {"confirmed": 60, "emerging": 30}
CONFIDENCE_THRESHOLDS = {"high": 0.70, "moderate": 0.40}

DATA_ROOT = Path("data")
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"
PARTICIPATION_PATH = DATA_ROOT / "participation" / "us"
OUTPUT_PATH = DATA_ROOT / "momentum" / "us"
VERSION = "1.0.0"
