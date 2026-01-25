
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.append(os.getcwd())

from traderfund.regime.types import MarketBehavior, RegimeState, DirectionalBias
from traderfund.regime.observability import RegimeFormatter

logger = logging.getLogger("USMarketAggregator")

class MarketAggregator:
    DATA_DIR = Path("data/us_market")
    WEIGHTS = {
        "SPY": 0.35,
        "QQQ": 0.25,
        "IWM": 0.25,
        "VIXY": 0.15
    }
    
    def load_snapshots(self) -> Dict[str, Dict]:
        snapshots = {}
        for sym in self.WEIGHTS.keys():
            path = self.DATA_DIR / f"{sym}_regime.json"
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        snapshots[sym] = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading {sym}: {e}")
        return snapshots

    def aggregate(self) -> Dict[str, Any]:
        snapshots = self.load_snapshots()
        if not snapshots:
            logger.warning("No snapshots to aggregate")
            return {}

        # 1. Global Event Lock Check
        is_locked = False
        lock_drivers = []
        for sym, data in snapshots.items():
            # Check event state string
            # Format: "EventState.NO_EVENT"
            evt_str = data.get("event_state", "NO_EVENT")
            if "LOCKED" in evt_str:
                is_locked = True
                lock_drivers.append(sym)

        # 2. Weighted Behavior Score
        # Map behavior to numeric
        # BULLISH_TREND = 1
        # BEARISH_TREND = -1
        # SIDEWAYS_STABLE = 0
        # Others? We'll rely on BIAS mostly.
        
        score_bias = 0.0
        score_vol = 0.0
        total_weight = 0.0
        
        drivers = []
        
        for sym, weight in self.WEIGHTS.items():
            if sym not in snapshots:
                continue
            
            data = snapshots[sym]
            total_weight += weight
            
            # Extract Bias
            bias_str = data.get("bias", "NEUTRAL")
            val = 0.0
            if "BULL" in bias_str: val = 1.0
            elif "BEAR" in bias_str: val = -1.0
            
            # VIXY INVERSION LOGIC
            if sym == "VIXY":
                val = -val # Bullish VIX = Bearish Market
                
            score_bias += val * weight
            
            # Extract Volatility
            # factors.volatility_ratio
            vol_ratio = 1.0
            if "factors" in data:
                 vol_ratio = data["factors"].get("volatility_ratio", 1.0)
            score_vol += vol_ratio * weight
            
            drivers.append(f"{sym}({bias_str})")

        if total_weight == 0:
            return {}

        # Normalize
        final_bias_score = score_bias / total_weight
        final_vol_score = score_vol / total_weight
        
        # Determine Market State
        # If Locked -> LOCKED behavior (we map to UNDEFINED or SPECIFIC?)
        # RegimeState has minimal creation ability without Calculator.
        # We will synthesize a dictionary result directly suited for consumption.
        
        market_behavior = "UNDEFINED"
        market_bias = "NEUTRAL"
        
        if is_locked:
            market_behavior = "EVENT_RISK_OFF" # Custom or reuse existing?
            # Or stick to standard
            market_behavior = MarketBehavior.UNDEFINED.value # Usually event lock -> undefined
        else:
            # Vol Check
            is_high_vol = final_vol_score > 1.2 # Aggressive threshold
            
            # Bias Check
            if final_bias_score > 0.2:
                market_bias = "BULLISH"
                market_behavior = MarketBehavior.TRENDING_NORMAL_VOL.value if not is_high_vol else MarketBehavior.TRENDING_HIGH_VOL.value
            elif final_bias_score < -0.2:
                market_bias = "BEARISH"
                market_behavior = MarketBehavior.TRENDING_NORMAL_VOL.value if not is_high_vol else MarketBehavior.TRENDING_HIGH_VOL.value
            else:
                market_bias = "NEUTRAL"
                market_behavior = MarketBehavior.MEAN_REVERTING_LOW_VOL.value if not is_high_vol else MarketBehavior.MEAN_REVERTING_HIGH_VOL.value

        # Timestamp Logic: Try root, then meta
        ref_snap = snapshots[list(snapshots.keys())[0]]
        ts = ref_snap.get("timestamp")
        if not ts and "meta" in ref_snap:
             ts = ref_snap["meta"].get("timestamp")

        result = {
            "timestamp": ts, # Use first timestamp
            "symbol": "US_MARKET_AGG",
            "regime": market_behavior,
            "bias": market_bias,
            "confidence": 1.0 if not is_locked else 0.0, # Placeholder
            "is_locked": is_locked,
            "drivers": drivers,
            "scores": {
                "bias_score": final_bias_score,
                "vol_score": final_vol_score
            }
        }
        
        # Save
        out_path = self.DATA_DIR / "us_market_regime.json"
        with open(out_path, 'w') as f:
            json.dump(result, f, indent=2)
            
        return result

if __name__ == "__main__":
    agg = MarketAggregator()
    print(agg.aggregate())
