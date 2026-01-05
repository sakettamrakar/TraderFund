"""Replay Controller - Orchestrates Minute-by-Minute Historical Replay.

This module drives the replay loop, feeding candles progressively to the
momentum engine and logging signals.
"""

import sys
import pandas as pd
import logging
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core_modules.momentum_engine.momentum_engine import MomentumEngine
from .candle_cursor import CandleCursor
from .replay_logger import ReplayLogger
from .replay_validator import ReplayValidator

logger = logging.getLogger(__name__)


class ReplayController:
    """Orchestrates minute-by-minute replay of historical intraday data.
    
    This controller:
    1. Loads historical parquet data for a symbol/date
    2. Initializes a CandleCursor for lookahead prevention
    3. Iterates through each candle timestamp
    4. At each step, feeds candles up to current time to momentum engine
    5. Logs any generated signals
    
    WARNING: This is for DIAGNOSTIC purposes only.
    """
    
    MODE = "HISTORICAL_REPLAY"
    
    def __init__(
        self,
        symbol: str,
        replay_date: str,
        interval_minutes: int = 1,
        processed_data_path: str = "data/processed/candles/intraday",
        exchange: str = "NSE"
    ):
        """Initialize the replay controller.
        
        Args:
            symbol: Trading symbol to replay.
            replay_date: Date to replay (YYYY-MM-DD format).
            interval_minutes: Evaluation interval (default: 1 minute).
            processed_data_path: Path to processed parquet files.
            exchange: Exchange segment.
        """
        self.symbol = symbol
        self.replay_date = replay_date
        self.interval = interval_minutes
        self.exchange = exchange
        self.data_path = Path(processed_data_path)
        
        # Initialize components
        self.engine = MomentumEngine()
        self.replay_logger = ReplayLogger(replay_date)
        self.replay_validator = ReplayValidator(replay_date)
        
        # Will be set during run()
        self._cursor: Optional[CandleCursor] = None
        self._signals_generated = 0
        
        # Safety check
        self._validate_replay_mode()
    
    def _validate_replay_mode(self):
        """Ensure we're in replay mode and not accidentally calling live APIs."""
        # This is a safety guard - in replay mode, we should NEVER touch broker APIs
        logger.info(f"[{self.MODE}] Replay controller initialized for {self.symbol} on {self.replay_date}")
        logger.info(f"[{self.MODE}] Live ingestion is DISABLED in this mode")
    
    def _load_historical_data(self) -> pd.DataFrame:
        """Load historical parquet data for the symbol and filter to replay date.
        
        Returns:
            DataFrame containing candles for the replay date only.
        """
        file_path = self.data_path / f"{self.exchange}_{self.symbol}_1m.parquet"
        
        if not file_path.exists():
            raise FileNotFoundError(f"No processed data found: {file_path}")
        
        df = pd.read_parquet(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter to the specific replay date
        df['date'] = df['timestamp'].dt.date.astype(str)
        df_filtered = df[df['date'] == self.replay_date].copy()
        df_filtered.drop(columns=['date'], inplace=True)
        
        if df_filtered.empty:
            raise ValueError(f"No data found for {self.symbol} on {self.replay_date}")
        
        logger.info(f"Loaded {len(df_filtered)} candles for {self.symbol} on {self.replay_date}")
        return df_filtered
    
    def run(self) -> dict:
        """Execute the full replay for the trading day.
        
        Returns:
            Dict with replay statistics.
        """
        logger.info(f"[{self.MODE}] Starting replay for {self.symbol} on {self.replay_date}")
        
        # 1. Load historical data
        df = self._load_historical_data()
        
        # 2. Initialize cursor
        self._cursor = CandleCursor(df)
        
        # Register cursor with validator for T+N lookups
        self.replay_validator.register_cursor(self.symbol, self._cursor)
        
        # 3. Get all timestamps for iteration
        timestamps = self._cursor.get_all_timestamps()
        
        # 4. Filter to evaluation interval
        eval_timestamps = timestamps[::self.interval]
        
        logger.info(f"[{self.MODE}] Replaying {len(eval_timestamps)} evaluation points (interval={self.interval}m)")
        
        # 5. Main replay loop
        for idx, ts in enumerate(eval_timestamps):
            # Get candles up to this timestamp (NO LOOKAHEAD)
            candles_up_to_now = self._cursor.get_candles_up_to(ts)
            
            # Run momentum engine with filtered data
            signals = self.engine.generate_signals_from_df(
                candles_up_to_now,
                self.symbol,
                self.exchange
            )
            
            # Log any signals
            for sig in signals:
                self.replay_logger.log_signal(sig.to_dict())
                self._signals_generated += 1
            
            # Progress logging (every 10%)
            if (idx + 1) % max(1, len(eval_timestamps) // 10) == 0:
                pct = (idx + 1) / len(eval_timestamps) * 100
                logger.info(f"[{self.MODE}] Progress: {pct:.0f}% ({idx + 1}/{len(eval_timestamps)})")
        
        logger.info(f"[{self.MODE}] Replay complete. Generated {self._signals_generated} signals.")
        
        # 6. Run instant validation
        logger.info(f"[{self.MODE}] Running T+5/T+15 validation...")
        self.replay_validator.validate_signals()
        
        return {
            "symbol": self.symbol,
            "date": self.replay_date,
            "total_candles": self._cursor.total_candles,
            "evaluation_points": len(eval_timestamps),
            "signals_generated": self._signals_generated,
            "output_file": str(self.replay_logger.get_review_file_path())
        }
    
    @property
    def signals_generated(self) -> int:
        """Number of signals generated during replay."""
        return self._signals_generated
