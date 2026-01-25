import uuid
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from research_reports.core.models import ResearchReport

@dataclass(frozen=True)
class ReportDiff:
    """
    Structural difference between two report versions.
    """
    diff_id: str
    old_version_id: Optional[str]
    new_version_id: str
    generated_at: datetime
    
    # Narrative Changes
    added_narrative_ids: List[str]
    removed_narrative_ids: List[str]
    
    # Confidence Changes
    confidence_deltas: Dict[str, float] # Narrative ID -> Delta
    avg_confidence_delta: float
    
    classification: str # "MINOR_UPDATE", "MAJOR_REVISION", "NEW_REPORT"

@dataclass(frozen=True)
class ReportVersionMetadata:
    """
    Audit trail metadata for a report.
    """
    report_id: str
    version: int
    parent_version_pk: Optional[str] # Pointer to previous version entry ID if any (not just report_id)
    
    generation_reason: str # "SCHEDULED", "MANUAL", "CORRECTION"
    input_fingerprint: str # Hash of inputs
    
    diff_id: Optional[str] # Link to diff against parent
    
    @staticmethod
    def compute_fingerprint(report: ResearchReport) -> str:
        # Canonical string representation of critical inputs
        # Narratives sorted by ID + Stats
        n_ids = sorted(report.included_narrative_ids)
        content = f"{n_ids}|{report.signal_stats}|{report.period_start}|{report.period_end}"
        return hashlib.sha256(content.encode()).hexdigest()
        
    def to_dict(self):
        return asdict(self)
