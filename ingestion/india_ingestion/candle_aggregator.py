"""Candle Aggregator for WebSocket Ingestion.

Aggregates real-time ticks into 1-minute candles and persists them to Parquet
in the same schema as the existing processed data layer.
"""

import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
import pandas as pd

from .symbol_state import SymbolState

logger = logging.getLogger(__name__)


class CandleAggregator:
    """Aggregates WebSocket ticks into 1-minute candles.
    
    Maintains SymbolState for all subscribed symbols and finalizes candles
    every minute on the minute boundary. Persists candles to Parquet files
    compatible with existing processed data schema.
    """
    
    def __init__(
        self,
        processed_base_path: str = "data/processed/candles/intraday",
        on_candle_callback: Optional[Callable[[List[Dict]], None]] = None
    ):
        """Initialize the candle aggregator.
        
        Args:
            processed_base_path: Path to save processed Parquet files.
            on_candle_callback: Optional callback function called when candles are finalized.
                                Receives list of candle dicts.
        """
        self.processed_base_path = Path(processed_base_path)
        self.on_candle_callback = on_candle_callback
        
        # Symbol states: {symbol: SymbolState}
        self.states: Dict[str, SymbolState] = {}
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Finalization timer
        self._timer: Optional[threading.Timer] = None
        self._running = False
        
        # Statistics
        self.total_ticks_received = 0
        self.total_candles_generated = 0
        self.last_finalization_time: Optional[datetime] = None
    
    def _ensure_directories(self) -> None:
        """Ensure processed directories exist."""
        self.processed_base_path.mkdir(parents=True, exist_ok=True)
    
    def add_symbol(self, symbol: str, exchange: str = "NSE") -> None:
        """Add a symbol to track.
        
        Args:
            symbol: Trading symbol.
            exchange: Exchange segment.
        """
        with self._lock:
            if symbol not in self.states:
                self.states[symbol] = SymbolState(symbol=symbol, exchange=exchange)
                logger.info(f"Added symbol {symbol} to aggregator")
    
    def remove_symbol(self, symbol: str) -> None:
        """Remove a symbol from tracking.
        
        Args:
            symbol: Trading symbol.
        """
        with self._lock:
            if symbol in self.states:
                del self.states[symbol]
                logger.info(f"Removed symbol {symbol} from aggregator")
    
    def update_tick(self, symbol: str, price: float, volume: int, timestamp: datetime) -> None:
        """Update state with a new tick.
        
        Args:
            symbol: Trading symbol.
            price: Last traded price.
            volume: Volume traded in this tick.
            timestamp: Tick timestamp.
        """
        with self._lock:
            if symbol not in self.states:
                logger.warning(f"Received tick for untracked symbol: {symbol}")
                return
            
            self.states[symbol].update_tick(price, volume, timestamp)
            self.total_ticks_received += 1
    
    def finalize_candles(self) -> List[Dict]:
        """Finalize all current candles and return them.
        
        Returns:
            List of candle dicts ready for persistence.
        """
        candles = []
        
        with self._lock:
            for symbol, state in self.states.items():
                candle = state.finalize_candle()
                if candle:
                    candles.append(candle)
            
            self.total_candles_generated += len(candles)
            self.last_finalization_time = datetime.now()
        
        if candles:
            logger.info(f"Finalized {len(candles)} candles")
            
            # Persist to Parquet
            self._persist_candles(candles)
            
            # Call callback if provided
            if self.on_candle_callback:
                try:
                    self.on_candle_callback(candles)
                except Exception as e:
                    logger.exception(f"Error in candle callback: {e}")
        
        return candles
    
    def _persist_candles(self, candles: List[Dict]) -> None:
        """Persist candles to Parquet files.
        
        Args:
            candles: List of candle dicts.
        """
        if not candles:
            return
        
        self._ensure_directories()
        
        # Group by symbol
        grouped: Dict[str, List[Dict]] = {}
        for candle in candles:
            symbol = candle["symbol"]
            grouped.setdefault(symbol, []).append(candle)
        
        # Persist each symbol
        for symbol, symbol_candles in grouped.items():
            exchange = symbol_candles[0]["exchange"]
            file_path = self.processed_base_path / f"{exchange}_{symbol}_1m.parquet"
            
            try:
                # Convert to DataFrame
                df_new = pd.DataFrame(symbol_candles)
                df_new["timestamp"] = pd.to_datetime(df_new["timestamp"])
                
                # Load existing data if file exists
                if file_path.exists():
                    df_existing = pd.read_parquet(file_path)
                    
                    # Append new candles
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    
                    # Deduplicate (keep last for each timestamp)
                    df_combined = df_combined.sort_values("timestamp")
                    df_combined = df_combined.drop_duplicates(subset=["symbol", "timestamp"], keep="last")
                else:
                    df_combined = df_new
                
                # Save to Parquet
                df_combined.to_parquet(file_path, engine="pyarrow", index=False)
                logger.debug(f"Persisted {len(symbol_candles)} candles for {symbol} to {file_path}")
                
            except Exception as e:
                logger.exception(f"Failed to persist candles for {symbol}: {e}")
    
    def _schedule_next_finalization(self) -> None:
        """Schedule the next candle finalization on the minute boundary."""
        if not self._running:
            return
        
        now = datetime.now()
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        delay = (next_minute - now).total_seconds()
        
        self._timer = threading.Timer(delay, self._on_timer_tick)
        self._timer.daemon = True
        self._timer.start()
        
        logger.debug(f"Scheduled next finalization in {delay:.1f}s at {next_minute}")
    
    def _on_timer_tick(self) -> None:
        """Timer callback to finalize candles."""
        try:
            self.finalize_candles()
        except Exception as e:
            logger.exception(f"Error during candle finalization: {e}")
        finally:
            # Schedule next finalization
            self._schedule_next_finalization()
    
    def start(self) -> None:
        """Start automatic candle finalization timer."""
        if self._running:
            logger.warning("Aggregator already running")
            return
        
        self._running = True
        self._schedule_next_finalization()
        logger.info("Candle aggregator started")
    
    def stop(self) -> None:
        """Stop automatic candle finalization timer."""
        self._running = False
        
        if self._timer:
            self._timer.cancel()
            self._timer = None
        
        # Finalize any remaining candles
        self.finalize_candles()
        
        logger.info("Candle aggregator stopped")
    
    def reset_all_symbols(self) -> None:
        """Reset daily state for all symbols (called at market open)."""
        with self._lock:
            for state in self.states.values():
                state.reset_day()
        logger.info("Reset daily state for all symbols")
    
    def get_stats(self) -> Dict:
        """Get aggregator statistics.
        
        Returns:
            Dict with aggregator statistics.
        """
        with self._lock:
            symbol_stats = {
                symbol: state.get_stats()
                for symbol, state in self.states.items()
            }
        
        return {
            "total_symbols": len(self.states),
            "total_ticks_received": self.total_ticks_received,
            "total_candles_generated": self.total_candles_generated,
            "last_finalization_time": self.last_finalization_time.isoformat() if self.last_finalization_time else None,
            "running": self._running,
            "symbol_stats": symbol_stats,
        }
