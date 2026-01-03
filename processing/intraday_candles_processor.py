"""Intraday Candles Processor.

This module processes raw JSONL market data from Angel One SmartAPI
into a clean, deterministic, and idempotent Parquet layer.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class IntradayCandlesProcessor:
    """Processes raw intraday OHLC data into cleaned Parquet files."""

    def __init__(
        self,
        raw_base_path: str = "data/raw/api_based/angel/intraday_ohlc",
        processed_base_path: str = "data/processed/candles/intraday"
    ):
        """Initialize the processor.

        Args:
            raw_base_path: Path to raw JSONL files.
            processed_base_path: Path to save processed Parquet files.
        """
        self.raw_base_path = Path(raw_base_path)
        self.processed_base_path = Path(processed_base_path)
        self.schema_columns = [
            "symbol", "exchange", "timestamp", "open", "high", "low", "close", "volume"
        ]

    def _ensure_directories(self) -> None:
        """Ensure processed directories exist."""
        self.processed_base_path.mkdir(parents=True, exist_ok=True)

    def _read_raw_files(self, symbol: str, exchange: str) -> pd.DataFrame:
        """Read all raw JSONL files for a given symbol and exchange.

        Args:
            symbol: Trading symbol.
            exchange: Exchange segment.

        Returns:
            DataFrame containing all raw records.
        """
        pattern = f"{exchange}_{symbol}_*.jsonl"
        files = list(self.raw_base_path.glob(pattern))
        
        if not files:
            logger.warning(f"No raw files found for {exchange}:{symbol}")
            return pd.DataFrame()

        all_records = []
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            all_records.append(json.loads(line))
            except (IOError, json.JSONDecodeError) as exc:
                logger.error(f"Error reading {file_path}: {exc}")

        return pd.DataFrame(all_records)

    def process_symbol(self, symbol: str, exchange: str = "NSE") -> bool:
        """Process raw data for a single symbol and save to Parquet.

        Args:
            symbol: Trading symbol.
            exchange: Exchange segment.

        Returns:
            True if successful, False otherwise.
        """
        logger.info(f"Processing {exchange}:{symbol}")
        
        df_raw = self._read_raw_files(symbol, exchange)
        if df_raw.empty:
            return False

        # 1. Validate Schema & Extract required columns
        # Check if all required columns exist
        missing_cols = [col for col in self.schema_columns if col not in df_raw.columns]
        if missing_cols:
            logger.error(f"Raw data missing columns for {symbol}: {missing_cols}")
            return False

        # 2. Convert Timestamps
        # Raw timestamp: "2026-01-03T14:13:00+05:30"
        df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])
        
        # 3. Handle Duplicates (Idempotency)
        # We sort by ingestion_ts (if it exists) to keep the most recent ingestion for the same candle timestamp
        if "ingestion_ts" in df_raw.columns:
            df_raw = df_raw.sort_values(by=["timestamp", "ingestion_ts"])
        else:
            df_raw = df_raw.sort_values(by=["timestamp"])
            
        # Deduplicate: Keep the last entry for each (symbol, timestamp)
        df_processed = df_raw.drop_duplicates(subset=["symbol", "timestamp"], keep="last")

        # 4. Final Selection & Formatting
        df_processed = df_processed[self.schema_columns].copy()
        df_processed = df_processed.sort_values(by="timestamp")
        
        # Ensure correct types
        df_processed["open"] = df_processed["open"].astype(float)
        df_processed["high"] = df_processed["high"].astype(float)
        df_processed["low"] = df_processed["low"].astype(float)
        df_processed["close"] = df_processed["close"].astype(float)
        df_processed["volume"] = df_processed["volume"].astype(int)

        # 5. Persist to Parquet
        self._ensure_directories()
        output_path = self.processed_base_path / f"{exchange}_{symbol}_1m.parquet"
        
        try:
            # engine='pyarrow' is preferred and now installed
            df_processed.to_parquet(output_path, engine='pyarrow', index=False)
            logger.info(f"Successfully processed {len(df_processed)} candles to {output_path}")
            return True
        except Exception as exc:
            logger.exception(f"Failed to save Parquet for {symbol}: {exc}")
            return False

    def process_all(self, watchlist: Optional[List[str]] = None, exchange: str = "NSE") -> Dict[str, bool]:
        """Process all symbols in the watchlist or all symbols found in raw data.

        Args:
            watchlist: Optional list of symbols.
            exchange: Exchange segment.

        Returns:
            Dict mapping symbol to success status.
        """
        if not watchlist:
            # Discover symbols from file patterns
            files = list(self.raw_base_path.glob(f"{exchange}_*_*.jsonl"))
            watchlist = sorted(list(set(f.name.split("_")[1] for f in files)))

        results = {}
        for symbol in watchlist:
            results[symbol] = self.process_symbol(symbol, exchange)
        
        return results

if __name__ == "__main__":
    # Example execution (can be called via verify script later)
    processor = IntradayCandlesProcessor()
    
    # Symbols from config (would ideally import from config.py)
    watchlist = [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", 
        "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "LT"
    ]
    
    status = processor.process_all(watchlist)
    logger.info(f"Processing complete. Status: {status}")
