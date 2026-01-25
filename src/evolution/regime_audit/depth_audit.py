"""
Historical Depth Audit (L12 - Evolution Phase / Regime Audit).
Verifies lookback windows are satisfiable with available data.

SAFETY INVARIANTS:
- Read-only audit.
- Does not modify data.
- Does not backfill gaps.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum


class SufficiencyStatus(str, Enum):
    """Sufficiency status for a lookback window."""
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    MARGINAL = "MARGINAL"  # <10% buffer


@dataclass
class LookbackSufficiency:
    """Sufficiency check for a symbol's lookback window."""
    symbol: str
    required_days: int
    available_days: int
    status: SufficiencyStatus
    gap_days: int
    buffer_pct: float


@dataclass
class HistoricalGap:
    """A gap in historical data."""
    symbol: str
    gap_start: date
    gap_end: date
    gap_days: int


class DepthAudit:
    """
    Audits historical depth for regime lookback windows.
    
    SAFETY GUARANTEES:
    - Read-only (does not modify data).
    - Does not backfill.
    - Produces diagnostic output.
    
    OBL-RG-DEPTH: Required lookback windows must be satisfiable.
    """
    
    def __init__(self):
        self._sufficiency_results: Dict[str, LookbackSufficiency] = {}
        self._gaps: List[HistoricalGap] = []
        self._audit_timestamp = datetime.now()
    
    def check_sufficiency(
        self,
        symbol: str,
        required_days: int,
        available_days: int
    ) -> LookbackSufficiency:
        """
        Check if a symbol has sufficient historical depth.
        """
        gap_days = max(0, required_days - available_days)
        
        if available_days >= required_days:
            buffer_pct = ((available_days - required_days) / required_days) * 100 if required_days > 0 else 100
            if buffer_pct < 10:
                status = SufficiencyStatus.MARGINAL
            else:
                status = SufficiencyStatus.SUFFICIENT
        else:
            buffer_pct = -((required_days - available_days) / required_days) * 100 if required_days > 0 else 0
            status = SufficiencyStatus.INSUFFICIENT
        
        result = LookbackSufficiency(
            symbol=symbol,
            required_days=required_days,
            available_days=available_days,
            status=status,
            gap_days=gap_days,
            buffer_pct=round(buffer_pct, 2)
        )
        
        self._sufficiency_results[symbol] = result
        return result
    
    def identify_gaps(
        self,
        symbol: str,
        available_dates: List[date],
        expected_frequency_days: int = 1
    ) -> List[HistoricalGap]:
        """
        Identify gaps in historical data.
        """
        if len(available_dates) < 2:
            return []
        
        sorted_dates = sorted(available_dates)
        symbol_gaps = []
        
        for i in range(1, len(sorted_dates)):
            delta = (sorted_dates[i] - sorted_dates[i-1]).days
            # Allow for weekends (2-day gap normal for daily data)
            if delta > 3:  # More than a weekend gap
                gap = HistoricalGap(
                    symbol=symbol,
                    gap_start=sorted_dates[i-1],
                    gap_end=sorted_dates[i],
                    gap_days=delta
                )
                symbol_gaps.append(gap)
                self._gaps.append(gap)
        
        return symbol_gaps
    
    def audit_all_depths(
        self,
        symbol_day_counts: Dict[str, int],
        lookback_requirements: Dict[str, int]
    ) -> Dict[str, LookbackSufficiency]:
        """
        Audit depth for all required symbols.
        """
        for symbol, required in lookback_requirements.items():
            available = symbol_day_counts.get(symbol, 0)
            self.check_sufficiency(symbol, required, available)
        
        return self._sufficiency_results.copy()
    
    def get_insufficient_symbols(self) -> List[str]:
        """Get symbols with insufficient history."""
        return [
            s for s, r in self._sufficiency_results.items()
            if r.status == SufficiencyStatus.INSUFFICIENT
        ]
    
    def generate_sufficiency_report(self) -> Dict[str, Any]:
        """
        Generate lookback sufficiency report.
        
        OBL-RG-DEPTH: Gaps must be identified.
        """
        return {
            "report_type": "LOOKBACK_SUFFICIENCY",
            "generated_at": self._audit_timestamp.isoformat(),
            "total_symbols_checked": len(self._sufficiency_results),
            "sufficient": len([r for r in self._sufficiency_results.values() if r.status == SufficiencyStatus.SUFFICIENT]),
            "marginal": len([r for r in self._sufficiency_results.values() if r.status == SufficiencyStatus.MARGINAL]),
            "insufficient": len([r for r in self._sufficiency_results.values() if r.status == SufficiencyStatus.INSUFFICIENT]),
            "sufficiency_details": {
                s: {
                    "required_days": r.required_days,
                    "available_days": r.available_days,
                    "status": r.status.value,
                    "gap_days": r.gap_days,
                    "buffer_pct": r.buffer_pct
                }
                for s, r in self._sufficiency_results.items()
            },
            "insufficient_symbols": self.get_insufficient_symbols(),
            "gaps_found": len(self._gaps),
            "gaps": [
                {
                    "symbol": g.symbol,
                    "gap_start": g.gap_start.isoformat(),
                    "gap_end": g.gap_end.isoformat(),
                    "gap_days": g.gap_days
                }
                for g in self._gaps
            ]
        }
