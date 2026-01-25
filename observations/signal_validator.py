"""Signal Post-Validation Utility.

This script monitors the signal log and validates price action 5-15 minutes
after a signal was generated.
"""

import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SignalValidator")

class SignalValidator:
    def __init__(self, review_dir: str = "observations/signal_reviews"):
        self.review_dir = Path(review_dir)
        self.processed_data_path = Path("data/processed/candles/intraday")

    def _get_latest_review_file(self) -> Optional[Path]:
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = self.review_dir / f"signals_for_review_{date_str}.csv"
        return file_path if file_path.exists() else None

    def _get_price_at_timestamp(self, symbol: str, timestamp_str: str, offset_mins: int = 0) -> Optional[tuple]:
        """Fetch price and volume for a symbol at T + offset_mins."""
        file_path = self.processed_data_path / f"NSE_{symbol}_1m.parquet"
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_parquet(file_path)
            target_time = pd.to_datetime(timestamp_str) + timedelta(minutes=offset_mins)
            
            # Ensure target_time matches df['timestamp'] timezone awareness
            if df['timestamp'].dt.tz is not None:
                if target_time.tzinfo is None:
                    target_time = target_time.tz_localize('Asia/Kolkata')
                else:
                    target_time = target_time.tz_convert(df['timestamp'].dt.tz)
            else:
                if target_time.tzinfo is not None:
                    target_time = target_time.tz_localize(None)

            # Find the closest candle at or after target_time
            mask = df['timestamp'] >= target_time
            matches = df[mask]
            
            if not matches.empty:
                latest = matches.iloc[0]
                return float(latest['close']), float(latest['volume'])
        except Exception as e:
            logger.error(f"Error reading data for {symbol}: {e}")
        
        return None

    def validate_signals(self):
        file_path = self._get_latest_review_file()
        if not file_path:
            logger.info("No review file found for today.")
            return

        df = pd.read_csv(file_path)
        if df.empty:
            return

        # Ensure columns that might store strings are object type to avoid warnings
        for col in ['outcome', 'volume_continuation', 'classification']:
            if col in df.columns:
                df[col] = df[col].astype(object)

        updated = False
        
        for idx, row in df.iterrows():
            # Skip if already fully validated
            if pd.notna(row['price_t15']) and row['price_t15'] != "":
                continue

            sig_time = pd.to_datetime(row['timestamp'])
            
            # Ensure 'now' matches sig_time's awareness
            if sig_time.tzinfo is not None:
                now = pd.Timestamp.now(tz=sig_time.tzinfo)
            else:
                now = pd.Timestamp.now()

            # 5-minute validation
            if pd.isna(row['price_t5']) or row['price_t5'] == "":
                if now >= sig_time + timedelta(minutes=5):
                    result = self._get_price_at_timestamp(row['symbol'], row['timestamp'], 5)
                    if result:
                        p5, v5 = result
                        df.at[idx, 'price_t5'] = p5
                        # Volume change relative to T0
                        p0 = float(row['price_t0']) if pd.notna(row['price_t0']) else p5
                        v0 = float(row['volume_t0']) if pd.notna(row['volume_t0']) else v5
                        df.at[idx, 'volume_t5_change'] = round(((v5 - v0) / v0 * 100), 2) if v0 > 0 else 0
                        updated = True

            # 15-minute validation
            if pd.isna(row['price_t15']) or row['price_t15'] == "":
                if now >= sig_time + timedelta(minutes=15):
                    result = self._get_price_at_timestamp(row['symbol'], row['timestamp'], 15)
                    if result:
                        p15, v15 = result
                        df.at[idx, 'price_t15'] = p15
                        
                        # Apply naive outcome classification
                        p0 = float(row['price_t0'])
                        p5 = float(df.at[idx, 'price_t5'])
                        
                        change_15m = (p15 - p0) / p0 * 100
                        if change_15m > 0.3:
                            df.at[idx, 'outcome'] = "Clean"
                        elif change_15m < -0.1:
                            df.at[idx, 'outcome'] = "False"
                        else:
                            df.at[idx, 'outcome'] = "Choppy"
                            
                        df.at[idx, 'volume_continuation'] = "Surge" if float(df.at[idx, 'volume_t5_change']) > 50 else "Steady"
                        updated = True

        if updated:
            df.to_csv(file_path, index=False)
            logger.info(f"Updated {file_path} with new validation data.")

    def run_continually(self, interval_sec: int = 60):
        logger.info(f"Starting Signal Validator (Poll interval: {interval_sec}s)")
        while True:
            self.validate_signals()
            time.sleep(interval_sec)

if __name__ == "__main__":
    validator = SignalValidator()
    validator.run_continually()
