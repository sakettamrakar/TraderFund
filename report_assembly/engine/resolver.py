from typing import List
from datetime import datetime
from narratives.core.models import Narrative
from narratives.repository.base import NarrativeRepository
from signals.core.enums import Market
from report_assembly.config.settings import AssemblyConfig

class InputResolver:
    """
    Deterministically fetches, filters, and sorts narratives for reporting.
    """
    def __init__(self, repo: NarrativeRepository, config: AssemblyConfig):
        self.repo = repo
        self.config = config

    def resolve_narratives(self, market: Market, start_time: datetime, end_time: datetime) -> List[Narrative]:
        # 1. Fetch All Active
        # Ideally repo supports date filtering. For now we fetch active and filter in memory.
        candidates = self.repo.get_active_narratives(market)
        
        # 2. Filter Validity & Thresholds
        filtered = []
        for n in candidates:
            # Filter by update time intersection with window
            # If Updated within [start, end]
            # Assumes created_at/updated_at are timezone naive UTC as per models
            in_window = n.updated_at >= start_time and n.updated_at <= end_time
            # Also include if created in window
            in_window = in_window or (n.created_at >= start_time and n.created_at <= end_time)
            
            # Simple fallback: if active, permit it? No, Report is time-bound.
            # Strict window check.
            if not in_window:
                continue
                
            if n.confidence_score < self.config.MIN_NARRATIVE_CONFIDENCE:
                continue
                
            filtered.append(n)
            
        # 3. Deterministic Sort
        # Score = (Conf * W_Conf) + (Recency_Score)
        # Recency Score: Seconds since start / Window Len?
        # Let's keep it simple: Sort by Confidence Descending, then Recency Descending, then ID Ascending (Tie-break)
        
        def sort_key(n: Narrative):
            return (
                -n.confidence_score, # Desc
                -n.updated_at.timestamp(), # Desc
                n.narrative_id # Asc (Tie break)
            )
            
        filtered.sort(key=sort_key)
        
        # 4. Limit
        limit = self.config.MAX_NARRATIVES_DAILY # Defaulting to daily limit logic for now
        return filtered[:limit]
