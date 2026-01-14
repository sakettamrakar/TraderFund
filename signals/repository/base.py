from abc import ABC, abstractmethod
from typing import List, Optional
from signals.core.models import Signal
from signals.core.enums import Market, SignalState

class SignalRepository(ABC):
    
    @abstractmethod
    def save_signal(self, signal: Signal) -> None:
        """Persist a signal object (new version)."""
        pass

    @abstractmethod
    def get_signal_history(self, signal_id: str) -> List[Signal]:
        """Retrieve all versions of a signal by ID."""
        pass
    
    @abstractmethod
    def get_latest_signal(self, signal_id: str) -> Optional[Signal]:
        """Retrieve the latest version of a signal."""
        pass

    @abstractmethod
    def get_active_signals(self, market: Market) -> List[Signal]:
        """Retrieve all signals currently in ACTIVE state for a market."""
        pass
