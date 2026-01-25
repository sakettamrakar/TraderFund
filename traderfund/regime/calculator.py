
from typing import NamedTuple, Optional
from pydantic import BaseModel

from traderfund.regime.types import MarketBehavior, DirectionalBias

class RawRegime(NamedTuple):
    behavior: MarketBehavior
    bias: DirectionalBias
    event_state_description: str  # For debugging/logging

class RegimeCalculator:
    """
    Pure stateless component that maps Provider outputs to a RawRegime.
    Implements the Decision Tree defined in Blueprint v1.1.0 and Tech Spec v1.1.0.
    """

    def __init__(
        self,
        trend_threshold: float = 0.25,
        high_vol_ratio: float = 1.5,
        liquidity_min: float = 0.2,
        event_pressure_dominant: float = 0.8,
    ):
        self.trend_threshold = trend_threshold
        self.high_vol_ratio = high_vol_ratio
        self.liquidity_min = liquidity_min
        self.event_pressure_dominant = event_pressure_dominant

    def calculate(
        self,
        trend_strength: float,
        trend_bias: DirectionalBias,
        volatility_ratio: float,
        liquidity_score: float,
        event_pressure: float,
        is_event_locked: bool
    ) -> RawRegime:
        """
        Evaluates inputs deterministically to produce a Regime State.
        Order of Precedence:
        1. Event Lock -> EVENT_LOCK
        2. Liquidity Dry -> UNDEFINED (Risk Off)
        3. Event Dominant -> EVENT_DOMINANT
        4. Behavior Classification (Trend vs Mean Rev, Volatility)
        """

        # 1. Event Lock
        if is_event_locked:
            return RawRegime(
                behavior=MarketBehavior.EVENT_LOCK,
                bias=DirectionalBias.NEUTRAL,
                event_state_description="LOCKED"
            )

        # 2. Liquidity Check
        if liquidity_score < self.liquidity_min:
            return RawRegime(
                behavior=MarketBehavior.UNDEFINED,
                bias=DirectionalBias.NEUTRAL,
                event_state_description="LIQUIDITY_DRY"
            )

        # 3. Event Dominance
        if event_pressure >= self.event_pressure_dominant:
            # Event dominant but not locked. Bias might still differ from PROVIDER hint if event is specific,
            # but usually we keep the technical bias or set to Neutral. 
            # Blueprint: "Allow: News-Based... Block: Pure Technicals".
            # We'll allow the Bias to flow through if strong, else Neutral.
            # For simplicity in Phase 2, pass through the provider bias (or Neutral if weak).
            return RawRegime(
                behavior=MarketBehavior.EVENT_DOMINANT,
                bias=trend_bias, 
                event_state_description="DOMINANT"
            )

        # 4. Technical Classification
        is_trending = trend_strength >= self.trend_threshold
        is_high_vol = volatility_ratio >= self.high_vol_ratio

        behavior = MarketBehavior.UNDEFINED

        if is_trending:
            if is_high_vol:
                behavior = MarketBehavior.TRENDING_HIGH_VOL
            else:
                behavior = MarketBehavior.TRENDING_NORMAL_VOL
        else:
            # Mean Reverting
            if is_high_vol:
                behavior = MarketBehavior.MEAN_REVERTING_HIGH_VOL
            else:
                behavior = MarketBehavior.MEAN_REVERTING_LOW_VOL

        return RawRegime(
            behavior=behavior,
            bias=trend_bias,
            event_state_description="NONE"
        )
