
import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from traderfund.regime.calculator import RegimeCalculator
from traderfund.regime.core import StateManager
from traderfund.regime.providers.trend import ADXTrendStrengthProvider
from traderfund.regime.providers.volatility import ATRVolatilityProvider
from traderfund.regime.providers.liquidity import RVOLLiquidityProvider
from traderfund.regime.providers.event import CalendarEventProvider
from traderfund.regime.types import RegimeFactors, RegimeState
from traderfund.regime.observability import RegimeFormatter

logger = logging.getLogger("USSymbolRegime")

class SymbolRegimeRunner:
    DATA_DIR = Path("data/us_market")
    
    def __init__(self):
        self.calc = RegimeCalculator()
        self.trend = ADXTrendStrengthProvider()
        self.vol = ATRVolatilityProvider()
        self.liq = RVOLLiquidityProvider()
        self.event = CalendarEventProvider()
        
    def run_for_symbol(self, symbol: str) -> Dict[str, Any]:
        file_path = self.DATA_DIR / f"{symbol}_daily.csv"
        if not file_path.exists():
            logger.warning(f"No data for {symbol}")
            return {}
            
        try:
            df = pd.read_csv(file_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        except Exception as e:
            logger.error(f"Read error {symbol}: {e}")
            return {}

        if len(df) < 50:
            logger.warning(f"Insufficient history for {symbol} ({len(df)})")
            return {}

        # Replay History for State Stateability
        # We need to simulate the state evolution to get correct 'persistence' and 'confidence'.
        # We'll run the last N bars (e.g. 100) or full history if short.
        # Running full history is safer for "StableRegime" but slower.
        # Given daily data, full history is fast.
        
        manager = StateManager()
        last_state = None
        last_factors = None
        
        # Optimization: Calculate indicators vectorized first
        # But our providers take 'df' window. 
        # Iterating daily bars is fast enough.
        
        # Start from index 50 (warmup)
        for i in range(50, len(df)):
            window = df.iloc[:i+1]
            
            # Providers
            t_str = self.trend.get_trend_strength(window)
            t_aln = self.trend.get_alignment(window)
            v_rat = self.vol.get_volatility_ratio(window)
            l_scr = self.liq.get_liquidity_score(window)
            e_dat = self.event.get_pressure(window)
            
            # Calculator
            raw = self.calc.calculate(t_str, t_aln, v_rat, l_scr, e_dat['pressure'], e_dat['is_lock_window'])
            
            factors = RegimeFactors(
                trend_strength_norm=t_str, 
                volatility_ratio=v_rat, 
                liquidity_status="NORMAL" if l_scr > 0.5 else "DRY", 
                event_pressure_norm=e_dat['pressure']
            )
            
            last_state = manager.update(raw, factors)
            last_factors = factors

        if last_state:
            # Save Snapshot
            snapshot = RegimeFormatter.to_dict(last_state, last_factors, symbol)
            out_path = self.DATA_DIR / f"{symbol}_regime.json"
            with open(out_path, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            return snapshot
        return {}

def run_all(symbols=["SPY", "QQQ", "IWM"]):
    runner = SymbolRegimeRunner()
    for sym in symbols:
        runner.run_for_symbol(sym)
