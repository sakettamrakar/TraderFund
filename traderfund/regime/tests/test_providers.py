
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from traderfund.regime.types import DirectionalBias
from traderfund.regime.providers.trend import ADXTrendStrengthProvider
from traderfund.regime.providers.volatility import ATRVolatilityProvider
from traderfund.regime.providers.liquidity import RVOLLiquidityProvider
from traderfund.regime.providers.event import CalendarEventProvider

@pytest.fixture
def mock_ohlc_data():
    """Generates 100 bars of trending then ranging data."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="5min")
    
    # 0-50: Strong Up Trend
    price = np.linspace(100, 150, 50)
    # 50-100: Choppy Range
    price2 = np.linspace(150, 150, 50) + np.random.normal(0, 2, 50)
    
    close = np.concatenate([price, price2])
    high = close + 2
    low = close - 2
    open_ = close - 0.5
    volume = np.full(100, 1000)
    volume[99] = 5000 # Spike at end
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    return df

class TestTrendProvider:
    def test_adx_strength_calculation(self, mock_ohlc_data):
        provider = ADXTrendStrengthProvider(adx_period=14)
        
        # Test full data
        strength = provider.get_trend_strength(mock_ohlc_data)
        assert 0.0 <= strength <= 1.0
        
        # Test insufficient data
        short_data = mock_ohlc_data.head(10)
        assert provider.get_trend_strength(short_data) == 0.0

    def test_alignment_bullish(self):
        # Create perfect bullish stack: Price > EMA20 > EMA50
        dates = pd.date_range(start="2024-01-01", periods=250, freq="5min")
        close = np.linspace(100, 200, 250) # Linear up trend
        df = pd.DataFrame({'close': close}, index=dates)
        
        provider = ADXTrendStrengthProvider(ema_fast=20, ema_slow=50, ema_trend=200)
        bias = provider.get_alignment(df)
        assert bias == DirectionalBias.BULLISH

class TestVolatilityProvider:
    def test_atr_ratio_expansion(self, mock_ohlc_data):
        provider = ATRVolatilityProvider(atr_period=14, baseline_period=20)
        
        # Modify last bars to have huge range
        mock_ohlc_data.iloc[-1, mock_ohlc_data.columns.get_loc('high')] += 20
        mock_ohlc_data.iloc[-1, mock_ohlc_data.columns.get_loc('low')] -= 20
        
        ratio = provider.get_volatility_ratio(mock_ohlc_data)
        assert ratio > 1.5 # Expect expansion

    def test_insufficient_data_defaults(self, mock_ohlc_data):
        provider = ATRVolatilityProvider(atr_period=14, baseline_period=20)
        short_data = mock_ohlc_data.head(10)
        assert provider.get_volatility_ratio(short_data) == 1.0

class TestLiquidityProvider:
    def test_rvol_calculation(self, mock_ohlc_data):
        provider = RVOLLiquidityProvider(window=20)
        
        # Last bar volume is 5000, avg is likely ~1000
        score = provider.get_liquidity_score(mock_ohlc_data)
        assert score == 1.0 # Cap at 1.0
        
        # Test Dry
        mock_ohlc_data.iloc[-1, mock_ohlc_data.columns.get_loc('volume')] = 100
        score_dry = provider.get_liquidity_score(mock_ohlc_data)
        assert score_dry < 0.2 # Should be approx 0.1

    def test_validate_volume_col(self):
        provider = RVOLLiquidityProvider()
        df = pd.DataFrame({'close': [100]})
        with pytest.raises(ValueError, match="missing column: volume"):
            provider.get_liquidity_score(df)

class TestEventProvider:
    def test_event_lock_window(self):
        provider = CalendarEventProvider(lock_window_minutes=15)
        
        now = datetime.now()
        data = pd.DataFrame({'timestamp': [now]})
        
        # Inject Event via attrs
        data.attrs['events'] = [{
            'time': now + timedelta(minutes=10), # In lock window
            'impact': 1.0
        }]
        
        res = provider.get_pressure(data)
        assert res['is_lock_window'] is True
        assert res['pressure'] == 1.0

    def test_event_decay(self):
        provider = CalendarEventProvider(lock_window_minutes=15, max_lookahead_minutes=75)
        
        now = datetime.now()
        data = pd.DataFrame({'timestamp': [now]})
        
        # Event 45m away (30m past lock)
        # Range is 60m (75-15). Dist is 30m. Pressure should be 0.5.
        data.attrs['events'] = [{
            'time': now + timedelta(minutes=45),
            'impact': 1.0
        }]
        
        res = provider.get_pressure(data)
        assert res['is_lock_window'] is False
        assert 0.4 < res['pressure'] < 0.6
