from abc import ABC, abstractmethod
from typing import List, Optional
from presentation.core.models import NarrativeSummary

class SummaryRepository(ABC):
    @abstractmethod
    def save_summary(self, summary: NarrativeSummary) -> None:
        pass
    
    @abstractmethod
    def get_summary_by_narrative(self, narrative_id: str) -> Optional[NarrativeSummary]:
        pass
