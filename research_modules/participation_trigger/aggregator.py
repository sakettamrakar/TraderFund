"""Stage 3: Participation Trigger - Aggregator"""
import logging
from typing import Dict, List, Optional
import pandas as pd
from . import config
from .models import BehaviorScore, ParticipationTrigger
from . import evidence as ev

logger = logging.getLogger(__name__)

BEHAVIOR_EVIDENCE = {
    "volume_expansion": [
        ("relative_volume", ev.calculate_relative_volume),
        ("volume_streak", ev.calculate_volume_streak),
        ("volume_spike", ev.calculate_volume_spike),
    ],
    "range_expansion": [
        ("range_ratio", ev.calculate_range_ratio),
        ("body_expansion", ev.calculate_body_expansion),
        ("range_breakout", ev.calculate_range_breakout),
    ],
    "directional_commitment": [
        ("close_location", ev.calculate_close_location),
        ("direction_bias", ev.calculate_direction_bias),
        ("gap_follow", ev.calculate_gap_follow),
    ],
    "participation_continuity": [
        ("multi_day_expansion", ev.calculate_multi_day_expansion),
        ("fade_resistance", ev.calculate_fade_resistance),
        ("overlap_reduction", ev.calculate_overlap_reduction),
    ],
}

class ParticipationAggregator:
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
                       energy_score: Optional[float] = None) -> ParticipationTrigger:
        behavior_scores = [self.evaluate_behavior(b, df) for b in BEHAVIOR_EVIDENCE.keys()]
        limitations = []
        if len(df) < config.LOOKBACK["medium"]:
            limitations.append(f"Only {len(df)} days available")
        return ParticipationTrigger.create(symbol, behavior_scores, self.behavior_weights,
                                          energy_score, limitations, config.VERSION)
