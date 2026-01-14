"""Pipeline Controller - Config"""
from pathlib import Path

# Execution Intervals (Days)
STAG_0_INTERVAL = 7
STAG_1_INTERVAL = 3

# Activation Thresholds (Absolute)
S1_MIN_SCORE = 50.0  # Min structural score to trigger S2
S2_STATES = ["forming", "mature"]  # Energy states to trigger S3
S3_STATES = ["emerging", "active"]  # Participation states to trigger S4
S4_STATES = ["emerging", "confirmed"]  # Momentum states to trigger S5

# Score Bucket Thresholds (for crossing detection)
SCORE_BUCKETS = {
    "low": 30,
    "medium": 50,
    "high": 70,
}

# Formalized Skip Reason Codes
SKIP_CODES = {
    "interval_not_reached": "INTERVAL_NOT_REACHED",
    "history_not_backfilled": "HISTORY_NOT_BACKFILLED",
    "s1_score_insufficient": "S1_SCORE_INSUFFICIENT",
    "energy_state_none": "ENERGY_STATE_NONE",
    "participation_not_emerging": "PARTICIPATION_NOT_EMERGING",
    "momentum_not_emerging": "MOMENTUM_NOT_EMERGING",
}

# Paths
DATA_ROOT = Path("data")
CONTROLLER_PATH = DATA_ROOT / "controller" / "us"
EXECUTION_HISTORY_PATH = CONTROLLER_PATH / "execution_history.parquet"
SCORE_HISTORY_PATH = CONTROLLER_PATH / "score_history.parquet"
DECISIONS_PATH = CONTROLLER_PATH / "decisions"

VERSION = "1.1.0"
