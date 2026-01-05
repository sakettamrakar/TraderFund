"""Replay Validator - Instant T+5/T+15 Validation for Historical Replay.

This validator uses historical data to perform instant validation of signals,
looking up future candles that were already recorded.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional
from datetime import timedelta

from .candle_cursor import CandleCursor

logger = logging.getLogger(__name__)


class ReplayValidator:
    """Validates signals instantly using historical candle data.
    
    Unlike live SignalValidator which waits real-time, this validator
    looks up T+5 and T+15 candles immediately from the historical dataset.
    """
    
    def __init__(self, replay_date: str, base_dir: str = "observations/historical_replay"):
        """Initialize the replay validator.
        
        Args:
            replay_date: The date being replayed (YYYY-MM-DD format).
            base_dir: Base directory for replay outputs.
        """
        self.replay_date = replay_date
        self.output_dir = Path(base_dir) / replay_date
        self._cursors: dict = {}  # symbol -> CandleCursor
    
    def register_cursor(self, symbol: str, cursor: CandleCursor):
        """Register a CandleCursor for a symbol to enable T+N lookups.
        
        Args:
            symbol: Trading symbol.
            cursor: CandleCursor containing full day's data for this symbol.
        """
        self._cursors[symbol] = cursor
    
    def _get_price_at_offset(self, symbol: str, timestamp_str: str, offset_mins: int) -> Optional[tuple]:
        """Fetch price and volume at T + offset_mins.
        
        Args:
            symbol: Trading symbol.
            timestamp_str: Base timestamp (ISO format).
            offset_mins: Minutes to offset.
            
        Returns:
            Tuple of (close_price, volume) or None if not found.
        """
        cursor = self._cursors.get(symbol)
        if not cursor:
            logger.warning(f"No cursor registered for {symbol}")
            return None
        
        candles = cursor.get_candles_at(timestamp_str, offset_mins)
        if not candles.empty:
            row = candles.iloc[0]
            return float(row['close']), float(row['volume'])
        
        return None
    
    def validate_signals(self):
        """Run validation on all signals in the replay output file.
        
        This performs instant T+5 and T+15 validation using historical data.
        """
        file_path = self.output_dir / f"signals_for_review_{self.replay_date}.csv"
        
        if not file_path.exists():
            logger.info(f"No signals file found for {self.replay_date}")
            return
        
        df = pd.read_csv(file_path)
        if df.empty:
            logger.info("No signals to validate")
            return
        
        # Ensure string columns are object type
        for col in ['outcome', 'volume_continuation', 'classification']:
            if col in df.columns:
                df[col] = df[col].astype(object)
        
        updated = False
        
        for idx, row in df.iterrows():
            symbol = row['symbol']
            timestamp = row['timestamp']
            
            # Skip if already fully validated
            if pd.notna(row['price_t15']) and row['price_t15'] != "":
                continue
            
            # T+5 validation
            if pd.isna(row['price_t5']) or row['price_t5'] == "":
                result = self._get_price_at_offset(symbol, timestamp, 5)
                if result:
                    p5, v5 = result
                    df.at[idx, 'price_t5'] = p5
                    
                    p0 = float(row['price_t0']) if pd.notna(row['price_t0']) else p5
                    v0 = float(row['volume_t0']) if pd.notna(row['volume_t0']) else v5
                    df.at[idx, 'volume_t5_change'] = round(((v5 - v0) / v0 * 100), 2) if v0 > 0 else 0
                    updated = True
            
            # T+15 validation
            if pd.isna(row['price_t15']) or row['price_t15'] == "":
                result = self._get_price_at_offset(symbol, timestamp, 15)
                if result:
                    p15, v15 = result
                    df.at[idx, 'price_t15'] = p15
                    
                    p0 = float(row['price_t0'])
                    p5 = float(df.at[idx, 'price_t5']) if pd.notna(df.at[idx, 'price_t5']) else p0
                    
                    change_15m = (p15 - p0) / p0 * 100
                    if change_15m > 0.3:
                        df.at[idx, 'outcome'] = "Clean"
                    elif change_15m < -0.1:
                        df.at[idx, 'outcome'] = "False"
                    else:
                        df.at[idx, 'outcome'] = "Choppy"
                    
                    vol_change = float(df.at[idx, 'volume_t5_change']) if pd.notna(df.at[idx, 'volume_t5_change']) else 0
                    df.at[idx, 'volume_continuation'] = "Surge" if vol_change > 50 else "Steady"
                    updated = True
        
        if updated:
            df.to_csv(file_path, index=False)
            logger.info(f"Validated signals in {file_path}")
