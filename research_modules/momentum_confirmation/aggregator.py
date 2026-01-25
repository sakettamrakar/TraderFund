"""Stage 4: Momentum Confirmation - Aggregator"""
import logging
from typing import Dict, List, Optional
import pandas as pd
from . import config
from .models import BehaviorScore, MomentumConfirmation
from . import evidence as ev

logger = logging.getLogger(__name__)

BEHAVIOR_EVIDENCE = {
    "directional_persistence": [
        ("consecutive_closes", ev.calculate_consecutive_closes),
        ("net_movement", ev.calculate_net_movement),
        ("counter_reduction", ev.calculate_counter_reduction),
    ],
    "follow_through": [
        ("gain_holding", ev.calculate_gain_holding),
        ("pullback_depth", ev.calculate_pullback_depth),
        ("level_acceptance", ev.calculate_level_acceptance),
    ],
    "relative_strength": [
        ("vol_adjusted_return", ev.calculate_vol_adjusted_return),
        ("recent_outperformance", ev.calculate_recent_outperformance),
        ("persistence_ratio", ev.calculate_persistence_ratio),
    ],
    "momentum_stability": [
        ("smooth_progression", ev.calculate_smooth_progression),
        ("controlled_volatility", ev.calculate_controlled_volatility),
        ("reversal_absence", ev.calculate_reversal_absence),
    ],
}

class MomentumAggregator:
    def __init__(self):
        self.behavior_weights = config.BEHAVIOR_WEIGHTS
        self.evidence_weights = config.EVIDENCE_WEIGHTS
    
    def evaluate_behavior(self, behavior_name: str, df: pd.DataFrame) -> BehaviorScore:
        evidence_specs = BEHAVIOR_EVIDENCE.get(behavior_name, [])
        evidence_used, evidence_missing = {}, []
        weighted_sum, total_weight = 0.0, 0.0
        
        for eid, func in evidence_specs:
            try:
                val = func(df)
                if val is not None:
                    w = self.evidence_weights.get(eid, 1.0)
                    evidence_used[eid] = val
                    weighted_sum += val * w
                    total_weight += w
                else:
                    evidence_missing.append(eid)
            except Exception as e:
                logger.warning(f"Error {eid}: {e}")
                evidence_missing.append(eid)
        
        score = (weighted_sum / total_weight) * 100 if total_weight > 0 else 0.0
        return BehaviorScore(name=behavior_name, score=round(score, 2),
                            evidence_used=evidence_used, evidence_missing=evidence_missing)
    
    def evaluate_symbol(self, symbol: str, df: pd.DataFrame, 
                       participation_score: Optional[float] = None) -> MomentumConfirmation:
        behavior_scores = [self.evaluate_behavior(b, df) for b in BEHAVIOR_EVIDENCE.keys()]
        limitations = []
        if len(df) < config.LOOKBACK["long"]:
            limitations.append(f"Only {len(df)} days available")
        return MomentumConfirmation.create(symbol, behavior_scores, self.behavior_weights,
                                           participation_score, limitations, config.VERSION)
