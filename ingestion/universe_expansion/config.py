"""Universe Expansion - Config"""
from pathlib import Path

# Universe size limits
MIN_SYMBOLS = 200
MAX_SYMBOLS = 650

# Manual Inclusions (Force add these tickers)
MANUAL_INCLUSIONS = ["BDSX"]

# Filtering criteria
VALID_EXCHANGES = ["NYSE", "NASDAQ", "NYSE ARCA", "BATS", "NYSE MKT"]
VALID_ASSET_TYPES = ["Stock", "ETF"]
EXCLUDED_STATUS = ["Delisted"]

# Market cap buckets (in billions USD)
MARKET_CAP_BUCKETS = {
    "mega": 200,    # >= 200B
    "large": 10,    # >= 10B
    "mid": 2,       # >= 2B
    "small": 0.3,   # >= 300M
    "micro": 0,     # < 300M
}

# Data paths
DATA_ROOT = Path("data")
SYMBOLS_CSV = DATA_ROOT / "master" / "us" / "symbols.csv"
SYMBOL_MASTER_PATH = DATA_ROOT / "master" / "us" / "symbol_master.parquet"

VERSION = "1.0.0"
