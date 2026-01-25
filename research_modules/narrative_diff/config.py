"""Narrative Diff - Config"""
from pathlib import Path

# Score drift threshold - changes below this are ignored
SCORE_DRIFT_THRESHOLD = 10

# Narrative type promotion order (lower index = less advanced)
TYPE_ORDER = [
    "neutral", "structural_strength", "energy_buildup", 
    "early_momentum", "confirmed_momentum", "momentum_fragility", "degradation"
]

# State strength order
STATE_ORDER = ["invalidated", "emerging", "weakening", "stable", "strengthening"]

# Risk profile order
RISK_ORDER = ["low", "moderate", "high"]

# Data paths
DATA_ROOT = Path("data")
NARRATIVE_PATH = DATA_ROOT / "narratives" / "us"
DIFF_PATH = DATA_ROOT / "narrative_diffs" / "us"

VERSION = "1.0.0"
