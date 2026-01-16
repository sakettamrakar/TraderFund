
from typing import Dict, Optional, Literal
from pydantic import BaseModel
from enum import Enum

from traderfund.regime.types import MarketBehavior, RegimeState

class StrategyClass(str, Enum):
    MOMENTUM = "MOMENTUM"
    MEAN_REVERSION = "MEAN_REVERSION"
    SCALPING = "SCALPING"
    EVENT = "EVENT"

class GateAction(str, Enum):
    ALLOW = "ALLOW"
    REDUCE = "REDUCE"
    BLOCK = "BLOCK"

class GateDecision(BaseModel):
    is_allowed: bool
    size_multiplier: float
    reason: str

class StrategyCompatibilityMap:
    """
    Declarative mapping of Strategies to Regime Behaviors.
    """
    _DEFAULT_MAPPING = {
        StrategyClass.MOMENTUM: {
             MarketBehavior.TRENDING_NORMAL_VOL: GateAction.ALLOW,
             MarketBehavior.TRENDING_HIGH_VOL: GateAction.REDUCE,
             MarketBehavior.MEAN_REVERTING_LOW_VOL: GateAction.BLOCK,
             MarketBehavior.MEAN_REVERTING_HIGH_VOL: GateAction.BLOCK,
             MarketBehavior.EVENT_DOMINANT: GateAction.BLOCK,
        },
        StrategyClass.MEAN_REVERSION: {
             MarketBehavior.TRENDING_NORMAL_VOL: GateAction.BLOCK,
             MarketBehavior.TRENDING_HIGH_VOL: GateAction.BLOCK,
             MarketBehavior.MEAN_REVERTING_LOW_VOL: GateAction.ALLOW,
             MarketBehavior.MEAN_REVERTING_HIGH_VOL: GateAction.REDUCE,
             MarketBehavior.EVENT_DOMINANT: GateAction.BLOCK,
        },
        StrategyClass.SCALPING: {
             # Scalping thrives in Volatility
             MarketBehavior.TRENDING_NORMAL_VOL: GateAction.ALLOW,
             MarketBehavior.TRENDING_HIGH_VOL: GateAction.ALLOW,
             MarketBehavior.MEAN_REVERTING_LOW_VOL: GateAction.ALLOW,
             MarketBehavior.MEAN_REVERTING_HIGH_VOL: GateAction.ALLOW,
             MarketBehavior.EVENT_DOMINANT: GateAction.REDUCE,
        },
        StrategyClass.EVENT: {
             MarketBehavior.EVENT_DOMINANT: GateAction.ALLOW,
             # Block EVENT strategies in normal markets? Usually yes for purity.
             MarketBehavior.TRENDING_NORMAL_VOL: GateAction.BLOCK,
             MarketBehavior.TRENDING_HIGH_VOL: GateAction.BLOCK,
             MarketBehavior.MEAN_REVERTING_LOW_VOL: GateAction.BLOCK,
             MarketBehavior.MEAN_REVERTING_HIGH_VOL: GateAction.BLOCK,
        }
    }

    @classmethod
    def get_action(cls, strategy: StrategyClass, behavior: MarketBehavior) -> GateAction:
        """
        Returns the configured action for (Strategy, Behavior).
        Defaults to BLOCK if undefined (Whitelist approach).
        """
        # Global Blocking Conditions are checked in the Gate, but here we can return BLOCK.
        # If behavior is UNDEFINED or LOCK, we rely on map not having it, defaulting to BLOCK?
        # Or explicit maps. 
        # Better: Let the map return explicit action if found, else BLOCK.
        
        strat_map = cls._DEFAULT_MAPPING.get(strategy, {})
        return strat_map.get(behavior, GateAction.BLOCK)

class StrategyGate:
    """
    Gatekeeper that enforces Regime constraints on Strategies.
    """
    
    def evaluate(self, regime: RegimeState, strategy_class: StrategyClass) -> GateDecision:
        """
        Determines if a strategy is allowed to operate in the current regime.
        """
        behavior = regime.behavior
        
        # 1. Global Kill Switches
        if behavior == MarketBehavior.EVENT_LOCK:
            return GateDecision(
                is_allowed=False,
                size_multiplier=0.0,
                reason="BLOCKED: Market is in EVENT_LOCK."
            )
            
        if behavior == MarketBehavior.UNDEFINED:
            # Block everything unless we had a specific "SafetyStrategy".
            return GateDecision(
                is_allowed=False,
                size_multiplier=0.0,
                reason="BLOCKED: Market Regime UNDEFINED (Risk Off)."
            )
            
        # 2. Check Compatibility Map
        action = StrategyCompatibilityMap.get_action(strategy_class, behavior)
        
        if action == GateAction.ALLOW:
            return GateDecision(
                is_allowed=True,
                size_multiplier=1.0,
                reason=f"ALLOWED: {strategy_class} compatible with {behavior}."
            )
            
        elif action == GateAction.REDUCE:
            return GateDecision(
                is_allowed=True,
                size_multiplier=0.5, # Configurable in future
                reason=f"REDUCED: {strategy_class} risk reduced in {behavior}."
            )
            
        else: # BLOCK
            return GateDecision(
                is_allowed=False, 
                size_multiplier=0.0,
                reason=f"BLOCKED: {strategy_class} incompatible with {behavior}."
            )
