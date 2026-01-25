import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum, unique

@unique
class ExplanationSourceType(str, Enum):
    NARRATIVE = "NARRATIVE"
    REPORT = "REPORT"
    QUERY = "QUERY"

@dataclass(frozen=True)
class NarrativeExplanation:
    """
    Immutable, versioned LLM explanation of a Narrative.
    """
    explanation_id: str
    source_type: ExplanationSourceType
    source_id: str # narrative_id
    
    explanation_text: str
    referenced_signal_ids: List[str]
    referenced_event_ids: List[str]
    
    stated_confidence_level: str # "HIGH", "MODERATE", "LOW"
    uncertainty_notes: str
    
    generated_at: datetime
    model_metadata: Dict[str, Any] # model name, version, temp, etc.
    version: int

    @classmethod
    def create(cls, source_id: str, text: str, signal_ids: List[str], 
               event_ids: List[str], conf: str, uncertainty: str, 
               model_meta: Dict) -> 'NarrativeExplanation':
        return cls(
            explanation_id=str(uuid.uuid4()),
            source_type=ExplanationSourceType.NARRATIVE,
            source_id=source_id,
            explanation_text=text,
            referenced_signal_ids=signal_ids,
            referenced_event_ids=event_ids,
            stated_confidence_level=conf,
            uncertainty_notes=uncertainty,
            generated_at=datetime.utcnow(),
            model_metadata=model_meta,
            version=1
        )

@dataclass(frozen=True)
class ReportExplanation:
    """
    Immutable, versioned LLM explanation of a Report.
    """
    explanation_id: str
    report_id: str
    
    explanation_summary: str
    key_changes: List[str]
    unresolved_questions: List[str]
    confidence_interpretation: str
    
    generated_at: datetime
    model_metadata: Dict[str, Any]
    version: int

    @classmethod
    def create(cls, report_id: str, summary: str, changes: List[str],
               questions: List[str], conf_interp: str, 
               model_meta: Dict) -> 'ReportExplanation':
        return cls(
            explanation_id=str(uuid.uuid4()),
            report_id=report_id,
            explanation_summary=summary,
            key_changes=changes,
            unresolved_questions=questions,
            confidence_interpretation=conf_interp,
            generated_at=datetime.utcnow(),
            model_metadata=model_meta,
            version=1
        )
