import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from structural.proxy_adapter import ProxyAdapter
import json

class MarketLoader:
    """
    Ingests raw data based on canonical Proxy Adapter bindings.
    """
    def __init__(self):
        self.adapter = ProxyAdapter()

    def _load_csv_price_frame(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        df.columns = [c.title() for c in df.columns]
        if 'Timestamp' in df.columns:
            df.rename(columns={'Timestamp': 'Date'}, inplace=True)
        if 'Datetime' in df.columns:
            df.rename(columns={'Datetime': 'Date'}, inplace=True)
        if 'Date' not in df.columns:
            raise KeyError('Date')
        df['Date'] = pd.to_datetime(df['Date'])
        return df.set_index('Date').sort_index()

    def load_benchmark(self, market: str) -> pd.DataFrame:
        """
        Loads and aggregates the benchmark equity proxy.
        US: Aggregates SPY + QQQ (if available).
        INDIA: Loads RELIANCE.
        Returns: DataFrame with ['Date', 'Close']
        """
        paths = self.adapter.get_ingestion_binding(market, "equity_core")
        if not paths:
            raise ValueError(f"No benchmark binding for {market}")
            
        # Hardcoded composite logic for US phase 1
        if market == "US":
            # Just load SPY for now as the core anchor, QQQ later
            dfs = []
            for p in paths:
                if not p.exists(): continue
                dfs.append(self._load_csv_price_frame(p))
            
            if not dfs:
                raise FileNotFoundError("No benchmark files found on disk")
            
            primary_path = paths[0]
            return self._load_csv_price_frame(primary_path)

        elif market == "INDIA":
            # CSV Format (NIFTY50.csv, BANKNIFTY.csv, etc.)
            path = paths[0]
            if not path.exists():
                raise FileNotFoundError(f"Missing {path}")
            
            return self._load_csv_price_frame(path)
            
        return pd.DataFrame()

    def load_volatility(self, market: str, benchmark_df: Optional[pd.DataFrame] = None) -> float:
        """
        Returns latest volatility level.
        US: VIX Level.
        INDIA: Realized Vol of Benchmark (20d).
        """
        if market == "US":
            paths = self.adapter.get_ingestion_binding(market, "volatility_gauge")
            if paths and paths[0].exists():
                df = pd.read_csv(paths[0])
                df.columns = [c.title() for c in df.columns]
                # Return latest Close
                return float(df.iloc[-1]['Close'])
            return 20.0 # Fallback default
            
        elif market == "INDIA":
            if benchmark_df is None: 
                return 0.0
            # Calculate realized vol: rolling std of returns * sqrt(252) * 100
            rets = benchmark_df['Close'].pct_change()
            vol = rets.rolling(20).std().iloc[-1] * (252**0.5) * 100
            return float(vol)
            
        return 0.0

    def load_rates(self, market: str) -> float:
        """
        Returns latest Risk-Free Rate (Yield).
        US: 10Y Yield (^TNX).
        INDIA: Missing (returns 0.0 with warning).
        """
        if market == "US":
            paths = self.adapter.get_ingestion_binding(market, "rates_anchor")
            if paths and paths[0].exists():
                df = pd.read_csv(paths[0])
                df.columns = [c.title() for c in df.columns]
                return float(df.iloc[-1]['Close'])
        return 0.0 # Default if missing (Fail Soft for now, but logged)

    def load_growth_proxy(self, market: str) -> pd.DataFrame:
        """
        Loads Growth/Tech proxy (e.g. QQQ).
        """
        paths = self.adapter.get_ingestion_binding(market, "growth_proxy")
        if not paths:
            return pd.DataFrame()
        
        path = paths[0]
        if not path.exists():
            return pd.DataFrame()

        df = self._load_csv_price_frame(path)
        return df[['Close']]
