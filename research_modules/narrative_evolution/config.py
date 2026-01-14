"""Narrative Evolution - Config"""
from pathlib import Path

# Narrative type thresholds (stage score requirements)
NARRATIVE_THRESHOLDS = {
    "structural_strength": {"s1": 60, "s2_max": 40, "s3_max": 40},
    "energy_buildup": {"s2": 50, "s3_max": 40},
    "early_momentum": {"s3": 50, "s4_max": 50},
    "confirmed_momentum": {"s4": 60},
    "momentum_fragility": {"s4": 40, "s5_risk": 50},
    "degradation": {"s5_risk": 60},
    "neutral": {},  # Default when nothing qualifies
}

# State transition thresholds
EVOLUTION_THRESHOLDS = {
    "strengthen_delta": 10,  # Score increase to strengthen
    "weaken_delta": -15,     # Score drop to weaken
    "invalidate_days": 2,    # Days below threshold to invalidate
    "decay_days": 5,         # Days without change to decay
}

# Narrative state priorities (higher = stronger)
STATE_PRIORITY = {
    "invalidated": 0,
    "emerging": 1,
    "weakening": 2,
    "stable": 3,
    "strengthening": 4,
}

# Data paths
DATA_ROOT = Path("data")
STRUCTURAL_PATH = DATA_ROOT / "structural" / "us"
ENERGY_PATH = DATA_ROOT / "energy" / "us"
PARTICIPATION_PATH = DATA_ROOT / "participation" / "us"
MOMENTUM_PATH = DATA_ROOT / "momentum" / "us"
SUSTAINABILITY_PATH = DATA_ROOT / "sustainability" / "us"
NARRATIVE_PATH = DATA_ROOT / "narratives" / "us"

VERSION = "1.0.0"
