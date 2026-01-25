"""
Ingestion Coverage Audit (L12 - Evolution Phase / Regime Audit).
Audits symbol × time ingestion coverage for regime inputs.

SAFETY INVARIANTS:
- Read-only audit.
- Does not modify data.
- Does not backfill gaps.
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum


class CoverageStatus(str, Enum):
    """Coverage status for a symbol."""
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    PARTIAL = "PARTIAL"


@dataclass
class SymbolCoverage:
    """Coverage information for a single symbol."""
    symbol: str
    status: CoverageStatus
    earliest_date: Optional[date]
    latest_date: Optional[date]
    total_days: int
    missing_days: int
    coverage_pct: float


class IngestionCoverageAudit:
    """
    Audits ingestion coverage for regime-required symbols.
    
    SAFETY GUARANTEES:
    - Read-only (does not modify data).
    - Does not backfill gaps.
    - Produces diagnostic output.
    """
    
    def __init__(self):
        self._coverage_results: Dict[str, SymbolCoverage] = {}
        self._audit_timestamp = datetime.now()
    
    def audit_symbol_coverage(
        self,
        symbol: str,
        available_dates: List[date],
        required_lookback_days: int
    ) -> SymbolCoverage:
        """
        Audit coverage for a single symbol.
        
        Returns coverage status without modifying data.
        """
        if not available_dates:
            coverage = SymbolCoverage(
                symbol=symbol,
                status=CoverageStatus.MISSING,
                earliest_date=None,
                latest_date=None,
                total_days=0,
                missing_days=required_lookback_days,
                coverage_pct=0.0
            )
        else:
            sorted_dates = sorted(available_dates)
            earliest = sorted_dates[0]
            latest = sorted_dates[-1]
            
            # Calculate expected trading days (approx 252/year)
            date_range = (latest - earliest).days
            expected_days = int(date_range * 252 / 365)  # Approx trading days
            actual_days = len(sorted_dates)
            
            if actual_days >= required_lookback_days:
                status = CoverageStatus.PRESENT
            elif actual_days > 0:
                status = CoverageStatus.PARTIAL
            else:
                status = CoverageStatus.MISSING
            
            coverage = SymbolCoverage(
                symbol=symbol,
                status=status,
                earliest_date=earliest,
                latest_date=latest,
                total_days=actual_days,
                missing_days=max(0, required_lookback_days - actual_days),
                coverage_pct=min(100.0, (actual_days / required_lookback_days) * 100) if required_lookback_days > 0 else 100.0
            )
        
        self._coverage_results[symbol] = coverage
        return coverage
    
    def audit_all_symbols(
        self,
        symbol_data: Dict[str, List[date]],
        lookback_requirements: Dict[str, int]
    ) -> Dict[str, SymbolCoverage]:
        """
        Audit coverage for all required symbols.
        
        symbol_data: {symbol: [available_dates]}
        lookback_requirements: {symbol: required_days}
        """
        required_symbols = set(lookback_requirements.keys())
        available_symbols = set(symbol_data.keys())
        
        # Check all required symbols
        for symbol in required_symbols:
            dates = symbol_data.get(symbol, [])
            lookback = lookback_requirements.get(symbol, 252)
            self.audit_symbol_coverage(symbol, dates, lookback)
        
        return self._coverage_results.copy()
    
    def get_missing_symbols(self) -> List[str]:
        """Get symbols that are completely missing."""
        return [
            s for s, c in self._coverage_results.items()
            if c.status == CoverageStatus.MISSING
        ]
    
    def get_partial_symbols(self) -> List[str]:
        """Get symbols with partial coverage."""
        return [
            s for s, c in self._coverage_results.items()
            if c.status == CoverageStatus.PARTIAL
        ]
    
    def generate_coverage_matrix(self) -> Dict[str, Any]:
        """
        Generate coverage matrix report.
        
        OBL-RG-SYMBOLS: Presence/absence must be explicit.
        """
        return {
            "report_type": "REGIME_COVERAGE_MATRIX",
            "generated_at": self._audit_timestamp.isoformat(),
            "total_symbols_checked": len(self._coverage_results),
            "present": len([c for c in self._coverage_results.values() if c.status == CoverageStatus.PRESENT]),
            "partial": len([c for c in self._coverage_results.values() if c.status == CoverageStatus.PARTIAL]),
            "missing": len([c for c in self._coverage_results.values() if c.status == CoverageStatus.MISSING]),
            "coverage_details": {
                s: {
                    "status": c.status.value,
                    "earliest_date": c.earliest_date.isoformat() if c.earliest_date else None,
                    "latest_date": c.latest_date.isoformat() if c.latest_date else None,
                    "total_days": c.total_days,
                    "missing_days": c.missing_days,
                    "coverage_pct": round(c.coverage_pct, 2)
                }
                for s, c in self._coverage_results.items()
            },
            "missing_symbols": self.get_missing_symbols(),
            "partial_symbols": self.get_partial_symbols()
        }
