"""
Stage 0: Universe Hygiene - Configuration

All thresholds are configurable. Adjust these values to tune
the eligibility filter without modifying core logic.
"""

from pathlib import Path

# =============================================================================
# PRICE THRESHOLDS
# =============================================================================
# Buckets: PENNY (excluded) | EXTREME_LOW | LOW | ACCEPTABLE | HIGH

PRICE_THRESHOLDS = {
    "penny_cutoff": 1.00,       # Below this = excluded as penny stock
    "extreme_low": 5.00,        # Price $1-$5 = EXTREME_LOW bucket
    "low": 10.00,               # Price $5-$10 = LOW bucket
    "acceptable": 50.00,        # Price $10-$50 = ACCEPTABLE bucket
    # Above $50 = HIGH bucket
}


# =============================================================================
# VOLUME THRESHOLDS (Average Daily Volume)
# =============================================================================
# Buckets: ILLIQUID (excluded) | VERY_LOW | LOW | ACCEPTABLE | HIGH

VOLUME_THRESHOLDS = {
    "illiquid": 50_000,         # Below this = excluded as illiquid
    "very_low": 100_000,        # 50K-100K = VERY_LOW bucket
    "low": 500_000,             # 100K-500K = LOW bucket
    "acceptable": 1_000_000,    # 500K-1M = ACCEPTABLE bucket
    # Above 1M = HIGH bucket
}


# =============================================================================
# EXCHANGE & ASSET TYPE FILTERS
# =============================================================================

EXCHANGE_ALLOWLIST = [
    "NYSE",
    "NASDAQ",
    "NYSE MKT",     # NYSE American (formerly AMEX)
    "NYSE ARCA",    # NYSE Arca
    "BATS",         # Cboe BZX Exchange
]

ASSET_TYPE_ALLOWLIST = [
    "Stock",        # Common equity only
    # Explicitly excluded: ETF, ADR, Warrant, Unit, etc.
]


# =============================================================================
# ACTIVITY THRESHOLDS
# =============================================================================

EVALUATION_WINDOW_DAYS = 30     # Calendar days to look back
TRADING_DAYS_MIN = 15           # Relaxed for expansion backfills


# =============================================================================
# DATA PATHS
# =============================================================================

DATA_ROOT = Path("data")

# Input: Symbol universe from Alpha Vantage
SYMBOLS_CSV_PATH = DATA_ROOT / "master" / "us" / "symbols.csv"

# Input: Metadata from ingestion layer (preferred)
METADATA_PARQUET_PATH = DATA_ROOT / "master" / "us" / "universe_metadata.parquet"

# Input: Staged price data for volume/price evaluation (fallback)
STAGING_PATH = DATA_ROOT / "staging" / "us" / "daily"

# Output: Eligibility results
ELIGIBILITY_OUTPUT_PATH = DATA_ROOT / "master" / "us" / "universe_eligibility.parquet"


# =============================================================================
# EXECUTION SETTINGS
# =============================================================================

# Minimum eligible symbols expected (sanity check)
MIN_ELIGIBLE_SYMBOLS = 500

# Maximum eligible symbols expected (sanity check)  
MAX_ELIGIBLE_SYMBOLS = 3000
