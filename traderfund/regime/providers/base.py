from abc import ABC, abstractmethod
from typing import Any, Dict
from enum import Enum
from traderfund.regime.types import DirectionalBias

class ITrendStrengthProvider(ABC):
    """
    Interface for providers that quantify trend intensity.
    Normalized Output: 0.0 (No Trend) to 1.0 (Max Trend).
    """
    @abstractmethod
    def get_trend_strength(self, data: Any) -> float:
        pass

class ITrendAlignmentProvider(ABC):
    """
    Interface for providers that determine directional structure.
    Output: DirectionalBias Enum.
    """
    @abstractmethod
    def get_alignment(self, data: Any) -> DirectionalBias:
        pass

class IVolatilityRatioProvider(ABC):
    """
    Interface for providers that compare current volatility vs baseline.
    Output: Ratio float (1.0 = Baseline).
    """
    @abstractmethod
    def get_volatility_ratio(self, data: Any) -> float:
        pass

class ILiquidityProvider(ABC):
    """
    Interface for providers that measure execution capability.
    Output: Normalized Score (0.0 = Dry/Risk, 1.0 = Liquid).
    """
    @abstractmethod
    def get_liquidity_score(self, data: Any) -> float:
        pass

class IEventPressureProvider(ABC):
    """
    Interface for providers measuring external shock potential.
    Output: 
        - pressure: 0.0 (Calm) to 1.0 (Imminent)
        - is_lock_window: bool (Hard No-Trade Zone)
    """
    @abstractmethod
    def get_pressure(self, data: Any) -> Dict[str, Any]:
        """
        Returns: {'pressure': float, 'is_lock_window': bool}
        """
        pass
