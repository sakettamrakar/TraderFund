"""Momentum Engine v0.

Generates trade-ready signals from processed intraday data based on:
1. Price > VWAP
2. Near High-of-Day
3. Relative Volume Expansion
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict
from .signal_models import MomentumSignal

logger = logging.getLogger(__name__)

class MomentumEngine:
    """Minimal Momentum Engine (v0)."""

    def __init__(
        self,
        processed_data_path: str = "data/processed/candles/intraday",
        vol_ma_window: int = 20,
        hod_proximity_pct: float = 0.5,  # 0.5% from HOD
        vol_multiplier: float = 2.0      # 2x relative volume
    ):
        """Initialize the engine.

        Args:
            processed_data_path: Path to Parquet files.
            vol_ma_window: Window for average volume calculation.
            hod_proximity_pct: Tolerance for HOD proximity.
            vol_multiplier: Threshold for volume expansion.
        """
        self.data_path = Path(processed_data_path)
        self.vol_ma_window = vol_ma_window
        self.hod_proximity_pct = hod_proximity_pct
        self.vol_multiplier = vol_multiplier

    def _load_data(self, symbol: str, exchange: str = "NSE") -> pd.DataFrame:
        """Load processed Parquet data for a symbol."""
        file_path = self.data_path / f"{exchange}_{symbol}_1m.parquet"
        if not file_path.exists():
            logger.warning(f"No processed data found for {exchange}:{symbol}")
            return pd.DataFrame()
        
        df = pd.read_parquet(file_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def _compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute internal indicators: VWAP, HOD, RelVol."""
        if df.empty:
            return df
            
        df = df.copy()
        
        # 1. VWAP (Intraday reset)
        # Assuming data is for a single day as per Phase 2 naming but we'll group by date just in case
        df['date'] = df['timestamp'].dt.date
        
        # 1. VWAP (Intraday reset)
        df['tp'] = (df['high'] + df['low'] + df['close']) / 3
        df['tpv'] = df['tp'] * df['volume']
        
        df['cum_tpv'] = df.groupby('date')['tpv'].cumsum()
        df['cum_vol'] = df.groupby('date')['volume'].cumsum()
        df['vwap'] = df['cum_tpv'] / df['cum_vol']
        
        # Cleanup temporary columns
        df.drop(columns=['tp', 'tpv', 'cum_tpv', 'cum_vol'], inplace=True)
        
        # 2. High of Day (HOD)
        df['hod'] = df.groupby('date')['high'].cummax()
        
        # 3. Relative Volume
        df['vol_ma'] = df['volume'].rolling(window=self.vol_ma_window).mean()
        df['rel_vol'] = df['volume'] / df['vol_ma']
        
        return df

    def generate_signals(self, symbol: str, exchange: str = "NSE") -> List[MomentumSignal]:
        """Analyze data and generate signals."""
        df = self._load_data(symbol, exchange)
        if df.empty:
            return []
            
        df = self._compute_indicators(df)
        if len(df) < self.vol_ma_window:
            return []

        signals = []
        
        # Analyze the latest candle
        latest = df.iloc[-1]
        
        # Criteria:
        # 1. Price > VWAP
        # 2. Near HOD
        # 3. Volume Expansion
        
        above_vwap = latest['close'] > latest['vwap']
        
        hod_dist = (latest['hod'] - latest['close']) / latest['hod'] * 100
        near_hod = hod_dist <= self.hod_proximity_pct
        
        vol_surge = latest['rel_vol'] >= self.vol_multiplier
        
        if above_vwap and near_hod and vol_surge:
            reason = (
                f"Price ({latest['close']:.2f}) > VWAP ({latest['vwap']:.2f}); "
                f"Near HOD ({latest['hod']:.2f}, dist {hod_dist:.2f}%); "
                f"Vol surge (x{latest['rel_vol']:.1f})"
            )
            
            # Confidence calculation (simple heuristic for v0)
            confidence = min(1.0, (latest['rel_vol'] / (self.vol_multiplier * 2)) + 0.5)
            
            signal = MomentumSignal(
                symbol=symbol,
                timestamp=latest['timestamp'].isoformat(),
                confidence=round(confidence, 2),
                entry_hint=f"Above {latest['high']:.2f}",
                stop_hint=f"Below {latest['vwap']:.2f}",
                reason=reason,
                price_t0=float(latest['close']),
                volume_t0=float(latest['volume'])
            )
            signals.append(signal)
            
        return signals

    def generate_signals_from_df(self, df: pd.DataFrame, symbol: str, exchange: str = "NSE") -> List[MomentumSignal]:
        """Analyze data from a provided DataFrame and generate signals.
        
        This method allows external callers (like replay controller) to 
        provide pre-filtered data, enabling lookahead-free historical replay.
        
        Args:
            df: DataFrame containing candle data (must have OHLCV columns).
            symbol: Trading symbol for signal labeling.
            exchange: Exchange for signal labeling.
            
        Returns:
            List of MomentumSignal objects.
        """
        if df.empty:
            return []
            
        df = self._compute_indicators(df)
        if len(df) < self.vol_ma_window:
            return []

        signals = []
        
        # Analyze the latest candle
        latest = df.iloc[-1]
        
        # Criteria:
        # 1. Price > VWAP
        # 2. Near HOD
        # 3. Volume Expansion
        
        above_vwap = latest['close'] > latest['vwap']
        
        hod_dist = (latest['hod'] - latest['close']) / latest['hod'] * 100
        near_hod = hod_dist <= self.hod_proximity_pct
        
        vol_surge = latest['rel_vol'] >= self.vol_multiplier
        
        if above_vwap and near_hod and vol_surge:
            reason = (
                f"Price ({latest['close']:.2f}) > VWAP ({latest['vwap']:.2f}); "
                f"Near HOD ({latest['hod']:.2f}, dist {hod_dist:.2f}%); "
                f"Vol surge (x{latest['rel_vol']:.1f})"
            )
            
            # Confidence calculation (simple heuristic for v0)
            confidence = min(1.0, (latest['rel_vol'] / (self.vol_multiplier * 2)) + 0.5)
            
            signal = MomentumSignal(
                symbol=symbol,
                timestamp=latest['timestamp'].isoformat(),
                confidence=round(confidence, 2),
                entry_hint=f"Above {latest['high']:.2f}",
                stop_hint=f"Below {latest['vwap']:.2f}",
                reason=reason,
                price_t0=float(latest['close']),
                volume_t0=float(latest['volume'])
            )
            signals.append(signal)
            
        return signals

    def run_on_all(self, watchlist: List[str]) -> List[MomentumSignal]:
        """Run engine on all watchlist symbols."""
        all_signals = []
        for symbol in watchlist:
            symbol_signals = self.generate_signals(symbol)
            all_signals.extend(symbol_signals)
        return all_signals

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    engine = MomentumEngine()
    symbols = ["RELIANCE", "TCS", "INFY", "ITC"]
    
    signals = engine.run_on_all(symbols)
    print(f"\n--- Momentum Signals (v0) ---\n")
    if not signals:
        print("No signals generated.")
    for sig in signals:
        import json
        print(json.dumps(sig.to_dict(), indent=2))
