"""Verification script for Momentum Engine logic."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core_modules.momentum_engine.momentum_engine import MomentumEngine

def create_synthetic_data():
    """Create synthetic intraday data that should trigger a signal."""
    now = datetime(2026, 1, 3, 10, 0, 0)
    data = []
    
    # Base data: 20 candles of stable price/volume
    for i in range(20):
        data.append({
            "symbol": "TEST",
            "exchange": "NSE",
            "timestamp": (now + timedelta(minutes=i)).isoformat() + "+05:30",
            "open": 100.0,
            "high": 100.5,
            "low": 99.5,
            "close": 100.0,
            "volume": 1000
        })
    
    # Breakdown of criteria:
    # 21st candle: VWAP should be around 100.
    # We want: Price > VWAP, Near HOD, Vol Surge.
    
    # HOD so far: 100.5
    
    data.append({
        "symbol": "TEST",
        "exchange": "NSE",
        "timestamp": (now + timedelta(minutes=20)).isoformat() + "+05:30",
        "open": 100.0,
        "high": 102.0,  # New HOD
        "low": 100.0,
        "close": 101.8, # Price > VWAP (approx 100), Near HOD (102.0), Vol Surge
        "volume": 3000  # 3x average (1000)
    })
    
    return pd.DataFrame(data)

def test_logic():
    engine = MomentumEngine(vol_ma_window=20, hod_proximity_pct=0.5, vol_multiplier=2.0)
    df = create_synthetic_data()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Mocking indicators computation
    df_with_inds = engine._compute_indicators(df)
    
    # Manual check of last row
    latest = df_with_inds.iloc[-1]
    print(f"Latest Candle Analysis:")
    print(f"  Close: {latest['close']}, VWAP: {latest['vwap']:.2f}, HOD: {latest['hod']}")
    print(f"  RelVol: {latest['rel_vol']:.1f}, VolMA: {latest['vol_ma']}")
    
    # Run signal generation logic manually or by mocking load_data
    # For simplicity, we'll just check if the engine's internal logic would have triggered it
    above_vwap = latest['close'] > latest['vwap']
    near_hod = (latest['hod'] - latest['close']) / latest['hod'] * 100 <= 0.5
    vol_surge = latest['rel_vol'] >= 2.0
    
    print(f"Criteria check: Above VWAP: {above_vwap}, Near HOD: {near_hod}, Vol Surge: {vol_surge}")
    
    if above_vwap and near_hod and vol_surge:
        print("SUCCESS: Signal would have been triggered.")
    else:
        print("FAILURE: Signal criteria not met.")

if __name__ == "__main__":
    test_logic()
