"""
Regime Symbol Enumeration (L12 - Evolution Phase / Regime Audit).
Enumerates all symbols required for regime classification.

SAFETY INVARIANTS:
- Read-only audit.
- Does not modify regime logic.
- Does not add symbols.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class SymbolRole(str, Enum):
    """Roles that symbols play in regime classification."""
    EQUITY_PROXY = "EQUITY_PROXY"
    VOLATILITY_PROXY = "VOLATILITY_PROXY"
    RATES_PROXY = "RATES_PROXY"
    CREDIT_PROXY = "CREDIT_PROXY"
    MACRO_INDICATOR = "MACRO_INDICATOR"
    MOMENTUM_SIGNAL = "MOMENTUM_SIGNAL"


@dataclass
class RequiredSymbol:
    """A symbol required for regime classification."""
    symbol: str
    role: SymbolRole
    required_for: List[str]  # Which regime states require this
    lookback_days: int
    description: str


class SymbolEnumeration:
    """
    Enumerates symbols required for regime classification.
    
    SAFETY GUARANTEES:
    - Read-only (does not modify data).
    - Enumeration only (does not add symbols).
    - Produces diagnostic output.
    """
    
    def __init__(self):
        self._required_symbols: List[RequiredSymbol] = []
        self._enumeration_timestamp = datetime.now()
    
    def enumerate_regime_requirements(self) -> List[RequiredSymbol]:
        """
        Enumerate all symbols required for regime classification.
        
        This is based on the regime definition documents.
        """
        # Based on epistemic/policies/regime_layer_policy.md
        self._required_symbols = [
            RequiredSymbol(
                symbol="QQQ",
                role=SymbolRole.EQUITY_PROXY,
                required_for=["RISK_ON", "RISK_OFF", "TRANSITION"],
                lookback_days=252,
                description="NASDAQ 100 ETF - primary equity proxy"
            ),
            RequiredSymbol(
                symbol="SPY",
                role=SymbolRole.EQUITY_PROXY,
                required_for=["RISK_ON", "RISK_OFF", "TRANSITION"],
                lookback_days=252,
                description="S&P 500 ETF - secondary equity proxy"
            ),
            RequiredSymbol(
                symbol="VIX",
                role=SymbolRole.VOLATILITY_PROXY,
                required_for=["RISK_OFF", "TRANSITION", "CRISIS"],
                lookback_days=63,
                description="CBOE Volatility Index"
            ),
            RequiredSymbol(
                symbol="^TNX",
                role=SymbolRole.RATES_PROXY,
                required_for=["RISING_RATES", "FALLING_RATES"],
                lookback_days=126,
                description="10-Year Treasury Yield"
            ),
            RequiredSymbol(
                symbol="^TYX",
                role=SymbolRole.RATES_PROXY,
                required_for=["RISING_RATES", "FALLING_RATES"],
                lookback_days=126,
                description="30-Year Treasury Yield"
            ),
            RequiredSymbol(
                symbol="HYG",
                role=SymbolRole.CREDIT_PROXY,
                required_for=["CREDIT_RISK", "CREDIT_NORMAL"],
                lookback_days=63,
                description="High Yield Corporate Bond ETF"
            ),
            RequiredSymbol(
                symbol="LQD",
                role=SymbolRole.CREDIT_PROXY,
                required_for=["CREDIT_RISK", "CREDIT_NORMAL"],
                lookback_days=63,
                description="Investment Grade Corporate Bond ETF"
            ),
        ]
        
        return self._required_symbols
    
    def get_symbols_by_role(self, role: SymbolRole) -> List[RequiredSymbol]:
        """Get all symbols with a specific role."""
        return [s for s in self._required_symbols if s.role == role]
    
    def get_max_lookback(self) -> int:
        """Get the maximum lookback required across all symbols."""
        if not self._required_symbols:
            return 0
        return max(s.lookback_days for s in self._required_symbols)
    
    def generate_requirements_report(self) -> Dict[str, Any]:
        """
        Generate regime symbol requirements report.
        
        OBL-RG-SYMBOLS: All symbols required must be enumerated.
        """
        if not self._required_symbols:
            self.enumerate_regime_requirements()
        
        return {
            "report_type": "REGIME_SYMBOL_REQUIREMENTS",
            "generated_at": self._enumeration_timestamp.isoformat(),
            "total_symbols": len(self._required_symbols),
            "max_lookback_days": self.get_max_lookback(),
            "symbols": [
                {
                    "symbol": s.symbol,
                    "role": s.role.value,
                    "required_for": s.required_for,
                    "lookback_days": s.lookback_days,
                    "description": s.description
                }
                for s in self._required_symbols
            ],
            "by_role": {
                role.value: [s.symbol for s in self._required_symbols if s.role == role]
                for role in SymbolRole
            }
        }
