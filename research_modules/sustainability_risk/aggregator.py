"""Stage 5: Sustainability & Risk - Aggregator"""
import logging
from typing import Dict, List, Optional
import pandas as pd
from . import config
from .models import BehaviorScore, SustainabilityRisk
from . import evidence as ev

logger = logging.getLogger(__name__)

BEHAVIOR_EVIDENCE = {
    "extension_risk": [
        ("distance_from_base", ev.calculate_distance_from_base),
        ("mean_deviation", ev.calculate_mean_deviation),
        ("speed_of_move", ev.calculate_speed_of_move),
    ],
    "participation_quality": [
        ("volume_consistency", ev.calculate_volume_consistency),
        ("pullback_support", ev.calculate_pullback_support),
        ("distribution_pattern", ev.calculate_distribution_pattern),
    ],
    "volatility_compatibility": [
        ("volatility_spike", ev.calculate_volatility_spike),
        ("range_instability", ev.calculate_range_instability),
        ("chaos_score", ev.calculate_chaos_score),
    ],
    "momentum_decay": [
        ("follow_through_decay", ev.calculate_follow_through_decay),
        ("persistence_decline", ev.calculate_persistence_decline),
        ("progress_stall", ev.calculate_progress_stall),
    ],
}

class SustainabilityAggregator:
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
                       momentum_score: Optional[float] = None) -> SustainabilityRisk:
        behavior_scores = [self.evaluate_behavior(b, df) for b in BEHAVIOR_EVIDENCE.keys()]
        limitations = []
        if len(df) < config.LOOKBACK["long"]:
            limitations.append(f"Only {len(df)} days available")
        return SustainabilityRisk.create(symbol, behavior_scores, self.behavior_weights,
                                         momentum_score, limitations, config.VERSION)
