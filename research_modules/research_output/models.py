"""Research Output - Models"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

@dataclass
class ResearchReport:
    report_id: str
    report_type: str  # daily/weekly
    report_date: str
    market_scope: str
    included_symbols: List[str]
    key_changes: List[Dict]
    risk_summary: Dict
    narrative_summary: str
    confidence_note: str
    generated_at: str
    version: str
    
    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "report_date": self.report_date,
            "market_scope": self.market_scope,
            "included_symbols": self.included_symbols,
            "key_changes": self.key_changes,
            "risk_summary": self.risk_summary,
            "narrative_summary": self.narrative_summary,
            "confidence_note": self.confidence_note,
            "generated_at": self.generated_at,
            "version": self.version,
        }
    
    @classmethod
    def create(cls, report_type: str, date_str: str, symbols: List[str], 
               changes: List[Dict], risk: Dict, summary: str, confidence: str):
        return cls(
            report_id=str(uuid.uuid4())[:8],
            report_type=report_type,
            report_date=date_str,
            market_scope="US Equities",
            included_symbols=symbols,
            key_changes=changes,
            risk_summary=risk,
            narrative_summary=summary,
            confidence_note=confidence,
            generated_at=datetime.utcnow().isoformat(),
            version="1.0.0",
        )
