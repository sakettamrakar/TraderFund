"""
Stage 2: Energy Setup - Configuration

Behavior weights, lookback periods, and energy state thresholds.
"""

from pathlib import Path

# =============================================================================
# BEHAVIOR WEIGHTS
# =============================================================================

BEHAVIOR_WEIGHTS = {
    "volatility_compression": 0.30,
    "range_balance": 0.25,
    "mean_adherence": 0.25,
    "energy_duration": 0.20,
}

# =============================================================================
# LOOKBACK PERIODS
# =============================================================================

LOOKBACK = {
    "short": 10,    # Recent compression window
    "medium": 20,   # Standard analysis window
    "long": 50,     # Historical reference
}

# =============================================================================
# EVIDENCE WEIGHTS
# =============================================================================

EVIDENCE_WEIGHTS = {
    # Volatility Compression
    "atr_compression": 0.40,
    "range_squeeze": 0.35,
    "return_tightness": 0.25,
    
    # Range Balance
    "range_containment": 0.35,
    "rejection_symmetry": 0.30,
    "trend_neutrality": 0.35,
    
    # Mean Adherence
    "mean_deviation": 0.40,
    "reversion_speed": 0.30,
    "wick_containment": 0.30,
    
    # Energy Duration
    "compression_days": 0.40,
    "setup_stability": 0.35,
    "expansion_failures": 0.25,
}

# =============================================================================
# ENERGY STATE THRESHOLDS
# =============================================================================

ENERGY_STATE_THRESHOLDS = {
    "mature": 60,    # Score >= 60 = mature
    "forming": 30,   # Score >= 30 = forming
    # Below 30 = none
}

# =============================================================================
# CONFIDENCE THRESHOLDS
# =============================================================================

CONFIDENCE_THRESHOLDS = {
    "high": 0.70,
    "moderate": 0.40,
}

# =============================================================================
# DATA PATHS
# =============================================================================

DATA_ROOT = Path("data")
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"
STRUCTURAL_PATH = DATA_ROOT / "structural" / "us"
OUTPUT_PATH = DATA_ROOT / "energy" / "us"

# =============================================================================
# VERSION
# =============================================================================

VERSION = "1.0.0"
