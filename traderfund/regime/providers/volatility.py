
import numpy as np
import pandas as pd
from typing import Any

from traderfund.regime.providers.base import IVolatilityRatioProvider

class ATRVolatilityProvider(IVolatilityRatioProvider):
    """
    Computes Volatility Ratio using ATR vs Moving Average of ATR.
    Formula: Current ATR(14) / SMA(ATR(14), 20)
    """
    def __init__(self, atr_period: int = 14, baseline_period: int = 20):
        self.atr_period = atr_period
        self.baseline_period = baseline_period

    def get_volatility_ratio(self, data: pd.DataFrame) -> float:
        """
        Returns ratio of Current ATR to Historical Baseline ATR.
        Ratio > 1.0 implies volatility expansion.
        """
        self._validate_input(data)
        
        required_len = self.atr_period + self.baseline_period
        if len(data) < required_len:
            return 1.0 # Insufficient data, assume baseline
            
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Calculate ATR Series
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Smooth TR (Wilder's Smoothing / EMA)
        alpha = 1.0 / self.atr_period
        atr_series = tr.ewm(alpha=alpha, adjust=False).mean()
        
        current_atr = atr_series.iloc[-1]
        
        # Calculate Baseline (SMA of ATR)
        baseline_atr = atr_series.rolling(window=self.baseline_period).mean().iloc[-1]
        
        if baseline_atr == 0:
            return 1.0
            
        return current_atr / baseline_atr

    def _validate_input(self, data: pd.DataFrame):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
        missing = [col for col in ['high', 'low', 'close'] if col not in data.columns]
        if missing:
            raise ValueError(f"Input data missing columns: {missing}")
        if data.empty:
            raise ValueError("Input data is empty")
