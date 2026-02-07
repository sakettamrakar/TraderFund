import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class ProxyAdapter:
    """
    Structural adapter to read and enforce Market Proxy Sets.
    Reads from src/structural/market_proxy_instance.json
    """
    
    def __init__(self, config_path: str = "src/structural/market_proxy_instance.json"):
        self.root = Path(__file__).parent.parent.parent
        self.config_path = self.root / config_path
        self._config = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Proxy Instance config not found at {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_ingestion_binding(self, market: str, role: str) -> List[Path]:
        """
        Returns list of absolute file paths for a given role in a market.
        e.g. ('US', 'benchmark_equity') -> [Path('.../SPY.csv')]
        """
        m_cfg = self._config.get(market)
        if not m_cfg:
            raise ValueError(f"Market {market} not defined in Proxy Instance")
            
        tickers = m_cfg["roles"].get(role, [])
        bindings = m_cfg["ingestion_binding"]
        
        paths = []
        for t in tickers:
            rel_path = bindings.get(t)
            if not rel_path:
                continue # or raise error? Contract says Fail Closed for Primary.
            paths.append(self.root / rel_path)
            
        return paths

    def get_proxy_status(self, market: str) -> str:
        return self._config.get(market, {}).get("status", "UNKNOWN")

    def get_proxy_version(self, market: str) -> str:
        return self._config.get(market, {}).get("version", "UNKNOWN")
