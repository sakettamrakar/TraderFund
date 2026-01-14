from abc import ABC, abstractmethod
from typing import List, Optional
from alpha_discovery.core.models import AlphaHypothesis

class AlphaRepository(ABC):
    @abstractmethod
    def save_alpha(self, alpha: AlphaHypothesis) -> None:
        pass

    @abstractmethod
    def get_alpha_history(self, alpha_id: str) -> List[AlphaHypothesis]:
        pass

    @abstractmethod
    def get_active_alphas(self) -> List[AlphaHypothesis]:
        pass
