from abc import ABC, abstractmethod
from typing import List
from signals.core.models import Signal
from alpha_discovery.core.models import AlphaHypothesis

class AlphaPatternDetector(ABC):
    @abstractmethod
    def detect(self, signals: List[Signal]) -> List[AlphaHypothesis]:
        """
        Analyzes a list of signals to find patterns.
        Returns proposed Alpha Hypotheses.
        """
        pass
