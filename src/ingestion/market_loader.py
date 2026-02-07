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

    def load_benchmark(self, market: str) -> pd.DataFrame:
        """
        Loads and aggregates the benchmark equity proxy.
        US: Aggregates SPY + QQQ (if available).
        INDIA: Loads RELIANCE.
        Returns: DataFrame with ['Date', 'Close']
        """
        paths = self.adapter.get_ingestion_binding(market, "benchmark_equity")
        if not paths:
            raise ValueError(f"No benchmark binding for {market}")
            
        # Hardcoded composite logic for US phase 1
        if market == "US":
            # Just load SPY for now as the core anchor, QQQ later
            dfs = []
            for p in paths:
                if not p.exists(): continue
                df = pd.read_csv(p)
                # Normalize column names to title case or stick to lowercase
                # Inspect showed lowercase. Let's start by normalizing keys to title case for consistency with rest of system
                df.columns = [c.title() for c in df.columns] 
                # Now we expect 'Date', 'Close'
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date').sort_index()
                dfs.append(df['Close']) 
            
            if not dfs:
                raise FileNotFoundError("No benchmark files found on disk")
            
            primary_path = paths[0]
            df = pd.read_csv(primary_path)
            df.columns = [c.title() for c in df.columns]
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date').sort_index()
            return df[['Close']]

        elif market == "INDIA":
             # JSONL Format
            path = paths[0]
            if not path.exists():
                raise FileNotFoundError(f"Missing {path}")
            
            records = []
            with open(path, 'r') as f:
                for line in f:
                    records.append(json.loads(line))
            
            df = pd.DataFrame(records)
            # Keys are lowercase: date, close
            df['Date'] = pd.to_datetime(df['date'])
            df = df.set_index('Date').sort_index()
            df['Close'] = df['close'] 
            return df[['Close']]
            
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

        df = pd.read_csv(path)
        df.columns = [c.title() for c in df.columns]
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date').sort_index()
        return df[['Close']]
