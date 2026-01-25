from dataclasses import dataclass
from datetime import datetime
from typing import List, Set
from enum import Enum, unique

@unique
class IntegrityViolationType(str, Enum):
    ORPHAN_NARRATIVE = "ORPHAN_NARRATIVE" # Narrative references non-existent signal
    ORPHAN_REPORT = "ORPHAN_REPORT"       # Report references non-existent narrative
    DUPLICATE_ID = "DUPLICATE_ID"
    MISSING_ASSET = "MISSING_ASSET"

@dataclass
class IntegrityViolation:
    violation_type: IntegrityViolationType
    entity_id: str
    description: str
    detected_at: datetime

class IntegrityChecker:
    """
    Validates cross-layer invariants.
    """
    def check_narrative_signal_refs(self, 
                                     narrative_signal_ids: List[str], 
                                     known_signal_ids: Set[str]) -> List[IntegrityViolation]:
        violations = []
        for sig_id in narrative_signal_ids:
            if sig_id not in known_signal_ids:
                violations.append(IntegrityViolation(
                    violation_type=IntegrityViolationType.ORPHAN_NARRATIVE,
                    entity_id=sig_id,
                    description=f"Signal ID {sig_id} referenced by narrative does not exist.",
                    detected_at=datetime.utcnow()
                ))
        return violations

    def check_report_narrative_refs(self, 
                                     report_narrative_ids: List[str], 
                                     known_narrative_ids: Set[str]) -> List[IntegrityViolation]:
        violations = []
        for narr_id in report_narrative_ids:
            if narr_id not in known_narrative_ids:
                violations.append(IntegrityViolation(
                    violation_type=IntegrityViolationType.ORPHAN_REPORT,
                    entity_id=narr_id,
                    description=f"Narrative ID {narr_id} referenced by report does not exist.",
                    detected_at=datetime.utcnow()
                ))
        return violations
