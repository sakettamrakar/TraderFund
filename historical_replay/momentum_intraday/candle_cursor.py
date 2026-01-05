"""Candle Cursor - Lookahead Prevention Abstraction.

This module provides the CandleCursor class which is the KEY abstraction
for preventing future data leakage during historical replay.
"""

import pandas as pd
from typing import List
import logging

logger = logging.getLogger(__name__)


class CandleCursor:
    """Exposes intraday candles progressively up to a given timestamp.
    
    This is the core abstraction for preventing lookahead bias. At any point
    in the replay, only candles with timestamp <= T are accessible.
    
    Attributes:
        _full_df: The complete DataFrame of candles for the day (immutable).
        _timestamps: Ordered list of all candle timestamps.
    """
    
    def __init__(self, df: pd.DataFrame):
        """Initialize the cursor with a full day of candles.
        
        Args:
            df: DataFrame containing 1-minute candles with 'timestamp' column.
                Must contain columns: timestamp, open, high, low, close, volume.
        """
        if df.empty:
            raise ValueError("Cannot initialize CandleCursor with empty DataFrame")
        
        if 'timestamp' not in df.columns:
            raise ValueError("DataFrame must contain 'timestamp' column")
        
        # Sort by timestamp and freeze the data
        self._full_df = df.sort_values('timestamp').reset_index(drop=True).copy()
        self._full_df['timestamp'] = pd.to_datetime(self._full_df['timestamp'])
        self._timestamps = self._full_df['timestamp'].tolist()
        
        logger.debug(f"CandleCursor initialized with {len(self._timestamps)} candles")
        logger.debug(f"Time range: {self._timestamps[0]} to {self._timestamps[-1]}")
    
    def get_candles_up_to(self, timestamp: pd.Timestamp) -> pd.DataFrame:
        """Return only candles with timestamp <= T.
        
        This is the primary method for lookahead prevention. No matter what,
        this method will NEVER return future candles.
        
        Args:
            timestamp: The current evaluation timestamp.
            
        Returns:
            DataFrame containing only candles <= timestamp.
        """
        # Ensure timestamp is pandas Timestamp
        ts = pd.to_datetime(timestamp)
        
        # Filter to only past/current candles
        mask = self._full_df['timestamp'] <= ts
        filtered = self._full_df[mask].copy()
        
        logger.debug(f"get_candles_up_to({ts}): returning {len(filtered)} of {len(self._full_df)} candles")
        
        return filtered
    
    def get_candles_at(self, timestamp: pd.Timestamp, offset_minutes: int = 0) -> pd.DataFrame:
        """Return candles at a specific timestamp with optional offset.
        
        Useful for T+5 and T+15 lookups during validation.
        
        Args:
            timestamp: Base timestamp.
            offset_minutes: Minutes to add to timestamp.
            
        Returns:
            Single-row DataFrame or empty if not found.
        """
        target = pd.to_datetime(timestamp) + pd.Timedelta(minutes=offset_minutes)
        mask = self._full_df['timestamp'] == target
        return self._full_df[mask].copy()
    
    def get_all_timestamps(self) -> List[pd.Timestamp]:
        """Return ordered list of all candle timestamps for iteration.
        
        Use this to drive the replay loop.
        
        Returns:
            List of timestamps in chronological order.
        """
        return self._timestamps.copy()
    
    def get_market_open_time(self) -> pd.Timestamp:
        """Return the first timestamp (approximate market open)."""
        return self._timestamps[0]
    
    def get_market_close_time(self) -> pd.Timestamp:
        """Return the last timestamp (approximate market close)."""
        return self._timestamps[-1]
    
    @property
    def total_candles(self) -> int:
        """Total number of candles in the cursor."""
        return len(self._timestamps)
