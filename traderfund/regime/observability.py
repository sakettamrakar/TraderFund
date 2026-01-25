
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from traderfund.regime.types import (
    RegimeState, RegimeFactors, MarketBehavior, DirectionalBias
)
from traderfund.regime.gate import StrategyCompatibilityMap, StrategyClass, GateAction

class RegimeFormatter:
    """
    Stateless formatter for Regime Engine outputs.
    Provides canonical JSON and human-readable Strings.
    """
    
    @staticmethod
    def to_dict(
        regime: RegimeState, 
        factors: Optional[RegimeFactors] = None,
        symbol: str = "UNKNOWN",
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Produce Canonical JSON-serializable Dictionary.
        Ref: Tech Spec v1.1.0 Section 2.2
        """
        ts = timestamp or datetime.utcnow()
        
        # Calculate blocked/throttled strategies dynamically based on current behavior
        blocked = []
        throttled = []
        allowed = []
        
        if regime.behavior == MarketBehavior.EVENT_LOCK or regime.behavior == MarketBehavior.UNDEFINED:
            # All blocked except maybe safety (not defined yet)
            blocked = [s.value for s in StrategyClass]
        else:
            for strat in StrategyClass:
                action = StrategyCompatibilityMap.get_action(strat, regime.behavior)
                if action == GateAction.BLOCK:
                    blocked.append(strat.value)
                elif action == GateAction.REDUCE:
                    throttled.append(strat.value)
                else:
                    allowed.append(strat.value)

        return {
            "meta": {
                "symbol": symbol,
                "timestamp": ts.isoformat(),
                "version": "1.1.0"
            },
            "regime": {
                "behavior": regime.behavior.value,
                "bias": regime.bias.value,
                "id": regime.id,
                "is_stable": regime.is_stable,
                "total_confidence": round(regime.total_confidence, 2),
                "confidence_detail": {
                    "confluence": round(regime.confidence_components.confluence_score, 2),
                    "persistence": round(regime.confidence_components.persistence_score, 2),
                    "intensity": round(regime.confidence_components.intensity_score, 2)
                }
            },
            "factors": {
                "trend": round(factors.trend_strength_norm, 2) if factors else None,
                "vol_ratio": round(factors.volatility_ratio, 2) if factors else None,
                "liquidity": factors.liquidity_status if factors else None,
                "event": round(factors.event_pressure_norm, 2) if factors else None
            },
            "constraints": {
                "blocked_strategies": blocked,
                "throttled_strategies": throttled,
                "allowed_strategies": allowed
            }
        }

    @staticmethod
    def to_json(
        regime: RegimeState, 
        factors: Optional[RegimeFactors] = None,
        symbol: str = "UNKNOWN"
    ) -> str:
        data = RegimeFormatter.to_dict(regime, factors, symbol)
        return json.dumps(data, indent=2)

    @staticmethod
    def to_cli_string(regime: RegimeState) -> str:
        """
        Returns a single-line summary string for logs/CLI.
        Format: [REGIME] BEHAVIOR | Bias=BIAS | Conf=0.XX | Stable=T/F
        """
        risk_marker = "(!)" if regime.behavior in [MarketBehavior.EVENT_LOCK, MarketBehavior.UNDEFINED] else ""
        
        return (
            f"[REGIME] {regime.behavior.value:<22} {risk_marker}| "
            f"Bias={regime.bias.value:<7} | "
            f"Conf={regime.total_confidence:.2f} | "
            f"Stable={str(regime.is_stable)[0]}"
        )

class RegimeLogger:
    """
    Wrapper around Python logging to enforce standard format.
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_update(self, regime: RegimeState, symbol: str):
        """
        Logs update at appropriate level.
        """
        msg = RegimeFormatter.to_cli_string(regime)
        
        if regime.behavior in [MarketBehavior.EVENT_LOCK, MarketBehavior.UNDEFINED, MarketBehavior.TRENDING_HIGH_VOL]:
            self.logger.warning(f"[{symbol}] {msg}")
        else:
            self.logger.info(f"[{symbol}] {msg}")
