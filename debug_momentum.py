
import logging
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core_modules.momentum_engine.momentum_engine import MomentumEngine
from ingestion.api_ingestion.angel_smartapi.config import AngelConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DebugMomentum")

def debug_signals():
    config = AngelConfig()
    watchlist = config.symbol_watchlist
    engine = MomentumEngine()
    
    print("\n" + "="*80)
    print(f"{'Symbol':<12} | {'Price':<10} | {'VWAP':<10} | {'HOD':<10} | {'Dist %':<8} | {'RelVol':<6} | {'Status'}")
    print("-" * 80)
    
    for symbol in watchlist:
        df = engine._load_data(symbol)
        if df.empty:
            print(f"{symbol:<12} | No data")
            continue
            
        df = engine._compute_indicators(df)
        if len(df) < engine.vol_ma_window:
            print(f"{symbol:<12} | Insufficient data ({len(df)})")
            continue
            
        latest = df.iloc[-1]
        
        above_vwap = latest['close'] > latest['vwap']
        hod_dist = (latest['hod'] - latest['close']) / latest['hod'] * 100
        near_hod = hod_dist <= engine.hod_proximity_pct
        vol_surge = latest['rel_vol'] >= engine.vol_multiplier
        
        status = []
        if above_vwap: status.append("VWAP+")
        else: status.append("VWAP-")
        
        if near_hod: status.append("HOD+")
        else: status.append(f"HOD-({hod_dist:.2f}%)")
        
        if vol_surge: status.append("VOL+")
        else: status.append(f"VOL-(x{latest['rel_vol']:.1f})")
        
        status_str = ", ".join(status)
        
        print(f"{symbol:<12} | {latest['close']:<10.2f} | {latest['vwap']:<10.2f} | {latest['hod']:<10.2f} | {hod_dist:<8.2f} | {latest['rel_vol']:<6.1f} | {status_str}")

    print("="*80 + "\n")

if __name__ == "__main__":
    debug_signals()
