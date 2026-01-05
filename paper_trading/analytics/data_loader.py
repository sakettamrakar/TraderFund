"""
##############################################################################
## PAPER TRADING ANALYTICS - READ ONLY
##############################################################################
Data Loader

Loads paper trade logs from CSV/Parquet files.
READ-ONLY access to trade data.
##############################################################################
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Default log directory
DEFAULT_LOG_DIR = Path("paper_trading/logs")

# Expected columns in trade logs
REQUIRED_COLUMNS = [
    "timestamp",
    "symbol",
    "entry_price",
    "exit_price",
    "quantity",
    "holding_minutes",
    "gross_pnl",
    "net_pnl",
]

OPTIONAL_COLUMNS = [
    "signal_confidence",
    "signal_reason",
    "exit_reason",
]


def load_trade_logs(
    log_dir: Optional[Path] = None,
    date_filter: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> pd.DataFrame:
    """Load paper trade logs into a DataFrame.

    Args:
        log_dir: Directory containing log files.
        date_filter: Specific date to load (YYYYMMDD in filename).
        start_date: Start of date range.
        end_date: End of date range.

    Returns:
        DataFrame with trade logs.
    """
    log_dir = log_dir or DEFAULT_LOG_DIR
    log_dir = Path(log_dir)

    if not log_dir.exists():
        logger.warning(f"Log directory does not exist: {log_dir}")
        return pd.DataFrame()

    # Find all CSV files
    csv_files = list(log_dir.glob("*.csv"))
    if not csv_files:
        logger.warning(f"No CSV files found in {log_dir}")
        return pd.DataFrame()

    # Filter by date if specified
    if date_filter:
        date_str = date_filter.strftime("%Y%m%d")
        csv_files = [f for f in csv_files if date_str in f.name]

    # Load and concatenate
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            df["source_file"] = file.name
            dfs.append(df)
            logger.info(f"Loaded {len(df)} trades from {file.name}")
        except Exception as e:
            logger.error(f"Error loading {file}: {e}")

    if not dfs:
        return pd.DataFrame()

    combined = pd.concat(dfs, ignore_index=True)

    # Parse timestamp
    if "timestamp" in combined.columns:
        combined["timestamp"] = pd.to_datetime(combined["timestamp"])

    # Filter by date range
    if start_date and "timestamp" in combined.columns:
        combined = combined[combined["timestamp"].dt.date >= start_date]
    if end_date and "timestamp" in combined.columns:
        combined = combined[combined["timestamp"].dt.date <= end_date]

    # Validate columns
    missing = [c for c in REQUIRED_COLUMNS if c not in combined.columns]
    if missing:
        logger.warning(f"Missing required columns: {missing}")

    logger.info(f"Loaded {len(combined)} total trades")
    return combined


def validate_trade_data(df: pd.DataFrame) -> List[str]:
    """Validate trade data and return list of issues.

    Args:
        df: Trade DataFrame.

    Returns:
        List of validation issues (empty if valid).
    """
    issues = []

    if df.empty:
        issues.append("No trade data loaded")
        return issues

    # Check required columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            issues.append(f"Missing required column: {col}")

    # Check for nulls in critical columns
    for col in ["symbol", "entry_price", "exit_price", "net_pnl"]:
        if col in df.columns and df[col].isna().any():
            null_count = df[col].isna().sum()
            issues.append(f"NULL values in {col}: {null_count}")

    return issues
