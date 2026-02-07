"""
India Market Loader (DATA-INDIA-LOADER).
Role-based proxy ingestion for India market with strict parity validation.

DEPRECATION NOTICE:
- The "RELIANCE.NS" single-stock surrogate is DEPRECATED as of 2026-01-30.
- All factor calculations MUST use canonical proxies or fail explicitly.

SAFETY INVARIANTS:
- ROLE-BASED: Proxies are bound to roles, not symbols.
- FAIL-CLOSED: Missing proxy returns explicit failure, not fallback.
- NO INFERENCE: No surrogate substitution or synthetic generation.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Canonical Proxy Bindings (Role -> Expected Paths)
INDIA_PROXY_BINDINGS = {
    "equity_core": {
        "role": "Primary market trend indicator (NIFTY50)",
        "paths": [
            PROJECT_ROOT / "data" / "india" / "NIFTY50.csv",
            PROJECT_ROOT / "data" / "regime" / "raw" / "^NSEI.csv",
            PROJECT_ROOT / "data" / "regime" / "raw" / "NIFTYBEES.csv",
        ],
        "required_history": 200
    },
    "sector_proxy": {
        "role": "Banking/Financial sector for breadth (BANKNIFTY)",
        "paths": [
            PROJECT_ROOT / "data" / "india" / "BANKNIFTY.csv",
            PROJECT_ROOT / "data" / "regime" / "raw" / "^NSEBANK.csv",
        ],
        "required_history": 200
    },
    "volatility_gauge": {
        "role": "Market fear/greed (INDIAVIX)",
        "paths": [
            PROJECT_ROOT / "data" / "india" / "INDIAVIX.csv",
            PROJECT_ROOT / "data" / "regime" / "raw" / "^INDIAVIX.csv",
        ],
        "required_history": 50
    },
    "rates_anchor": {
        "role": "Liquidity/Rates (IN10Y G-Sec) - Monthly from FRED/IMF",
        "paths": [
            PROJECT_ROOT / "data" / "india" / "IN10Y.csv",
            PROJECT_ROOT / "data" / "regime" / "raw" / "IN10Y.csv",
        ],
        "required_history": 60,  # Monthly data: 60 months = 5 years
        "frequency": "monthly"
    }
}

# DEPRECATED Surrogate - Must never be used
DEPRECATED_SURROGATE = PROJECT_ROOT / "data" / "raw" / "api_based" / "angel" / "historical"


class IndiaMarketLoader:
    """
    Role-based loader for India canonical proxies.
    Returns explicit failure diagnostics if any role cannot be fulfilled.
    """
    
    def __init__(self):
        self.parity_status = {}
        self.gaps = []
    
    def load_proxy(self, role: str) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
        """
        Attempts to load proxy for the given role.
        Returns (DataFrame, Diagnostic) or (None, Diagnostic).
        """
        if role not in INDIA_PROXY_BINDINGS:
            return None, {"status": "INVALID_ROLE", "role": role}
        
        binding = INDIA_PROXY_BINDINGS[role]
        
        for path in binding["paths"]:
            if path.exists():
                try:
                    df = pd.read_csv(path)
                    df.columns = [c.title() for c in df.columns]
                    
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'])
                        df = df.set_index('Date').sort_index()
                    
                    row_count = len(df)
                    required = binding["required_history"]
                    
                    if row_count < required:
                        return None, {
                            "status": "INSUFFICIENT_HISTORY",
                            "role": role,
                            "path": str(path),
                            "rows": row_count,
                            "required": required
                        }
                    
                    return df, {
                        "status": "ACTIVE",
                        "role": role,
                        "path": str(path),
                        "rows": row_count
                    }
                except Exception as e:
                    return None, {
                        "status": "PARSE_ERROR",
                        "role": role,
                        "path": str(path),
                        "error": str(e)
                    }
        
        # No path found
        return None, {
            "status": "NOT_INGESTED",
            "role": role,
            "searched_paths": [str(p) for p in binding["paths"]]
        }
    
    def check_parity(self) -> Dict[str, Any]:
        """
        Checks all proxy roles and returns parity status.
        """
        all_active = True
        diagnostics = {}
        
        for role in INDIA_PROXY_BINDINGS.keys():
            df, diag = self.load_proxy(role)
            diagnostics[role] = diag
            if diag["status"] != "ACTIVE":
                all_active = False
                self.gaps.append(diag)
        
        parity_status = "CANONICAL" if all_active else "DEGRADED"
        
        result = {
            "market": "INDIA",
            "computed_at": datetime.now().isoformat(),
            "parity_status": parity_status,
            "proxy_diagnostics": diagnostics,
            "gaps": self.gaps,
            "canonical_ready": all_active
        }
        
        self.parity_status = result
        return result
    
    def load_equity_core(self) -> Tuple[Optional[pd.DataFrame], str]:
        """Load NIFTY50 or equivalent for Momentum/Regime."""
        df, diag = self.load_proxy("equity_core")
        return df, diag.get("status", "UNKNOWN")
    
    def load_sector_proxy(self) -> Tuple[Optional[pd.DataFrame], str]:
        """Load BANKNIFTY for Breadth."""
        df, diag = self.load_proxy("sector_proxy")
        return df, diag.get("status", "UNKNOWN")
    
    def load_volatility(self) -> Tuple[Optional[float], str]:
        """Load India VIX for Volatility factor."""
        df, diag = self.load_proxy("volatility_gauge")
        if df is not None and 'Close' in df.columns:
            return df['Close'].iloc[-1], "ACTIVE"
        return None, diag.get("status", "UNKNOWN")
    
    def load_rates(self) -> Tuple[Optional[float], str]:
        """Load IN10Y for Liquidity factor."""
        df, diag = self.load_proxy("rates_anchor")
        if df is not None and 'Close' in df.columns:
            return df['Close'].iloc[-1], "ACTIVE"
        return None, diag.get("status", "UNKNOWN")


def run_parity_check():
    """
    Standalone parity check execution.
    """
    loader = IndiaMarketLoader()
    result = loader.check_parity()
    
    output_path = PROJECT_ROOT / "docs" / "intelligence" / "india_parity_status.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print(f"India Parity Status: {result['parity_status']}")
    print(f"Gaps Found: {len(result['gaps'])}")
    for gap in result['gaps']:
        print(f"  - {gap['role']}: {gap['status']}")
    
    return result


if __name__ == "__main__":
    run_parity_check()
