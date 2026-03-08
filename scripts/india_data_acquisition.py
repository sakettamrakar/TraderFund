"""
India Data Acquisition Script (Remediated).
Implements strict delta-merge logic for India market data ingestion.
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import sys

from india_in10y_fred_ingestion import ingest_india_10y

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "india"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "india_delta_ingestion.log"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ticker mappings
INDIA_TICKERS = {
    "NIFTY50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "INDIAVIX": "^INDIAVIX",
}


def _normalize_yfinance_frame(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    frame = df.reset_index().rename(columns={"index": "Date"})
    required_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
    missing = [column for column in required_cols if column not in frame.columns]
    if missing:
        raise ValueError(f"Downloaded frame missing columns: {missing}")

    frame = frame[required_cols].copy()
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce").dt.normalize()
    frame = frame.dropna(subset=["Date"]).drop_duplicates(subset=["Date"], keep="last")
    frame = frame[frame["Date"].dt.weekday < 5]
    return frame.sort_values("Date").reset_index(drop=True)


def align_proxy_sessions(names: list[str]) -> bool:
    frames: dict[str, pd.DataFrame] = {}
    common_dates = None

    for name in names:
        path = DATA_DIR / f"{name}.csv"
        if not path.exists():
            continue
        frame = pd.read_csv(path, parse_dates=["Date"])
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce").dt.normalize()
        frame = frame.dropna(subset=["Date"]).drop_duplicates(subset=["Date"], keep="last")
        frame = frame[frame["Date"].dt.weekday < 5].sort_values("Date").reset_index(drop=True)
        frames[name] = frame
        date_set = set(frame["Date"])
        common_dates = date_set if common_dates is None else common_dates & date_set

    if not frames or not common_dates:
        logger.error("Unable to align India proxy sessions: no common weekday session set found.")
        return False

    for name, frame in frames.items():
        aligned = frame[frame["Date"].isin(common_dates)].sort_values("Date").reset_index(drop=True)
        aligned.to_csv(DATA_DIR / f"{name}.csv", index=False)
        logger.info(f"Aligned {name} to {len(aligned)} common weekday sessions")

    return True

def download_ticker(name: str, ticker: str) -> bool:
    """
    Downloads historical data using strict delta-merge logic.
    Aborts if merge boundary cannot be determined to prevent data loss.
    """
    logger.info(f"Starting ingestion for {name} ({ticker})...")
    output_path = DATA_DIR / f"{name}.csv"
    
    existing_df = pd.DataFrame()
    start_date = None
    rows_before = 0

    # 1. Load Existing Canonical Data
    if output_path.exists():
        try:
            existing_df = pd.read_csv(output_path)
            if 'Date' not in existing_df.columns:
                raise ValueError(f"Existing file {output_path} missing 'Date' column.")
            
            existing_df['Date'] = pd.to_datetime(existing_df['Date'])
            existing_df = existing_df.sort_values('Date')
            
            if existing_df.empty:
                 logger.warning(f"Existing file {output_path} is empty. Treating as new.")
            else:
                last_date = existing_df['Date'].iloc[-1]
                # Overlap strictly: fetch from last known date
                start_date = last_date.strftime('%Y-%m-%d')
                rows_before = len(existing_df)
                logger.info(f"  Loaded canonical history: {rows_before} rows. Last Date: {last_date.date()}")
                
        except Exception as e:
            logger.error(f"CRITICAL: Failed to read existing canonical data for {name}: {e}")
            logger.error("ABORTING ingestion to prevent overwrite of potentially valid data.")
            raise  # Strict failure
    else:
        logger.info(f"  No existing history found for {name}. performing full initialization.")
        start_date = "2010-01-01" # Default start for new files

    # 2. Incremental Fetch
    try:
        logger.info(f"  Fetching incremental data from {start_date}...")
        new_data = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)
        
        if new_data.empty:
            logger.warning(f"  No new data returned for {ticker} from {start_date}.")
            # Even if no new data, we persist existing (no change) or just return
            # But let's verify if we are truly up to date
            return True

        new_data = _normalize_yfinance_frame(new_data)
            
        rows_fetched = len(new_data)
        logger.info(f"  Fetched {rows_fetched} rows.")

        # 3. Merge Semantics
        if not existing_df.empty:
            # Concatenate
            combined_df = pd.concat([existing_df, new_data])
            # Merge & Deduplicate: Keep LAST (newest fetch)
            # This handles corrections for the overlap date
            combined_df = combined_df.drop_duplicates(subset=['Date'], keep='last')
            combined_df = combined_df[combined_df['Date'].dt.weekday < 5]
            combined_df = combined_df.sort_values('Date')
            
            rows_after = len(combined_df)
            # Overlap calculation: (Before + Fetched) - After
            overlap_count = (rows_before + rows_fetched) - rows_after
            
            logger.info(f"  Merge Stats: Before={rows_before}, Fetched={rows_fetched}, After={rows_after}, Overlap/Dedup={overlap_count}")
        else:
            combined_df = new_data
            rows_after = len(combined_df)
            overlap_count = 0
            logger.info(f"  Initialized entries: {rows_after}")

        # 4. Save (Atomic-ish)
        # In a real heavy system we'd write to temp then rename, but here direct write is acceptable
        # provided we loaded successfully first.
        combined_df.to_csv(output_path, index=False)
        logger.info(f"SUCCESS: Saved {name} to {output_path}")
        return True

    except Exception as e:
        logger.error(f"ERROR during acquisition for {name}: {e}")
        return False

def ingest_real_in10y() -> bool:
    logger.info("Refreshing real IN10Y data from FRED...")
    try:
        output_path = ingest_india_10y()
        logger.info(f"Saved real IN10Y to {output_path}")
        return True
    except Exception as exc:
        logger.error(f"Failed to refresh real IN10Y data: {exc}")
        return False

def main():
    logger.info("=" * 60)
    logger.info("INDIA DELTA INGESTION RUN")
    logger.info("=" * 60)
    
    results = {}
    for name, ticker in INDIA_TICKERS.items():
        try:
            success = download_ticker(name, ticker)
            results[name] = "SUCCESS" if success else "FAILED"
        except Exception as e:
            logger.critical(f"Unhandled exception for {name}: {e}")
            results[name] = "CRITICAL_FAILURE"

    if align_proxy_sessions(list(INDIA_TICKERS.keys())):
        logger.info("India proxy sessions aligned to common weekday dates")
    else:
        logger.error("India proxy session alignment failed")

    results["IN10Y"] = "SUCCESS" if ingest_real_in10y() else "FAILED"
    
    logger.info("Run Complete. Results: " + str(results))

if __name__ == "__main__":
    main()
