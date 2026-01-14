"""
Stage 2: Energy Setup - Aggregator

Aggregates evidence into behavior scores and energy setup score.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd

from . import config
from .models import BehaviorScore, EnergySetup
from . import evidence as ev

logger = logging.getLogger(__name__)


BEHAVIOR_EVIDENCE = {
    "volatility_compression": [
        ("atr_compression", ev.calculate_atr_compression),
        ("range_squeeze", ev.calculate_range_squeeze),
        ("return_tightness", ev.calculate_return_tightness),
    ],
    "range_balance": [
        ("range_containment", ev.calculate_range_containment),
        ("rejection_symmetry", ev.calculate_rejection_symmetry),
        ("trend_neutrality", ev.calculate_trend_neutrality),
    ],
    "mean_adherence": [
        ("mean_deviation", ev.calculate_mean_deviation),
        ("reversion_speed", ev.calculate_reversion_speed),
        ("wick_containment", ev.calculate_wick_containment),
    ],
    "energy_duration": [
        ("compression_days", ev.calculate_compression_days),
        ("setup_stability", ev.calculate_setup_stability),
        ("expansion_failures", ev.calculate_expansion_failures),
    ],
}


class EnergyAggregator:
    """Aggregates evidence into energy setup scores."""
    
    def __init__(self):
        self.behavior_weights = config.BEHAVIOR_WEIGHTS
        self.evidence_weights = config.EVIDENCE_WEIGHTS
    
    def evaluate_behavior(self, behavior_name: str, df: pd.DataFrame) -> BehaviorScore:
        evidence_specs = BEHAVIOR_EVIDENCE.get(behavior_name, [])
        
        evidence_used = {}
        evidence_missing = []
        weighted_sum = 0.0
        total_weight = 0.0
        
        for evidence_id, calc_func in evidence_specs:
            try:
                value = calc_func(df)
                if value is not None:
                    weight = self.evidence_weights.get(evidence_id, 1.0)
                    evidence_used[evidence_id] = value
                    weighted_sum += value * weight
                    total_weight += weight
                else:
                    evidence_missing.append(evidence_id)
            except Exception as e:
                logger.warning(f"Error calculating {evidence_id}: {e}")
                evidence_missing.append(evidence_id)
        
        score = (weighted_sum / total_weight) * 100 if total_weight > 0 else 0.0
        
        return BehaviorScore(
            name=behavior_name,
            score=round(score, 2),
            evidence_used=evidence_used,
            evidence_missing=evidence_missing,
        )
    
    def evaluate_symbol(
        self,
        symbol: str,
        df: pd.DataFrame,
        structural_score: Optional[float] = None,
    ) -> EnergySetup:
        behavior_scores = []
        known_limitations = []
        
        available_days = len(df)
        if available_days < config.LOOKBACK["long"]:
            known_limitations.append(f"Only {available_days} days (ideal: {config.LOOKBACK['long']})")
        
        for behavior_name in BEHAVIOR_EVIDENCE.keys():
            bs = self.evaluate_behavior(behavior_name, df)
            behavior_scores.append(bs)
            
            if bs.evidence_missing:
                known_limitations.append(f"{behavior_name}: missing {len(bs.evidence_missing)} evidence")
        
        return EnergySetup.create(
            symbol=symbol,
            behavior_scores=behavior_scores,
            weights=self.behavior_weights,
            structural_score=structural_score,
            known_limitations=known_limitations,
            version=config.VERSION,
        )
