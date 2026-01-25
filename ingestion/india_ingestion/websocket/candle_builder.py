"""Candle Builder for WebSocket Ticks.

Builds 1-minute candles from tick data and emits at minute boundaries.
Stores in SAME schema as existing processed data.
"""

import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from .symbol_state import SymbolState

logger = logging.getLogger(__name__)


class CandleBuilder:
    """Builds 1-minute candles from WebSocket ticks."""
    
    def __init__(self, output_path: str = "data/test/websocket_candles"):
        """Initialize candle builder.
        
        Args:
            output_path: Path to save test candles.
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Symbol states
        self.states: Dict[str, SymbolState] = {}
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Timer for minute-boundary finalization
        self._timer: Optional[threading.Timer] = None
        self._running = False
        
        # Statistics
        self.total_ticks = 0
        self.total_candles = 0
        self.last_finalization: Optional[datetime] = None
    
    def add_symbol(self, symbol: str, exchange: str = "NSE") -> None:
        """Add symbol to track."""
        with self._lock:
            if symbol not in self.states:
                self.states[symbol] = SymbolState(symbol=symbol, exchange=exchange)
                logger.info("Added symbol: %s", symbol)
    
    def update_tick(self, symbol: str, price: float, volume: int, timestamp: datetime) -> None:
        """Update with new tick."""
        with self._lock:
            if symbol not in self.states:
                self.add_symbol(symbol)
            
            self.states[symbol].update_tick(price, volume, timestamp)
            self.total_ticks += 1
            
            # Log first few ticks for validation
            if self.total_ticks <= 5:
                logger.info("✓ Tick processed: %s @ %.2f (vol: %d)", symbol, price, volume)
    
    def finalize_candles(self) -> List[Dict]:
        """Finalize all current candles."""
        candles = []
        
        with self._lock:
            for symbol, state in self.states.items():
                candle = state.finalize_candle()
                if candle:
                    candles.append(candle)
            
            self.total_candles += len(candles)
            self.last_finalization = datetime.now()
        
        if candles:
            logger.info("✓ Finalized %d candles", len(candles))
            self._persist_candles(candles)
        
        return candles
    
    def _persist_candles(self, candles: List[Dict]) -> None:
        """Persist candles to Parquet (test output)."""
        if not candles:
            return
        
        # Group by symbol
        grouped: Dict[str, List[Dict]] = {}
        for candle in candles:
            symbol = candle["symbol"]
            grouped.setdefault(symbol, []).append(candle)
        
        # Save each symbol
        for symbol, symbol_candles in grouped.items():
            exchange = symbol_candles[0]["exchange"]
            file_path = self.output_path / f"{exchange}_{symbol}_1m_test.parquet"
            
            try:
                df_new = pd.DataFrame(symbol_candles)
                df_new["timestamp"] = pd.to_datetime(df_new["timestamp"])
                
                # Append if exists
                if file_path.exists():
                    df_existing = pd.read_parquet(file_path)
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined = df_combined.drop_duplicates(subset=["symbol", "timestamp"], keep="last")
                else:
                    df_combined = df_new
                
                df_combined.to_parquet(file_path, engine="pyarrow", index=False)
                logger.debug("Saved %d candles for %s to %s", len(symbol_candles), symbol, file_path)
                
            except Exception as e:
                logger.exception("Failed to save candles for %s: %s", symbol, e)
    
    def _schedule_next_finalization(self) -> None:
        """Schedule next minute-boundary finalization."""
        if not self._running:
            return
        
        now = datetime.now()
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        delay = (next_minute - now).total_seconds()
        
        self._timer = threading.Timer(delay, self._on_timer)
        self._timer.daemon = True
        self._timer.start()
    
    def _on_timer(self) -> None:
        """Timer callback."""
        try:
            self.finalize_candles()
        except Exception as e:
            logger.exception("Error during finalization: %s", e)
        finally:
            self._schedule_next_finalization()
    
    def start(self) -> None:
        """Start automatic finalization."""
        if self._running:
            return
        
        self._running = True
        self._schedule_next_finalization()
        logger.info("✓ Candle builder started (minute-boundary finalization)")
    
    def stop(self) -> None:
        """Stop automatic finalization."""
        self._running = False
        
        if self._timer:
            self._timer.cancel()
            self._timer = None
        
        # Final finalization
        self.finalize_candles()
        logger.info("✓ Candle builder stopped")
    
    def get_stats(self) -> Dict:
        """Get statistics."""
        with self._lock:
            return {
                "total_symbols": len(self.states),
                "total_ticks": self.total_ticks,
                "total_candles": self.total_candles,
                "last_finalization": self.last_finalization.isoformat() if self.last_finalization else None,
                "running": self._running,
            }
