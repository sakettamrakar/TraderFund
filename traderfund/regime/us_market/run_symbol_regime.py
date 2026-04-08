
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
from src.structural.proxy_adapter import ProxyAdapter # ADDED

logger = logging.getLogger("USSymbolRegime")

class SymbolRegimeRunner:
    # Deprecated: Path is now managed by ProxyAdapter
    # DATA_DIR = Path("data/us_market")
    
    def __init__(self):
        self.calc = RegimeCalculator()
        self.trend = ADXTrendStrengthProvider()
        self.vol = ATRVolatilityProvider()
        self.liq = RVOLLiquidityProvider()
        self.event = CalendarEventProvider()
        
    def run_for_symbol(self, symbol: str) -> Dict[str, Any]:
        adapter = ProxyAdapter()
        try:
            # We assume US market for this runner
            m_cfg = adapter._config.get("US", {})
            bindings = m_cfg.get("ingestion_binding", {})
            file_path = adapter.root / bindings.get(symbol, "")
        except:
            logger.warning(f"No binding for {symbol} in ProxyAdapter")
            return {}

        if not file_path or not file_path.exists():
            logger.warning(f"No data for {symbol} at {file_path}")
            return {}
            
        try:
            if file_path.suffix == ".parquet":
                df = pd.read_parquet(file_path)
                if df.index.name == 'timestamp':
                    df.index.name = 'Date'
                df.reset_index(inplace=True)
                # Map 'Date' or 'timestamp' to 'timestamp' for the rest of the logic
                df.rename(columns={'Date': 'timestamp', 'date': 'timestamp'}, inplace=True)
            else:
                df = pd.read_csv(file_path)
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Standardize columns for providers (Low, High, Close, Volume)
            df.columns = [c.lower() for c in df.columns]
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
            # Save to analytics side? For now keep in us_market legacy for dashboard compat
            out_path = Path("data/us_market") / f"{symbol}_regime.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            return snapshot
        return {}

def run_all(symbols=["SPY", "QQQ", "IWM"]):
    runner = SymbolRegimeRunner()
    for sym in symbols:
        runner.run_for_symbol(sym)
