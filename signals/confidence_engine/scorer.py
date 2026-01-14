from typing import Tuple, Dict, Any
from signals.core.models import Signal
from signals.core.enums import SignalDirection
from .inputs import ConfidenceContext

class ConfidenceScorer:
    """
    Deterministic Confidence Scoring Engine.
    """
    
    BASE_SCORE = 50.0
    
    # Weights / Adjustments
    BONUS_VOLUME_HIGH = 10.0      # Ratio > 1.2
    BONUS_VOLUME_EXTREME = 20.0   # Ratio > 2.0
    
    PENALTY_VOLATILITY_HIGH = -20.0 # Z > 2.0
    PENALTY_VOLATILITY_EXTREME = -40.0 # Z > 4.0
    
    BONUS_PER_AGREEMENT = 10.0   # Cap at 30
    MAX_AGREEMENT_BONUS = 30.0
    
    BONUS_REGIME_ALIGNMENT = 15.0 # Direction matches Trend
    PENALTY_REGIME_CONFLICT = -25.0 # Direction opposes Trend

    def compute_score(self, signal: Signal, context: ConfidenceContext) -> Tuple[float, Dict[str, Any]]:
        """
        Computes score (0-100) and returns explanation payload.
        """
        score = self.BASE_SCORE
        breakdown = {"base": self.BASE_SCORE}
        
        # 1. Volume Logic
        vol_score = 0.0
        if context.volume_ratio > 2.0:
            vol_score = self.BONUS_VOLUME_EXTREME
        elif context.volume_ratio > 1.2:
            vol_score = self.BONUS_VOLUME_HIGH
        
        score += vol_score
        if vol_score != 0:
            breakdown["volume_adjustment"] = vol_score

        # 2. Volatility Logic
        vola_score = 0.0
        if context.volatility_z_score > 4.0:
            vola_score = self.PENALTY_VOLATILITY_EXTREME
        elif context.volatility_z_score > 2.0:
            vola_score = self.PENALTY_VOLATILITY_HIGH
            
        score += vola_score
        if vola_score != 0:
            breakdown["volatility_adjustment"] = vola_score

        # 3. Agreement Logic
        agree_score = min(context.indicator_agreement_count * self.BONUS_PER_AGREEMENT, self.MAX_AGREEMENT_BONUS)
        score += agree_score
        if agree_score != 0:
            breakdown["agreement_adjustment"] = agree_score

        # 4. Regime Logic
        regime_score = 0.0
        trend = context.market_trend_score # -1 to 1
        
        is_bullish = signal.direction == SignalDirection.BULLISH
        is_bearish = signal.direction == SignalDirection.BEARISH
        
        if is_bullish:
            if trend > 0.2: # Bull Trend
                regime_score = self.BONUS_REGIME_ALIGNMENT
            elif trend < -0.2: # Bear Trend
                regime_score = self.PENALTY_REGIME_CONFLICT
        elif is_bearish:
            if trend < -0.2: # Bear Trend
                regime_score = self.BONUS_REGIME_ALIGNMENT
            elif trend > 0.2: # Bull Trend
                regime_score = self.PENALTY_REGIME_CONFLICT
                
        score += regime_score
        if regime_score != 0:
            breakdown["regime_adjustment"] = regime_score

        # Clamping
        final_score = max(0.0, min(100.0, score))
        
        breakdown["final_score"] = final_score
        breakdown["context_used"] = context.to_dict()
        
        return final_score, breakdown
