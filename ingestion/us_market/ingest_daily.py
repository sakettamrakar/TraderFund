
import os
import sys
import logging
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root
sys.path.append(os.getcwd())

from ingestion.api_ingestion.alpha_vantage.client import AlphaVantageClient
from ingestion.api_ingestion.alpha_vantage.key_pool import KeyPoolManager

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("USIngestion")

class USMarketIngestor:
    SYMBOLS = ["SPY", "QQQ", "IWM", "VIXY"]
    DATA_DIR = Path("data/us_market")

    def __init__(self):
        self.key_pool = KeyPoolManager()
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_history(self, symbol: str) -> pd.DataFrame:
        path = self.DATA_DIR / f"{symbol}_daily.csv"
        if path.exists():
            try:
                df = pd.read_csv(path)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
            except Exception as e:
                logger.error(f"Corrupt history for {symbol}: {e}")
                return pd.DataFrame()
        return pd.DataFrame()

    def _save_history(self, symbol: str, df: pd.DataFrame):
        path = self.DATA_DIR / f"{symbol}_daily.csv"
        # Sort and deduplicate
        df = df.sort_values('timestamp').drop_duplicates(subset=['timestamp'], keep='last')
        df.to_csv(path, index=False)
        logger.info(f"Saved {len(df)} bars for {symbol}")

    def ingest_symbol(self, symbol: str):
        logger.info(f"Ingesting {symbol}...")
        
        # 1. Check existing state
        df_hist = self._load_history(symbol)
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
