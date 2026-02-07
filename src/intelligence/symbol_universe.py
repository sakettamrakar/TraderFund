"""
Symbol Universe Builder.
Deterministic generation of the monitoring universe.

Supports:
- US (S&P 500 / Nasdaq 100 Proxies)
- India (Nifty 50 Proxies)
"""
import json
from pathlib import Path
from typing import List, Dict

class SymbolUniverseBuilder:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_path = output_dir / "symbol_universe.json"
        
        # Hardcoded definitions for phase 1. 
        # In a real system, these would fetch from an index provider or CSV.
        self.DEFINITIONS = {
            "US": [
                "SPY", "QQQ", "IWM",  # Indices
                "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "META", # Mag 7
                "JPM", "V", "XOM", "JNJ", "PG", # Defensive / Value
                "GLD", "SLV", "TLT", "HYG" # Macro Assets
            ],
            "INDIA": [
                "NIFTY_50", "BANKNIFTY",
                "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
                "ITC", "LT", "AXISBANK", "SBIN", "BHARTIARTL"
            ]
        }

    def build(self) -> Dict[str, List[str]]:
        """
        Builds and persists the universe definition.
        """
        universe = self.DEFINITIONS
        
        # Persist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(universe, f, indent=2)
            
        return universe

    def get_symbols(self, market: str) -> List[str]:
        return self.DEFINITIONS.get(market, [])
