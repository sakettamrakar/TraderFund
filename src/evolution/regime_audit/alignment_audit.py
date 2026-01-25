"""
Temporal Alignment Audit (L12 - Evolution Phase / Regime Audit).
Verifies timestamp alignment across regime-required symbols.

SAFETY INVARIANTS:
- Read-only audit.
- Does not modify data.
- Does not interpolate missing data.
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class AlignmentStatus(str, Enum):
    """Alignment status for symbol pair."""
    ALIGNED = "ALIGNED"
    PARTIAL = "PARTIAL"
    MISALIGNED = "MISALIGNED"


@dataclass
class SymbolAlignment:
    """Alignment information for a symbol pair."""
    symbol_a: str
    symbol_b: str
    status: AlignmentStatus
    common_dates: int
    a_only_dates: int
    b_only_dates: int
    alignment_pct: float


@dataclass
class AlignmentGap:
    """A gap where symbols don't align."""
    date: date
    present_symbols: List[str]
    missing_symbols: List[str]


class AlignmentAudit:
    """
    Audits temporal alignment across regime-required symbols.
    
    SAFETY GUARANTEES:
    - Read-only (does not modify data).
    - Does not interpolate.
    - Produces diagnostic output.
    
    OBL-RG-ALIGNMENT: Symbols must align on timestamps.
    """
    
    def __init__(self):
        self._pairwise_alignments: List[SymbolAlignment] = []
        self._alignment_gaps: List[AlignmentGap] = []
        self._audit_timestamp = datetime.now()
    
    def check_pairwise_alignment(
        self,
        symbol_a: str,
        dates_a: Set[date],
        symbol_b: str,
        dates_b: Set[date]
    ) -> SymbolAlignment:
        """
        Check alignment between two symbols.
        """
        common = dates_a & dates_b
        a_only = dates_a - dates_b
        b_only = dates_b - dates_a
        
        total = len(dates_a | dates_b)
        common_count = len(common)
        
        if total == 0:
            alignment_pct = 0.0
            status = AlignmentStatus.MISALIGNED
        else:
            alignment_pct = (common_count / total) * 100
            if alignment_pct >= 95:
                status = AlignmentStatus.ALIGNED
            elif alignment_pct >= 70:
                status = AlignmentStatus.PARTIAL
            else:
                status = AlignmentStatus.MISALIGNED
        
        alignment = SymbolAlignment(
            symbol_a=symbol_a,
            symbol_b=symbol_b,
            status=status,
            common_dates=common_count,
            a_only_dates=len(a_only),
            b_only_dates=len(b_only),
            alignment_pct=round(alignment_pct, 2)
        )
        
        self._pairwise_alignments.append(alignment)
        return alignment
    
    def audit_all_alignments(
        self,
        symbol_dates: Dict[str, Set[date]]
    ) -> List[SymbolAlignment]:
        """
        Audit alignment across all symbol pairs.
        """
        symbols = list(symbol_dates.keys())
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                self.check_pairwise_alignment(
                    symbols[i], symbol_dates[symbols[i]],
                    symbols[j], symbol_dates[symbols[j]]
                )
        
        return self._pairwise_alignments.copy()
    
    def find_intersection(
        self,
        symbol_dates: Dict[str, Set[date]]
    ) -> Set[date]:
        """
        Find dates where ALL symbols have data.
        """
        if not symbol_dates:
            return set()
        
        all_date_sets = list(symbol_dates.values())
        common = all_date_sets[0]
        for date_set in all_date_sets[1:]:
            common = common & date_set
        
        return common
    
    def identify_alignment_gaps(
        self,
        symbol_dates: Dict[str, Set[date]],
        required_symbols: List[str]
    ) -> List[AlignmentGap]:
        """
        Identify dates where not all required symbols have data.
        """
        # Get all dates across all symbols
        all_dates: Set[date] = set()
        for dates in symbol_dates.values():
            all_dates.update(dates)
        
        gaps = []
        for d in sorted(all_dates):
            present = [s for s in required_symbols if d in symbol_dates.get(s, set())]
            missing = [s for s in required_symbols if d not in symbol_dates.get(s, set())]
            
            if missing:
                gap = AlignmentGap(
                    date=d,
                    present_symbols=present,
                    missing_symbols=missing
                )
                gaps.append(gap)
                self._alignment_gaps.append(gap)
        
        return gaps
    
    def generate_alignment_report(self) -> Dict[str, Any]:
        """
        Generate alignment heatmap report.
        
        OBL-RG-ALIGNMENT: Missing intersections must be surfaced.
        """
        return {
            "report_type": "TEMPORAL_ALIGNMENT",
            "generated_at": self._audit_timestamp.isoformat(),
            "total_pairs_checked": len(self._pairwise_alignments),
            "aligned_pairs": len([a for a in self._pairwise_alignments if a.status == AlignmentStatus.ALIGNED]),
            "partial_pairs": len([a for a in self._pairwise_alignments if a.status == AlignmentStatus.PARTIAL]),
            "misaligned_pairs": len([a for a in self._pairwise_alignments if a.status == AlignmentStatus.MISALIGNED]),
            "pairwise_alignment": [
                {
                    "symbol_a": a.symbol_a,
                    "symbol_b": a.symbol_b,
                    "status": a.status.value,
                    "common_dates": a.common_dates,
                    "alignment_pct": a.alignment_pct
                }
                for a in self._pairwise_alignments
            ],
            "alignment_gaps_count": len(self._alignment_gaps),
            "sample_gaps": [
                {
                    "date": g.date.isoformat(),
                    "present": g.present_symbols,
                    "missing": g.missing_symbols
                }
                for g in self._alignment_gaps[:20]  # Limit to first 20
            ]
        }
