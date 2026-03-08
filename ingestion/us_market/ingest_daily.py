
import os
import sys
import logging
import pandas as pd
import time
import yfinance as yf
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root
sys.path.append(os.getcwd())

from ingestion.api_ingestion.alpha_vantage.client import AlphaVantageClient
from ingestion.api_ingestion.alpha_vantage.key_pool import KeyPoolManager
from traderfund.validation.validation_runner import ValidationRunner

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("USIngestion")

class USMarketIngestor:
    SYMBOLS = ["SPY", "QQQ", "IWM", "VIXY", "TNX"]
    DATA_DIR = Path("data/us_market")
    REGIME_DIR = Path("data/regime/raw")

    def __init__(self):
        self.key_pool = KeyPoolManager()
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.REGIME_DIR.mkdir(parents=True, exist_ok=True)

    def _history_path(self, symbol: str) -> Path:
        if symbol == "TNX":
            return self.REGIME_DIR / "^TNX.csv"
        return self.DATA_DIR / f"{symbol}_daily.csv"

    def _date_column(self, symbol: str) -> str:
        return "date" if symbol == "TNX" else "timestamp"

    def _load_history(self, symbol: str) -> pd.DataFrame:
        path = self._history_path(symbol)
        date_col = self._date_column(symbol)
        if path.exists():
            try:
                df = pd.read_csv(path)
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col])
                return df
            except Exception as e:
                logger.error(f"Corrupt history for {symbol}: {e}")
                return pd.DataFrame()
        return pd.DataFrame()

    def _save_history(self, symbol: str, df: pd.DataFrame):
        path = self._history_path(symbol)
        date_col = self._date_column(symbol)
        # Sort and deduplicate
        df = df.sort_values(date_col).drop_duplicates(subset=[date_col], keep='last')
        df.to_csv(path, index=False)
        logger.info(f"Saved {len(df)} bars for {symbol}")

    def _fetch_tnx_history(self, start_date: str | None) -> pd.DataFrame:
        logger.info("Refreshing TNX via yfinance fallback (^TNX)...")
        df = yf.download("^TNX", start=start_date or "2020-01-01", progress=False, auto_adjust=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index().rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
        df["symbol"] = "^TNX"
        return df[["date", "symbol", "open", "high", "low", "close", "volume"]].dropna(subset=["date"])

    def ingest_symbol(self, symbol: str):
        logger.info(f"Ingesting {symbol}...")
        
        # 1. Check existing state
        df_hist = self._load_history(symbol)

        if symbol == "TNX":
            start_date = None
            if not df_hist.empty and "date" in df_hist.columns:
                start_date = (df_hist["date"].max() - pd.Timedelta(days=14)).strftime("%Y-%m-%d")
            df_new = self._fetch_tnx_history(start_date)
            if df_new.empty:
                logger.error("TNX refresh failed: no data returned from yfinance")
                return
            df_final = pd.concat([df_hist, df_new]) if not df_hist.empty else df_new
            self._save_history(symbol, df_final)
            return

        # Force compact for Free Tier compatibility (100 bars)
        output_size = 'compact' 
        
        logger.info(f"Existing bars: {len(df_hist)}. Fetching {output_size}...")

        # 2. Key Management
        try:
            key = self.key_pool.get_key()
            logger.info(f"Using key ending in ...{key[-4:]}")
        except Exception as e:
            logger.error(f"Key Pool Exhausted: {e}")
            return

        # 3. Fetch
        client = AlphaVantageClient(api_key=key)
        try:
            data = client.get_daily(symbol, outputsize=output_size)
            
            # Check for API Errors
            if "Note" in data:
                logger.warning(f"API Note: {data['Note']}")
                if "Thank you" in data['Note']: # Rate limit
                    self.key_pool.mark_failure(key)
                    return 

            if "Error Message" in data:
                logger.error(f"API Error: {data['Error Message']}")
                return

            if "Time Series (Daily)" not in data:
                 logger.error(f"Invalid response keys: {list(data.keys())}")
                 if "Information" in data:
                     logger.error(f"API Info: {data['Information']}")
                 return

            # 4. Normalize
            records = []
            for ts_str, metrics in data["Time Series (Daily)"].items():
                records.append({
                    "timestamp": pd.to_datetime(ts_str),
                    "open": float(metrics["1. open"]),
                    "high": float(metrics["2. high"]),
                    "low": float(metrics["3. low"]),
                    "close": float(metrics["4. close"]),
                    "volume": int(metrics["5. volume"])
                })
            
            df_new = pd.DataFrame(records)
            
            # 5. Merge & Persist
            if not df_hist.empty:
                df_final = pd.concat([df_hist, df_new])
            else:
                df_final = df_new
                
            self._save_history(symbol, df_final)

        except Exception as e:
            logger.error(f"Ingestion failed for {symbol}: {e}")
            self.key_pool.mark_failure(key)

    def run_all(self):
        for sym in self.SYMBOLS:
            self.ingest_symbol(sym)
            time.sleep(1) # Gentle pacing

if __name__ == "__main__":
    ingestor = USMarketIngestor()
    ingestor.run_all()
    ValidationRunner().run_post_ingestion(
        {
            "source": "ingestion.us_market.ingest_daily",
            "symbols": list(USMarketIngestor.SYMBOLS),
        }
    )
