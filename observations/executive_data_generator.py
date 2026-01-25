
import json
import logging
import pandas as pd
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core_modules.momentum_engine.momentum_engine import MomentumEngine
from ingestion.api_ingestion.angel_smartapi.config import AngelConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExecutiveData")

def generate_dashboard_data():
    config = AngelConfig()
    watchlist = config.symbol_watchlist
    engine = MomentumEngine()
    
    # Relaxed parameters for "Executive Observation"
    RELAXED_HOD_DIST = 1.0  # 1% instead of 0.5%
    RELAXED_VOL_MULT = 1.2  # 1.2x instead of 2.0x
    
    data = {
        "last_updated": datetime.now().isoformat(),
        "symbols": []
    }
    
    today = datetime.now().date()
    
    for symbol in watchlist:
        try:
            df = engine._load_data(symbol)
            if df.empty:
                continue
                
            df = engine._compute_indicators(df)
            if len(df) < engine.vol_ma_window:
                continue
            
            # Filter for today's data
            df_today = df[df['timestamp'].dt.date == today].copy()
            if df_today.empty:
                continue
                
            latest = df_today.iloc[-1]
            
            # Check for ANY signal today
            # We use the generate_signals_from_df logic implicitly
            df_today['above_vwap'] = df_today['close'] > df_today['vwap']
            df_today['near_hod'] = (df_today['hod'] - df_today['close']) / df_today['hod'] * 100 <= engine.hod_proximity_pct
            df_today['vol_surge'] = df_today['rel_vol'] >= engine.vol_multiplier
            
            df_today['is_signal'] = df_today['above_vwap'] & df_today['near_hod'] & df_today['vol_surge']
            signals_today = df_today[df_today['is_signal']]
            
            # Latest candle metrics
            hod_dist = (latest['hod'] - latest['close']) / latest['hod'] * 100
            score = 0
            if latest['close'] > latest['vwap']: score += 33
            score += max(0, (RELAXED_HOD_DIST - hod_dist) / RELAXED_HOD_DIST) * 33
            score += min(34, (latest['rel_vol'] - 1.0) / (RELAXED_VOL_MULT - 1.0) * 34) if latest['rel_vol'] >= 1.0 else 0
            
            item = {
                "symbol": symbol,
                "price": float(latest['close']),
                "vwap": float(latest['vwap']),
                "hod": float(latest['hod']),
                "hod_dist": float(hod_dist),
                "rel_vol": float(latest['rel_vol']),
                "score": round(score, 1),
                "signals_count": len(signals_today),
                "last_signal_time": signals_today.iloc[-1]['timestamp'].strftime("%H:%M") if not signals_today.empty else None,
                "status": "SIGNAL" if (latest['close'] > latest['vwap'] and hod_dist <= engine.hod_proximity_pct and latest['rel_vol'] >= engine.vol_multiplier) else ("CANDIDATE" if (latest['close'] > latest['vwap'] and hod_dist <= RELAXED_HOD_DIST and latest['rel_vol'] >= RELAXED_VOL_MULT) else "MONITORING")
            }
            data["symbols"].append(item)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            
    # Sort by score descending
    data["symbols"] = sorted(data["symbols"], key=lambda x: x["score"], reverse=True)
    
    output_path = Path("dashboard/data.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Dashboard data generated at {output_path}")

if __name__ == "__main__":
    generate_dashboard_data()
