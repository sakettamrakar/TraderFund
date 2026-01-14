import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import timedelta
from signals.repository.base import SignalRepository
from signals.core.models import Signal
from signals.core.enums import SignalDirection
from analytics.signal_reliability.models import ReliabilityMetric

logger = logging.getLogger("SignalEvaluator")

class SignalEvaluator:
    """
    Compares Signals against Historical Price Data.
    Calculates MFE, MAE, and Accuracy.
    """
    
    def __init__(self, signal_repo: SignalRepository, price_dir: Path):
        self.signal_repo = signal_repo
        self.price_dir = price_dir
        self.cache = {}

    def _get_price_data(self, asset: str) -> pd.DataFrame:
        if asset in self.cache:
            return self.cache[asset]
            
        path = self.price_dir / f"{asset}.parquet"
        if not path.exists():
            return pd.DataFrame()
            
        df = pd.read_parquet(path)
        # Ensure UTC datetime index
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        self.cache[asset] = df
        return df

    def evaluate_batch(self, signals: List[Signal], horizon_bars: int = 5) -> ReliabilityMetric:
        # Aggregators
        hits = 0
        total = 0
        mfes = []
        maes = []
        follow_throughs = 0
        
        for sig in signals:
            df = self._get_price_data(sig.asset_id)
            if df.empty:
                continue
            
            # Find trigger time index
            # Price data is typically Daily 00:00 UTC or Close time.
            # Signal trigger is precise timestamp.
            # We map signal trigger to the NEXT available bar if intraday, or SAME bar if daily closed.
            # Assuming daily data for now.
            
            trigger_date = sig.trigger_timestamp.date()
            if hasattr(trigger_date, 'to_period'): # Pandas compatibility logic if needed
                 pass 
                 
            # Slice future window
            future_prices = df[df.index >= pd.Timestamp(trigger_date)].head(horizon_bars + 1)
            
            if len(future_prices) < 2:
                continue
                
            entry_price = future_prices.iloc[0]['close']
            window = future_prices.iloc[1:] # Bars after entry
            
            if window.empty:
                continue

            total += 1
            
            # Calculation
            if sig.direction == SignalDirection.BULLISH:
                max_high = window['high'].max()
                min_low = window['low'].min()
                mfe = (max_high - entry_price) / entry_price
                mae = (entry_price - min_low) / entry_price
                final_change = (window.iloc[-1]['close'] - entry_price) / entry_price
                
            elif sig.direction == SignalDirection.BEARISH:
                max_high = window['high'].max()
                min_low = window['low'].min()
                mfe = (entry_price - min_low) / entry_price
                mae = (max_high - entry_price) / entry_price
                final_change = (entry_price - window.iloc[-1]['close']) / entry_price
            
            else: # Neutral
                continue

            mfes.append(max(0, mfe))
            maes.append(max(0, mae))
            
            if final_change > 0:
                hits += 1
                
            if mfe > 0.01: # 1% favorable move at any point
                follow_throughs += 1
                
        # Compute Stats
        if total == 0:
            return ReliabilityMetric(0, 0.0, 0.0, 0.0, 0.0, "N/A")
            
        return ReliabilityMetric(
            sample_size=total,
            directional_accuracy=hits / total,
            mean_favorable_excursion=np.mean(mfes),
            mean_adverse_excursion=np.mean(maes),
            follow_through_rate=follow_throughs / total,
            confidence_bucket="AGGREGATE"
        )
