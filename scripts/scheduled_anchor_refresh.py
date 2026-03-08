"""
Scheduled Anchor Refresh
========================
Refreshes ONLY structural (ANCHOR) datasets that do not need daily updates.
This protects them from redundant API calls and processing overhead.

Pipeline Steps:
1. Refresh Regime Anchors from yfinance (SPY, QQQ, VIX, HYG, LQD, ^TNX, ^TYX) -> data/regime/raw/
2. Refresh India 10Y Yield from FRED (IN10Y) -> data/india/IN10Y.csv
"""
import sys, time, logging
from pathlib import Path
import pandas as pd
import yfinance as yf

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("AnchorRefresh")

def refresh_regime_anchors():
    REGIME_DIR = PROJECT_ROOT / "data" / "regime" / "raw"
    REGIME_DIR.mkdir(parents=True, exist_ok=True)
    
    symbols = {
        "SPY": "SPY", "QQQ": "QQQ", "VIX": "^VIX",
        "HYG": "HYG", "LQD": "LQD", "^TYX": "^TYX", "^TNX": "^TNX"
    }
    
    for file_sym, yf_sym in symbols.items():
        out_path = REGIME_DIR / f"{file_sym}.csv"
        start_date = "2021-01-01"
        
        try:
            if out_path.exists():
                existing = pd.read_csv(out_path)
                if "date" in existing.columns:
                    last = pd.to_datetime(existing["date"]).max()
                    start_date = (last - pd.Timedelta(days=3)).strftime("%Y-%m-%d")
                    
            logger.info(f"Fetching {yf_sym} from {start_date}...")
            df = yf.download(yf_sym, start=start_date, progress=False, auto_adjust=False)
            
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.reset_index().rename(columns={
                    "Date": "date", "Open": "open", "High": "high",
                    "Low": "low", "Close": "close", "Volume": "volume"
                })
                df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
                df["symbol"] = file_sym
                df = df[["date", "symbol", "open", "high", "low", "close", "volume"]].dropna(subset=["date"])
                
                if out_path.exists():
                    existing["date"] = pd.to_datetime(existing["date"], errors="coerce").dt.normalize()
                    df = pd.concat([existing, df])
                    
                df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
                df.to_csv(out_path, index=False)
                logger.info(f"✅ {file_sym} anchor refreshed. Rows={len(df)}")
            else:
                logger.warning(f"⚠️ {file_sym}: No data returned")
        except Exception as e:
            logger.error(f"❌ Failed to refresh anchor {file_sym}: {e}")
        time.sleep(1)

def refresh_india_in10y():
    from scripts.india_in10y_fred_ingestion import ingest_india_10y
    try:
        output_path = ingest_india_10y()
        logger.info(f"✅ India 10Y anchor refreshed at {output_path}")
    except Exception as e:
        logger.error(f"❌ Failed to refresh India IN10Y: {e}")

def main(*args, **kwargs):
    logger.info("Starting Weekly Anchor Data Refresh...")
    refresh_regime_anchors()
    refresh_india_in10y()
    logger.info("Weekly Anchor Data Refresh Complete.")
    return True

if __name__ == "__main__":
    main()
