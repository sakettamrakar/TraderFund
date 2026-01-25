
import numpy as np
import pandas as pd
from typing import Any, Tuple, Optional
from datetime import datetime

from traderfund.regime.types import DirectionalBias
from traderfund.regime.providers.base import ITrendStrengthProvider, ITrendAlignmentProvider

class ADXTrendStrengthProvider(ITrendStrengthProvider, ITrendAlignmentProvider):
    """
    Computes Trend Strength using Wilder's ADX and Alignment using EMAs.
    Stateless implementation using numpy/pandas.
    """
    def __init__(self, 
                 adx_period: int = 14, 
                 ema_fast: int = 20, 
                 ema_slow: int = 50,
                 ema_trend: int = 200):
        self.adx_period = adx_period
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.ema_trend = ema_trend

    def get_trend_strength(self, data: pd.DataFrame) -> float:
        """
        Computes normalized ADX strength (0.0 to 1.0).
        Expects DataFrame with specific columns.
        Normalization: ADX / 100.
        """
        self._validate_input(data, required_columns=['high', 'low', 'close'])
        
        if len(data) < self.adx_period * 2:
            return 0.0 # Insufficient data
            
        adx = self._calculate_adx(data['high'], data['low'], data['close'], self.adx_period)
        if np.isnan(adx):
            return 0.0
            
        return max(0.0, min(1.0, adx / 100.0))

    def get_alignment(self, data: pd.DataFrame) -> DirectionalBias:
        """
        Determines directional bias using EMA alignment.
        """
        self._validate_input(data, required_columns=['close'])
        
        if len(data) < self.ema_trend:
            return DirectionalBias.NEUTRAL
            
        close = data['close']
        ema_f = close.ewm(span=self.ema_fast, adjust=False).mean().iloc[-1]
        ema_s = close.ewm(span=self.ema_slow, adjust=False).mean().iloc[-1]
        price = close.iloc[-1]
        
        if price > ema_f > ema_s:
            return DirectionalBias.BULLISH
        elif price < ema_f < ema_s:
            return DirectionalBias.BEARISH
        else:
            return DirectionalBias.NEUTRAL

    def _validate_input(self, data: pd.DataFrame, required_columns: list):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
        missing = [col for col in required_columns if col not in data.columns]
        if missing:
            raise ValueError(f"Input data missing columns: {missing}")
        if data.empty:
            raise ValueError("Input data is empty")

    def _calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> float:
        """
        Standard Wilder's ADX calculation.
        """
        # Calculate TR
        # TR = max(high-low, abs(high-prev_close), abs(low-prev_close))
        # Using vectorization
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate DM
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        
        # +DM: up_move > down_move and up_move > 0
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        # -DM: down_move > up_move and down_move > 0
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        
        # Smooth TR and DM (Wilder's Smoothing usually, but using EMA is acceptable proxy for simplicity in 'stateless' if exact match not required, 
        # but standard ADX uses Wilder's which is effectively EMA with alpha=1/n)
        # Wilder's Smoothing: Current = Prev + (Current - Prev)/n -> EMA(alpha=1/n)
        alpha = 1.0 / period
        
        tr_s = pd.Series(tr).ewm(alpha=alpha, adjust=False).mean()
        plus_dm_s = pd.Series(plus_dm).ewm(alpha=alpha, adjust=False).mean()
        minus_dm_s = pd.Series(minus_dm).ewm(alpha=alpha, adjust=False).mean()
        
        # Avoid division by zero
        tr_s = tr_s.replace(0, 1e-9)
        
        plus_di = 100 * (plus_dm_s / tr_s)
        minus_di = 100 * (minus_dm_s / tr_s)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
        
        # ADX is smoothed DX
        adx = dx.ewm(alpha=alpha, adjust=False).mean()
        
        return adx.iloc[-1]
