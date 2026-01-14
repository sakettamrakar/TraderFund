"""
Stage 1: Structural Capability - Configuration

Behavior weights, lookback periods, and evidence configuration.
All thresholds are configurable to allow tuning without code changes.
"""

from pathlib import Path

# =============================================================================
# BEHAVIOR WEIGHTS
# =============================================================================
# How much each behavior contributes to final structural score

BEHAVIOR_WEIGHTS = {
    "long_term_bias": 0.30,
    "medium_term_alignment": 0.25,
    "institutional_acceptance": 0.25,
    "volatility_suitability": 0.20,
}

# =============================================================================
# LOOKBACK PERIODS (Trading Days)
# =============================================================================

LOOKBACK = {
    "long_term": 100,   # Days for long-term analysis
    "medium_term": 20,  # Days for medium-term analysis
    "short_term": 5,    # Days for short-term context
}

# =============================================================================
# EVIDENCE WEIGHTS (within each behavior)
# =============================================================================

EVIDENCE_WEIGHTS = {
    # Long-Term Bias
    "lt_trend_slope": 0.40,
    "lt_position": 0.35,
    "lt_stability": 0.25,
    
    # Medium-Term Alignment  
    "mt_trend_slope": 0.30,
    "mt_lt_coherence": 0.40,
    "mt_channel_quality": 0.30,
    
    # Institutional Acceptance
    "vwap_position": 0.30,
    "volume_trend": 0.40,
    "wick_ratio": 0.30,
    
    # Volatility Suitability
    "atr_percentile": 0.40,
    "range_stability": 0.35,
    "gap_frequency": 0.25,
}

# =============================================================================
# CONFIDENCE THRESHOLDS
# =============================================================================

CONFIDENCE_THRESHOLDS = {
    "high": 0.70,      # Score >= 70 = high confidence
    "moderate": 0.40,  # Score >= 40 = moderate confidence
    # Below 40 = low confidence
}

# =============================================================================
# DATA PATHS
# =============================================================================

DATA_ROOT = Path("data")

# Input: Staged price data
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"

# Input: Eligible symbols from Stage 0
ELIGIBILITY_PATH = DATA_ROOT / "master" / "us" / "universe_eligibility.parquet"

# Output: Structural capability results
OUTPUT_PATH = DATA_ROOT / "structural" / "us"

# =============================================================================
# VERSION
# =============================================================================

VERSION = "1.0.0"
