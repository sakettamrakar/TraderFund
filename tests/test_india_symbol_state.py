"""Unit tests for SymbolState class."""

import pytest
from datetime import datetime
from ingestion.india_ingestion.symbol_state import SymbolState


class TestSymbolState:
    """Test suite for SymbolState."""
    
    def test_initialization(self):
        """Test SymbolState initialization."""
        state = SymbolState(symbol="RELIANCE", exchange="NSE")
        
        assert state.symbol == "RELIANCE"
        assert state.exchange == "NSE"
        assert state.last_price == 0.0
        assert state.cumulative_volume == 0
        assert state.tick_count == 0
        assert state.candles_generated == 0
    
    def test_update_tick_updates_state(self):
        """Test that update_tick correctly updates state."""
        state = SymbolState(symbol="TCS", exchange="NSE")
        timestamp = datetime(2026, 1, 14, 9, 15, 30)
        
        state.update_tick(price=3500.0, volume=100, timestamp=timestamp)
        
        assert state.last_price == 3500.0
        assert state.cumulative_volume == 100
        assert state.tick_count == 1
        assert state.high_of_day == 3500.0
        assert state.low_of_day == 3500.0
        assert state.current_1m_open == 3500.0
        assert state.current_1m_close == 3500.0
    
    def test_update_tick_aggregates_volume(self):
        """Test that multiple ticks aggregate volume correctly."""
        state = SymbolState(symbol="INFY", exchange="NSE")
        timestamp = datetime(2026, 1, 14, 9, 15, 30)
        
        state.update_tick(price=1500.0, volume=100, timestamp=timestamp)
        state.update_tick(price=1505.0, volume=200, timestamp=timestamp)
        state.update_tick(price=1502.0, volume=150, timestamp=timestamp)
        
        assert state.cumulative_volume == 450
        assert state.current_1m_volume == 450
        assert state.tick_count == 3
    
    def test_update_tick_tracks_high_low(self):
        """Test that high and low are tracked correctly."""
        state = SymbolState(symbol="HDFCBANK", exchange="NSE")
        timestamp = datetime(2026, 1, 14, 9, 15, 30)
        
        state.update_tick(price=1600.0, volume=100, timestamp=timestamp)
        state.update_tick(price=1620.0, volume=100, timestamp=timestamp)  # New high
        state.update_tick(price=1590.0, volume=100, timestamp=timestamp)  # New low
        state.update_tick(price=1610.0, volume=100, timestamp=timestamp)
        
        assert state.high_of_day == 1620.0
        assert state.low_of_day == 1590.0
        assert state.current_1m_high == 1620.0
        assert state.current_1m_low == 1590.0
    
    def test_finalize_candle_returns_ohlc(self):
        """Test that finalize_candle returns correct OHLC."""
        state = SymbolState(symbol="SBIN", exchange="NSE")
        timestamp = datetime(2026, 1, 14, 9, 15, 30)
        
        state.update_tick(price=600.0, volume=100, timestamp=timestamp)
        state.update_tick(price=605.0, volume=200, timestamp=timestamp)
        state.update_tick(price=598.0, volume=150, timestamp=timestamp)
        state.update_tick(price=602.0, volume=100, timestamp=timestamp)
        
        candle = state.finalize_candle()
        
        assert candle is not None
        assert candle["symbol"] == "SBIN"
        assert candle["exchange"] == "NSE"
        assert candle["open"] == 600.0
        assert candle["high"] == 605.0
        assert candle["low"] == 598.0
        assert candle["close"] == 602.0
        assert candle["volume"] == 550
        assert candle["timestamp"] == datetime(2026, 1, 14, 9, 15, 0)
    
    def test_finalize_candle_resets_current_candle(self):
        """Test that finalize_candle resets current candle state."""
        state = SymbolState(symbol="ITC", exchange="NSE")
        timestamp = datetime(2026, 1, 14, 9, 15, 30)
        
        state.update_tick(price=400.0, volume=100, timestamp=timestamp)
        state.finalize_candle()
        
        assert state.current_1m_volume == 0
        assert state.current_candle_start is None
        assert state.candles_generated == 1
        
        # Daily aggregates should NOT be reset
        assert state.cumulative_volume == 100
        assert state.high_of_day == 400.0
    
    def test_finalize_candle_returns_none_if_no_data(self):
        """Test that finalize_candle returns None if no data."""
        state = SymbolState(symbol="LT", exchange="NSE")
        
        candle = state.finalize_candle()
        
        assert candle is None
    
    def test_reset_day_clears_aggregates(self):
        """Test that reset_day clears daily aggregates."""
        state = SymbolState(symbol="BHARTIARTL", exchange="NSE")
        timestamp = datetime(2026, 1, 14, 9, 15, 30)
        
        state.update_tick(price=800.0, volume=100, timestamp=timestamp)
        state.update_tick(price=810.0, volume=200, timestamp=timestamp)
        
        assert state.cumulative_volume == 300
        assert state.high_of_day == 810.0
        
        state.reset_day()
        
        assert state.cumulative_volume == 0
        assert state.high_of_day == 0.0
        assert state.low_of_day == float('inf')
        assert state.tick_count == 0
        assert state.candles_generated == 0
    
    def test_get_vwap_calculation(self):
        """Test VWAP calculation."""
        state = SymbolState(symbol="KOTAKBANK", exchange="NSE")
        timestamp = datetime(2026, 1, 14, 9, 15, 30)
        
        state.update_tick(price=1700.0, volume=100, timestamp=timestamp)
        state.update_tick(price=1710.0, volume=200, timestamp=timestamp)
        state.update_tick(price=1705.0, volume=150, timestamp=timestamp)
        
        # VWAP = (1700*100 + 1710*200 + 1705*150) / (100 + 200 + 150)
        # VWAP = (170000 + 342000 + 255750) / 450
        # VWAP = 767750 / 450 = 1706.111...
        
        vwap = state.get_vwap()
        assert abs(vwap - 1706.111) < 0.01
    
    def test_get_vwap_returns_zero_if_no_volume(self):
        """Test that get_vwap returns 0 if no volume."""
        state = SymbolState(symbol="RELIANCE", exchange="NSE")
        
        vwap = state.get_vwap()
        assert vwap == 0.0
    
    def test_get_stats(self):
        """Test get_stats returns correct statistics."""
        state = SymbolState(symbol="TCS", exchange="NSE")
        timestamp = datetime(2026, 1, 14, 9, 15, 30)
        
        state.update_tick(price=3500.0, volume=100, timestamp=timestamp)
        state.update_tick(price=3510.0, volume=200, timestamp=timestamp)
        
        stats = state.get_stats()
        
        assert stats["symbol"] == "TCS"
        assert stats["last_price"] == 3510.0
        assert stats["tick_count"] == 2
        assert stats["cumulative_volume"] == 300
        assert stats["high_of_day"] == 3510.0
        assert stats["low_of_day"] == 3500.0
