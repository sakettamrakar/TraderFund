
import numpy as np
import pandas as pd
from typing import Any

from traderfund.regime.providers.base import ILiquidityProvider

class RVOLLiquidityProvider(ILiquidityProvider):
    """
    Computes Relative Volume (RVOL).
    Formula: Current Volume / SMA(Volume, 20)
    Normalized Output: 0.0 (Dry) to 1.0 (Liquid) based on a simple heuristic scale or just clamped Ratio.
    Implementation Decision: Return pure ratio clamped to 0.0-1.0 is incorrect for RVOL as >1 is good.
    Re-reading Spec: "Output: Normalized Score (0.0 = Dry/Risk, 1.0 = Liquid)."
    Logic: 
    - RVOL < 1.0 implies below average.
    - RVOL < 0.2 is severe risk.
    - To map to 0..1 where 1 is "Good":
        - We want to penalize low volume. High volume is fine.
        - Function: min(1.0, RVOL / 1.0) -> If RVOL >= 1.0, score is 1.0. If RVOL is 0.5, score is 0.5.
    """
    def __init__(self, window: int = 20):
        self.window = window

    def get_liquidity_score(self, data: pd.DataFrame) -> float:
        """
        Returns normalized liquidity score.
        Score = min(1.0, Current_Vol / Average_Vol)
        """
        self._validate_input(data)
        
        if len(data) < self.window:
            return 1.0 # Assume normal if insufficient history
            
        volume = data['volume']
        current_vol = volume.iloc[-1]
        
        # Calculate SMA of Volume
        avg_vol = volume.rolling(window=self.window).mean().iloc[-1]
        
        if avg_vol == 0:
            return 0.0 # No volume history means illiquid
            
        rvol = current_vol / avg_vol
        
        # Normalize: Cap at 1.0 (Liquidity can't be "better than liquid" for our risk model)
        return float(min(1.0, max(0.0, rvol)))

    def _validate_input(self, data: pd.DataFrame):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a pandas DataFrame")
        if 'volume' not in data.columns:
            raise ValueError("Input data missing column: volume")
        if data.empty:
            raise ValueError("Input data is empty")
