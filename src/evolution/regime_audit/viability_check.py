"""
State Construction Viability Check (L12 - Evolution Phase / Regime Audit).
Checks if regime state can be constructed from available data.

SAFETY INVARIANTS:
- Read-only audit.
- Does not modify data or logic.
- Does not auto-fix issues.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ViabilityStatus(str, Enum):
    """Viability status for regime state construction."""
    VIABLE = "VIABLE"
    DEGRADED = "DEGRADED"  # Possible with fallbacks
    NOT_VIABLE = "NOT_VIABLE"


class BlockingReason(str, Enum):
    """Reasons why state construction is blocked."""
    MISSING_SYMBOL = "MISSING_SYMBOL"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    TEMPORAL_MISALIGNMENT = "TEMPORAL_MISALIGNMENT"
    MULTIPLE_ISSUES = "MULTIPLE_ISSUES"


@dataclass
class ViabilityCheck:
    """Result of a viability check for a specific date/context."""
    check_date: datetime
    status: ViabilityStatus
    blocking_reasons: List[BlockingReason]
    missing_inputs: List[str]
    degradation_notes: List[str]


class StateViabilityCheck:
    """
    Checks if regime state can be constructed.
    
    SAFETY GUARANTEES:
    - Read-only (does not modify data).
    - Does not auto-fix issues.
    - Produces explicit failure reasons.
    
    OBL-RG-VIABILITY: Inputs must be sufficient to compute regime state.
    """
    
    def __init__(self):
        self._viability_checks: List[ViabilityCheck] = []
        self._audit_timestamp = datetime.now()
    
    def check_viability(
        self,
        check_date: datetime,
        required_symbols: List[str],
        available_symbols: List[str],
        symbol_sufficiency: Dict[str, bool],
        symbol_alignment: Dict[str, bool]
    ) -> ViabilityCheck:
        """
        Check if regime state can be constructed at a given point.
        """
        blocking_reasons = []
        missing_inputs = []
        degradation_notes = []
        
        # Check for missing symbols
        missing_symbols = [s for s in required_symbols if s not in available_symbols]
        if missing_symbols:
            blocking_reasons.append(BlockingReason.MISSING_SYMBOL)
            missing_inputs.extend(missing_symbols)
        
        # Check for insufficient history
        insufficient = [s for s, ok in symbol_sufficiency.items() if not ok]
        if insufficient:
            blocking_reasons.append(BlockingReason.INSUFFICIENT_HISTORY)
            missing_inputs.extend([f"{s}:history" for s in insufficient])
        
        # Check for misalignment
        misaligned = [s for s, ok in symbol_alignment.items() if not ok]
        if misaligned:
            blocking_reasons.append(BlockingReason.TEMPORAL_MISALIGNMENT)
            degradation_notes.append(f"Misaligned: {', '.join(misaligned)}")
        
        # Determine overall status
        if not blocking_reasons:
            status = ViabilityStatus.VIABLE
        elif len(blocking_reasons) == 1 and blocking_reasons[0] == BlockingReason.TEMPORAL_MISALIGNMENT:
            status = ViabilityStatus.DEGRADED
            degradation_notes.append("Regime can be computed with interpolation (not auto-applied)")
        else:
            status = ViabilityStatus.NOT_VIABLE
            if len(blocking_reasons) > 1:
                blocking_reasons = [BlockingReason.MULTIPLE_ISSUES]
        
        check = ViabilityCheck(
            check_date=check_date,
            status=status,
            blocking_reasons=blocking_reasons,
            missing_inputs=missing_inputs,
            degradation_notes=degradation_notes
        )
        
        self._viability_checks.append(check)
        return check
    
    def check_overall_viability(
        self,
        required_symbols: List[str],
        symbol_coverage: Dict[str, str],  # symbol -> "PRESENT"|"MISSING"|"PARTIAL"
        symbol_sufficiency: Dict[str, bool],
        symbol_alignment: Dict[str, bool]
    ) -> ViabilityCheck:
        """
        Check overall viability for regime construction.
        """
        available = [s for s, status in symbol_coverage.items() if status != "MISSING"]
        
        return self.check_viability(
            check_date=datetime.now(),
            required_symbols=required_symbols,
            available_symbols=available,
            symbol_sufficiency=symbol_sufficiency,
            symbol_alignment=symbol_alignment
        )
    
    def generate_viability_report(self) -> Dict[str, Any]:
        """
        Generate state viability report.
        
        OBL-RG-VIABILITY: Failure reasons must be explicit.
        """
        latest = self._viability_checks[-1] if self._viability_checks else None
        
        return {
            "report_type": "STATE_CONSTRUCTION_VIABILITY",
            "generated_at": self._audit_timestamp.isoformat(),
            "overall_status": latest.status.value if latest else "UNKNOWN",
            "blocking_reasons": [r.value for r in latest.blocking_reasons] if latest else [],
            "missing_inputs": latest.missing_inputs if latest else [],
            "degradation_notes": latest.degradation_notes if latest else [],
            "viability_summary": {
                "can_construct_regime": latest.status == ViabilityStatus.VIABLE if latest else False,
                "can_construct_degraded": latest.status in [ViabilityStatus.VIABLE, ViabilityStatus.DEGRADED] if latest else False,
                "total_checks": len(self._viability_checks)
            },
            "recommendation": self._get_recommendation(latest) if latest else "No viability check performed"
        }
    
    def _get_recommendation(self, check: ViabilityCheck) -> str:
        """Generate actionable recommendation."""
        if check.status == ViabilityStatus.VIABLE:
            return "Regime state construction is viable. Proceed with evaluation."
        elif check.status == ViabilityStatus.DEGRADED:
            return "Regime can be computed with degraded accuracy. Consider data remediation."
        else:
            issues = ", ".join([r.value for r in check.blocking_reasons])
            return f"Regime state CANNOT be constructed. Issues: {issues}. Data remediation required."
