
import os
import sys
import logging
import time
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Setup Path
sys.path.append(os.getcwd())

# Configuration
SYMBOL = "SPY"
INTERVAL = "60min" # 5min is Premium? Try 60min.
REFRESH_SECONDS = 300 # 5 min refresh

# Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("USRegime")

try:
    from ingestion.api_ingestion.alpha_vantage.client import AlphaVantageClient
    from traderfund.regime.calculator import RegimeCalculator
    from traderfund.regime.core import StateManager
    from traderfund.regime.providers.trend import ADXTrendStrengthProvider
    from traderfund.regime.providers.volatility import ATRVolatilityProvider
    from traderfund.regime.providers.liquidity import RVOLLiquidityProvider
    from traderfund.regime.providers.event import CalendarEventProvider
    from traderfund.regime.types import RegimeFactors, MarketBehavior
except ImportError as e:
    logger.error(f"Import Error: {e}. Run from repo root.")
    sys.exit(1)

def normalize_daily_data(json_data: Dict) -> pd.DataFrame:
    """
    Converts AlphaVantage Daily JSON to DataFrame.
    """
    key = "Time Series (Daily)"
    if key not in json_data:
        logger.error(f"Missing time series key '{key}'. Keys: {list(json_data.keys())}")
        if "Information" in json_data:
             logger.error(f"API Info: {json_data['Information']}")
        return pd.DataFrame()

    records = []
    ts_data = json_data[key]
    
    for ts_str, metrics in ts_data.items():
        records.append({
            "timestamp": pd.to_datetime(ts_str),
            "open": float(metrics["1. open"]),
            "high": float(metrics["2. high"]),
            "low": float(metrics["3. low"]),
            "close": float(metrics["4. close"]),
            "volume": int(metrics["5. volume"])
        })
    
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df

class USRegimeRunner:
    def __init__(self):
        self.client = AlphaVantageClient()
        
        # Initialize Regime Components
        self.calc = RegimeCalculator()
        self.manager = StateManager()
        self.trend = ADXTrendStrengthProvider()
        self.vol = ATRVolatilityProvider()
        self.liq = RVOLLiquidityProvider()
        self.event = CalendarEventProvider()
                                             
    def run_cycle(self):
        logger.info(f"Fetching {SYMBOL} (DAILY)...")
        try:
            # Use DAILY instead of INTRADAY
            data = self.client.get_daily(SYMBOL, outputsize='compact')
            
            # Fail Safe Checks
            if "Note" in data:
                logger.warning(f"API Note: {data['Note']}")
                # Rate limit?
                if "Thank you" in data['Note']: # Standard Rate Limit msg
                     return 

            if "Error Message" in data:
                logger.error(f"API Error: {data['Error Message']}")
                return

            df = normalize_daily_data(data)
            if df.empty or len(df) < 50:
                 logger.warning("[US REGIME] DATA_UNAVAILABLE — FAIL SAFE (Insufficient History)")
                 return

            # WARM UP / CALCULATE
            # Since we get compact (100 bars), we can just run on the last few to update state?
            # Or run fully? 
            # To ensure Hysteresis works, we should ideally feed the last N bars if starting fresh.
            # But StateManager holds unique state. 
            # Simple approach: Just calculate on the LATEST bar using the full DF window for indicators.
            
            # Providers (Last Bar)
            t_str = self.trend.get_trend_strength(df)
            t_aln = self.trend.get_alignment(df)
            v_rat = self.vol.get_volatility_ratio(df)
            l_scr = self.liq.get_liquidity_score(df)
            e_dat = self.event.get_pressure(df)
            
            # Sanity Check
            if any(pd.isna([t_str, v_rat, l_scr])):
                logger.warning("[US REGIME] INVALID_INDICATORS — FAIL SAFE")
                return

            # Calculator
            raw = self.calc.calculate(t_str, t_aln, v_rat, l_scr, e_dat['pressure'], e_dat['is_lock_window'])
            
            factors = RegimeFactors(
                 trend_strength_norm=t_str, 
                 volatility_ratio=v_rat, 
                 liquidity_status="NORMAL" if l_scr > 0.5 else "DRY", 
                 event_pressure_norm=e_dat['pressure']
            )
            
            # Update State
            state = self.manager.update(raw, factors)
            
            # OUTPUT
            summary = (f"[US REGIME] {SYMBOL} | {state.behavior.value:<20} | "
                       f"Bias={state.bias.value:<8} | Conf={state.total_confidence:.2f} | "
                       f"VolRatio={v_rat:.2f}")
            logger.info(summary)
            
            # Structured Log (Console for now)
            # logger.info(json.dumps(RegimeFormatter.to_dict(state, factors, SYMBOL)))

        except Exception as e:
            logger.exception(f"[US REGIME] CRASH: {e}")

def main():
    runner = USRegimeRunner()
    logger.info("Starting US Live Regime Runner (Shadow Mode)...")
    logger.info("Ctrl+C to stop.")
    
    while True:
        runner.run_cycle()
        time.sleep(REFRESH_SECONDS)

if __name__ == "__main__":
    main()
