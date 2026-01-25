"""
Undefined Regime Attribution (L12 - Evolution Phase / Regime Audit).
Attributes every undefined regime to a root cause.

SAFETY INVARIANTS:
- Read-only audit.
- Does not suppress undefined states.
- Does not auto-fix issues.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class UndefinedCause(str, Enum):
    """Root causes for undefined regime."""
    MISSING_SYMBOL = "MISSING_SYMBOL"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    TEMPORAL_MISALIGNMENT = "TEMPORAL_MISALIGNMENT"
    INVALID_STATE = "INVALID_STATE"
    COMPUTATION_ERROR = "COMPUTATION_ERROR"
    UNATTRIBUTED = "UNATTRIBUTED"  # Should never happen - indicates audit failure


@dataclass
class UndefinedAttribution:
    """Attribution for a single undefined regime occurrence."""
    timestamp: datetime
    cause: UndefinedCause
    details: str
    affected_symbols: List[str]
    resolution_hint: str


class UndefinedAttributionReport:
    """
    Attributes undefined regimes to root causes.
    
    SAFETY GUARANTEES:
    - Does not suppress undefined states.
    - Does not auto-fix issues.
    - Produces explicit cause attribution.
    
    OBL-RG-ATTRIBUTION: Every regime = undefined must have a cause.
    """
    
    def __init__(self):
        self._attributions: List[UndefinedAttribution] = []
        self._audit_timestamp = datetime.now()
        self._unattributed_count = 0
    
    def attribute_undefined(
        self,
        timestamp: datetime,
        missing_symbols: List[str],
        insufficient_symbols: List[str],
        misaligned_symbols: List[str],
        computation_error: Optional[str] = None
    ) -> UndefinedAttribution:
        """
        Attribute an undefined regime occurrence.
        """
        # Determine primary cause
        if missing_symbols:
            cause = UndefinedCause.MISSING_SYMBOL
            details = f"Missing symbols: {', '.join(missing_symbols)}"
            affected = missing_symbols
            hint = f"Ingest data for: {', '.join(missing_symbols)}"
        elif insufficient_symbols:
            cause = UndefinedCause.INSUFFICIENT_HISTORY
            details = f"Insufficient history: {', '.join(insufficient_symbols)}"
            affected = insufficient_symbols
            hint = f"Extend history for: {', '.join(insufficient_symbols)}"
        elif misaligned_symbols:
            cause = UndefinedCause.TEMPORAL_MISALIGNMENT
            details = f"Misaligned symbols: {', '.join(misaligned_symbols)}"
            affected = misaligned_symbols
            hint = "Align symbol timestamps or implement interpolation"
        elif computation_error:
            cause = UndefinedCause.COMPUTATION_ERROR
            details = f"Computation error: {computation_error}"
            affected = []
            hint = "Review regime computation logic"
        else:
            cause = UndefinedCause.INVALID_STATE
            details = "Data present but state invalid"
            affected = []
            hint = "Review regime state transition logic"
        
        attribution = UndefinedAttribution(
            timestamp=timestamp,
            cause=cause,
            details=details,
            affected_symbols=affected,
            resolution_hint=hint
        )
        
        self._attributions.append(attribution)
        return attribution
    
    def attribute_batch(
        self,
        undefined_timestamps: List[datetime],
        symbol_issues: Dict[str, Dict[str, List[str]]]  # timestamp -> {issue_type: [symbols]}
    ) -> List[UndefinedAttribution]:
        """
        Attribute a batch of undefined regime occurrences.
        """
        results = []
        
        for ts in undefined_timestamps:
            ts_str = ts.isoformat()
            issues = symbol_issues.get(ts_str, {})
            
            attribution = self.attribute_undefined(
                timestamp=ts,
                missing_symbols=issues.get("missing", []),
                insufficient_symbols=issues.get("insufficient", []),
                misaligned_symbols=issues.get("misaligned", []),
                computation_error=None
            )
            results.append(attribution)
        
        return results
    
    def get_attribution_summary(self) -> Dict[str, int]:
        """Get count of attributions by cause."""
        summary = {cause.value: 0 for cause in UndefinedCause}
        for attr in self._attributions:
            summary[attr.cause.value] += 1
        return summary
    
    def get_unattributed_count(self) -> int:
        """Get count of unattributed undefined regimes (should be 0)."""
        return sum(1 for a in self._attributions if a.cause == UndefinedCause.UNATTRIBUTED)
    
    def generate_attribution_table(self) -> Dict[str, Any]:
        """
        Generate undefined regime attribution table.
        
        OBL-RG-ATTRIBUTION: Every undefined must have a cause.
        """
        summary = self.get_attribution_summary()
        unattributed = self.get_unattributed_count()
        
        return {
            "report_type": "UNDEFINED_REGIME_ATTRIBUTION",
            "generated_at": self._audit_timestamp.isoformat(),
            "total_undefined_count": len(self._attributions),
            "unattributed_count": unattributed,
            "all_attributed": unattributed == 0,
            "attribution_summary": summary,
            "primary_cause": max(summary.items(), key=lambda x: x[1])[0] if summary else None,
            "attributions": [
                {
                    "timestamp": a.timestamp.isoformat(),
                    "cause": a.cause.value,
                    "details": a.details,
                    "affected_symbols": a.affected_symbols,
                    "resolution_hint": a.resolution_hint
                }
                for a in self._attributions[:50]  # Limit to first 50
            ],
            "resolution_priorities": self._get_resolution_priorities()
        }
    
    def _get_resolution_priorities(self) -> List[Dict[str, Any]]:
        """Generate prioritized resolution list."""
        # Aggregate by affected symbol
        symbol_impact: Dict[str, int] = {}
        for attr in self._attributions:
            for sym in attr.affected_symbols:
                symbol_impact[sym] = symbol_impact.get(sym, 0) + 1
        
        # Sort by impact
        sorted_symbols = sorted(symbol_impact.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"symbol": sym, "impact_count": count, "priority_rank": i + 1}
            for i, (sym, count) in enumerate(sorted_symbols[:10])
        ]
