"""Symbol State Management for WebSocket Ingestion.

Maintains in-memory state for each subscribed symbol, tracking tick-level
updates and aggregating them into 1-minute candles.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SymbolState:
    """In-memory state for a single symbol.
    
    Tracks real-time tick updates and aggregates them into 1-minute candles.
    Maintains daily aggregates (HOD, VWAP) for momentum calculations.
    """
    
    symbol: str
    exchange: str
    
    # Current tick data
    last_price: float = 0.0
    last_tick_time: Optional[datetime] = None
    
    # Daily aggregates
    cumulative_volume: int = 0
    vwap_numerator: float = 0.0  # sum(price * volume)
    vwap_denominator: float = 0.0  # sum(volume)
    high_of_day: float = 0.0
    low_of_day: float = float('inf')
    
    # Current 1-minute candle (in progress)
    current_1m_open: float = 0.0
    current_1m_high: float = 0.0
    current_1m_low: float = float('inf')
    current_1m_close: float = 0.0
    current_1m_volume: int = 0
    current_candle_start: Optional[datetime] = None
    
    # Metadata
    tick_count: int = 0
    candles_generated: int = 0
    
    def update_tick(self, price: float, volume: int, timestamp: datetime) -> None:
        """Update state with a new tick.
        
        Args:
            price: Last traded price
            volume: Volume traded in this tick
            timestamp: Tick timestamp
        """
        self.last_price = price
        self.last_tick_time = timestamp
        self.tick_count += 1
        
        # Update daily aggregates
        self.cumulative_volume += volume
        self.vwap_numerator += price * volume
        self.vwap_denominator += volume
        
        if price > self.high_of_day:
            self.high_of_day = price
        if price < self.low_of_day:
            self.low_of_day = price
        
        # Initialize current candle if needed
        candle_minute = timestamp.replace(second=0, microsecond=0)
        if self.current_candle_start is None or self.current_candle_start != candle_minute:
            # New candle period started
            if self.current_candle_start is not None:
                logger.warning(
                    f"{self.symbol}: Tick received for new candle period before finalization. "
                    f"Previous candle: {self.current_candle_start}, New tick: {candle_minute}"
                )
            self.current_candle_start = candle_minute
            self.current_1m_open = price
            self.current_1m_high = price
            self.current_1m_low = price
            self.current_1m_close = price
            self.current_1m_volume = volume
        else:
            # Update current candle
            if price > self.current_1m_high:
                self.current_1m_high = price
            if price < self.current_1m_low:
                self.current_1m_low = price
            self.current_1m_close = price
            self.current_1m_volume += volume
    
    def finalize_candle(self) -> Optional[Dict]:
        """Finalize the current 1-minute candle and return OHLC data.
        
        Returns:
            Dict with candle data in schema-compatible format, or None if no data.
        """
        if self.current_candle_start is None or self.current_1m_volume == 0:
            # No data to finalize
            return None
        
        candle = {
            "symbol": self.symbol,
            "exchange": self.exchange,
            "timestamp": self.current_candle_start,
            "open": float(self.current_1m_open),
            "high": float(self.current_1m_high),
            "low": float(self.current_1m_low),
            "close": float(self.current_1m_close),
            "volume": int(self.current_1m_volume),
        }
        
        # Reset current candle (but keep daily aggregates)
        self.current_1m_open = 0.0
        self.current_1m_high = 0.0
        self.current_1m_low = float('inf')
        self.current_1m_close = 0.0
        self.current_1m_volume = 0
        self.current_candle_start = None
        
        self.candles_generated += 1
        
        return candle
    
    def reset_day(self) -> None:
        """Reset daily aggregates (called at market open)."""
        self.cumulative_volume = 0
        self.vwap_numerator = 0.0
        self.vwap_denominator = 0.0
        self.high_of_day = 0.0
        self.low_of_day = float('inf')
        self.tick_count = 0
        self.candles_generated = 0
        
        # Also reset current candle
        self.current_1m_open = 0.0
        self.current_1m_high = 0.0
        self.current_1m_low = float('inf')
        self.current_1m_close = 0.0
        self.current_1m_volume = 0
        self.current_candle_start = None
        
        logger.info(f"{self.symbol}: Daily state reset")
    
    def get_vwap(self) -> float:
        """Calculate current VWAP.
        
        Returns:
            VWAP value, or 0.0 if no volume traded.
        """
        if self.vwap_denominator == 0:
            return 0.0
        return self.vwap_numerator / self.vwap_denominator
    
    def get_stats(self) -> Dict:
        """Get current state statistics.
        
        Returns:
            Dict with state statistics for monitoring.
        """
        return {
            "symbol": self.symbol,
            "last_price": self.last_price,
            "tick_count": self.tick_count,
            "candles_generated": self.candles_generated,
            "cumulative_volume": self.cumulative_volume,
            "vwap": self.get_vwap(),
            "high_of_day": self.high_of_day,
            "low_of_day": self.low_of_day if self.low_of_day != float('inf') else 0.0,
            "last_tick_time": self.last_tick_time.isoformat() if self.last_tick_time else None,
        }
