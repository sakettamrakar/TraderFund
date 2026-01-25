from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, conlist

class MarketBehavior(str, Enum):
    """
    Core Behavioral States of the Market.
    Ref: Blueprint v1.1.0 Section 5
    """
    TRENDING_NORMAL_VOL = "TRENDING_NORMAL_VOL"
    TRENDING_HIGH_VOL = "TRENDING_HIGH_VOL"
    MEAN_REVERTING_LOW_VOL = "MEAN_REVERTING_LOW_VOL"
    MEAN_REVERTING_HIGH_VOL = "MEAN_REVERTING_HIGH_VOL"
    EVENT_DOMINANT = "EVENT_DOMINANT"
    EVENT_LOCK = "EVENT_LOCK"
    UNDEFINED = "UNDEFINED"

class DirectionalBias(str, Enum):
    """
    Directional overlay for the behavioral state.
    """
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class ConfidenceComponents(BaseModel):
    """
    Breakdown of the confidence score.
    """
    confluence_score: float = Field(..., ge=0.0, le=1.0, description="Agreement between indicators")
    persistence_score: float = Field(..., ge=0.0, le=1.0, description="Stability over time")
    intensity_score: float = Field(..., ge=0.0, le=1.0, description="Magnitude of signal")

class RegimeLevel(str, Enum):
    MARKET = "MARKET"
    SECTOR = "SECTOR"
    STOCK = "STOCK"

class RegimeScope(BaseModel):
    market: str = "IND"
    symbol: str
    level: RegimeLevel

class RegimeState(BaseModel):
    """
    Canonical Regime State. Ref: Tech Spec v1.1.0 Section 2.2 (inner 'regime' object)
    """
    behavior: MarketBehavior
    bias: DirectionalBias
    id: int
    confidence_components: ConfidenceComponents
    total_confidence: float = Field(..., ge=0.0, le=1.0)
    is_stable: bool

class RegimeFactors(BaseModel):
    """
    Normalized factors driving the regime decision.
    """
    trend_strength_norm: float
    volatility_ratio: float
    liquidity_status: str
    event_pressure_norm: float

class RegimeOutput(BaseModel):
    """
    Full payload for downstream consumers. Matches 'RegimePayload' concept.
    """
    meta: Dict[str, str]
    scope: Optional[RegimeScope] = None
    regime: RegimeState
    factors: RegimeFactors
    flags: Dict[str, object]
    timestamp: str  # ISO 8601
