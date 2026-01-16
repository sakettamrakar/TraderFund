
from typing import Optional
from traderfund.regime.types import (
    MarketBehavior, DirectionalBias, RegimeState, ConfidenceComponents,
    RegimeOutput, RegimeFactors
)
from traderfund.regime.calculator import RawRegime

class StateManager:
    """
    Maintains the state of the market regime over time.
    Adds hysteresis, cooldowns, and confidence scoring.
    """
    def __init__(
        self,
        hysteresis_risk_on: int = 5,
        hysteresis_risk_off: int = 1,
        hysteresis_default: int = 3,
        cooldown_bars: int = 30
    ):
        self.hysteresis_risk_on = hysteresis_risk_on
        self.hysteresis_risk_off = hysteresis_risk_off
        self.hysteresis_default = hysteresis_default
        self.cooldown_bars = cooldown_bars

        # State Variables
        self.current_behavior: MarketBehavior = MarketBehavior.UNDEFINED
        self.current_bias: DirectionalBias = DirectionalBias.NEUTRAL
        
        self.pending_behavior: Optional[MarketBehavior] = None
        self.pending_counter: int = 0
        
        self.persistence_counter: int = 0
        self.cooldown_timer: int = 0
        
        # Initial confidence state
        self.confluence: float = 0.5
        self.intensity: float = 0.5

    def update(self, raw: RawRegime, factors: RegimeFactors) -> RegimeState:
        """
        Updates the internal state machine with a new tick/bar.
        """
        # 0. Cooldown Management
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            # Constraints during cooldown:
            # If Raw is Normal/Low vol, force Higher Risk or Undefined
            if raw.behavior in [MarketBehavior.TRENDING_NORMAL_VOL, MarketBehavior.MEAN_REVERTING_LOW_VOL]:
                 # Override to prevent premature entry
                 # We keep it as UNDEFINED or degrade to MEAN_REVERTING_HIGH_VOL if already there
                 # For simplicity, during cooldown, we treat as UNDEFINED (safest)
                 # or map to a riskier state if applicable.
                 # Let's override the RAW, then let hysteresis handle the rest? 
                 # No, overriding the raw input preserves the state logic below.
                 raw = RawRegime(
                     behavior=MarketBehavior.UNDEFINED,
                     bias=DirectionalBias.NEUTRAL,
                     event_state_description="COOLDOWN"
                 )
        
        # 1. Start Cooldown Trigger
        if raw.behavior == MarketBehavior.EVENT_LOCK:
             # If we return to Lock (or are in Lock), cancel cooldown
             self.cooldown_timer = 0
        elif self.current_behavior == MarketBehavior.EVENT_LOCK and raw.behavior != MarketBehavior.EVENT_LOCK:
             # Trigger only if not already running
             if self.cooldown_timer == 0:
                 self.cooldown_timer = self.cooldown_bars

        # 2. Hysteresis Logic
        required_confirmations = self._get_required_confirmations(raw.behavior)
        
        if raw.behavior == self.current_behavior:
            # Persistence
            self.persistence_counter += 1
            self.pending_behavior = None
            self.pending_counter = 0
            
            # Update Bias immediately if behavior matches (Bias is a secondary attribute)
            self.current_bias = raw.bias
        else:
            # Transition Candidate
            if raw.behavior == self.pending_behavior:
                self.pending_counter += 1
            else:
                self.pending_behavior = raw.behavior
                self.pending_counter = 1
            
            # Check Threshold
            if self.pending_counter >= required_confirmations:
                self._switch_state(raw.behavior, raw.bias)
        
        # 3. Confidence Calculation
        confidence = self._calculate_confidence(raw, factors)
        
        return RegimeState(
            behavior=self.current_behavior,
            bias=self.current_bias,
            id=1, # Todo: map behavior to ID
            confidence_components=confidence,
            total_confidence=(confidence.confluence_score * 0.4 + confidence.persistence_score * 0.4 + confidence.intensity_score * 0.2), # Simple weighted
            is_stable=(self.persistence_counter > 5)
        )

    def _switch_state(self, new_behavior: MarketBehavior, new_bias: DirectionalBias):
        self.current_behavior = new_behavior
        self.current_bias = new_bias
        self.persistence_counter = 0
        self.pending_behavior = None
        self.pending_counter = 0

    def _get_required_confirmations(self, candidate: MarketBehavior) -> int:
        if candidate in [MarketBehavior.EVENT_LOCK, MarketBehavior.TRENDING_HIGH_VOL, MarketBehavior.MEAN_REVERTING_HIGH_VOL, MarketBehavior.UNDEFINED]:
            return self.hysteresis_risk_off
        if candidate in [MarketBehavior.TRENDING_NORMAL_VOL]:
            return self.hysteresis_risk_on
        return self.hysteresis_default

    def _calculate_confidence(self, raw: RawRegime, factors: RegimeFactors) -> ConfidenceComponents:
        # 1. Persistence Score (0.0 - 1.0)
        # Cap at 50 bars for max confidence
        persistence_score = min(1.0, self.persistence_counter / 50.0)
        
        # 2. Intensity Score
        # Driven by strength of signals. 
        # Trend Strength (0-1) + Vol (Deviation from 1).
        intensity = factors.trend_strength_norm
        if factors.volatility_ratio > 1.0:
             # Add volatility contribution capped at 1.0
             intensity = max(intensity, min(1.0, (factors.volatility_ratio - 1.0) / 0.5))
        
        # 3. Confluence Score
        # Simple heuristic: If Current State matches Raw State, Confluence is high.
        # If pending switch, Confluence drops.
        confluence = 1.0 if raw.behavior == self.current_behavior else 0.5
        
        # Refine confluence: If Bias matches Trend Provider?
        # Passed in RawRegime, bias is from provider.
        
        return ConfidenceComponents(
            confluence_score=confluence,
            persistence_score=persistence_score,
            intensity_score=intensity
        )
