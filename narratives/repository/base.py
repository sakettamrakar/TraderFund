from abc import ABC, abstractmethod
from typing import List, Optional
from narratives.core.models import Narrative
from signals.core.enums import Market

class NarrativeRepository(ABC):
    @abstractmethod
    def save_narrative(self, narrative: Narrative) -> None:
        pass
    
    @abstractmethod
    def get_narrative_history(self, narrative_id: str) -> List[Narrative]:
        pass

    @abstractmethod
    def get_active_narratives(self, market: Market) -> List[Narrative]:
        pass
