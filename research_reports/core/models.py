import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any
from signals.core.enums import Market
from .enums import ReportType

@dataclass(frozen=True)
class ResearchReport:
    """
    Time-bound Research Artifact.
    Immutable, Versioned.
    """
    report_id: str
    report_type: ReportType
    market_scope: Market
    
    # Timing
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    
    # Content Columns
    # We store structured IDs/Summaries here
    included_narrative_ids: List[str]
    narrative_summaries: List[Dict[str, Any]] # [{"id": "...", "headline": "...", "confidence": 80}]
    
    signal_stats: Dict[str, Any] # {"active_count": 10, "avg_confidence": 65}
    
    confidence_overview: str # "Moderate Confidence due to High Volatility" (Generated)
    
    version: int
    explainability_payload: Dict[str, Any] # Traceability back to inputs
    
    @classmethod
    def create(cls, 
               rtype: ReportType, 
               market: Market, 
               start: datetime, 
               end: datetime, 
               narratives: List[Dict],
               stats: Dict,
               conf_text: str,
               explanation: Dict) -> 'ResearchReport':
        
        return cls(
            report_id=str(uuid.uuid4()),
            report_type=rtype,
            market_scope=market,
            period_start=start,
            period_end=end,
            generated_at=datetime.utcnow(),
            included_narrative_ids=[n['id'] for n in narratives],
            narrative_summaries=narratives,
            signal_stats=stats,
            confidence_overview=conf_text,
            version=1,
            explainability_payload=explanation
        )

    def to_dict(self):
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        d['report_type'] = self.report_type.value
        d['market_scope'] = self.market_scope.value
        return d
    
    @staticmethod
    def from_dict(d: Dict) -> 'ResearchReport':
        d['report_type'] = ReportType(d['report_type'])
        d['market_scope'] = Market(d['market_scope'])
        for k in ['period_start', 'period_end', 'generated_at']:
            if d.get(k):
                d[k] = datetime.fromisoformat(d[k])
        return ResearchReport(**d)
