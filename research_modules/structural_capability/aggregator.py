"""
Stage 1: Structural Capability - Aggregator

Aggregates evidence into behavior scores and final capability score.
"""

import logging
from typing import Dict, List, Optional, Callable
import pandas as pd

from . import config
from .models import BehaviorScore, StructuralCapability
from . import evidence as ev

logger = logging.getLogger(__name__)


# =============================================================================
# BEHAVIOR DEFINITIONS
# =============================================================================
# Maps behavior name to list of (evidence_id, calculation_function)

BEHAVIOR_EVIDENCE = {
    "long_term_bias": [
        ("lt_trend_slope", ev.calculate_lt_trend_slope),
        ("lt_position", ev.calculate_lt_position),
        ("lt_stability", ev.calculate_lt_stability),
    ],
    "medium_term_alignment": [
        ("mt_trend_slope", ev.calculate_mt_trend_slope),
        ("mt_lt_coherence", ev.calculate_mt_lt_coherence),
        ("mt_channel_quality", ev.calculate_mt_channel_quality),
    ],
    "institutional_acceptance": [
        ("vwap_position", ev.calculate_vwap_position),
        ("volume_trend", ev.calculate_volume_trend),
        ("wick_ratio", ev.calculate_wick_ratio),
    ],
    "volatility_suitability": [
        ("atr_percentile", ev.calculate_atr_percentile),
        ("range_stability", ev.calculate_range_stability),
        ("gap_frequency", ev.calculate_gap_frequency),
    ],
}


class StructuralAggregator:
    """
    Aggregates evidence into behavior scores and structural capability.
    
    BEHAVIOR-first design:
    - Each behavior has multiple optional evidence sources
    - Missing evidence is skipped, not penalized
    - Minimum 1 evidence per behavior required for scoring
    """
    
    def __init__(self):
        self.behavior_weights = config.BEHAVIOR_WEIGHTS
        self.evidence_weights = config.EVIDENCE_WEIGHTS
    
    def evaluate_behavior(
        self,
        behavior_name: str,
        df: pd.DataFrame,
    ) -> BehaviorScore:
        """
        Evaluate a single behavior using available evidence.
        
        Args:
            behavior_name: Name of the behavior to evaluate.
            df: Price DataFrame with OHLCV data.
            
        Returns:
            BehaviorScore with aggregated score and evidence details.
        """
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
        
        # Calculate behavior score (0-100)
        if total_weight > 0:
            score = (weighted_sum / total_weight) * 100
        else:
            score = 0.0
        
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
    ) -> StructuralCapability:
        """
        Evaluate structural capability for a single symbol.
        
        Args:
            symbol: Ticker symbol.
            df: Price DataFrame with OHLCV data.
            
        Returns:
            StructuralCapability object with full evaluation.
        """
        behavior_scores = []
        known_limitations = []
        
        # Check data availability
        available_days = len(df)
        lt_required = config.LOOKBACK["long_term"]
        
        if available_days < lt_required:
            known_limitations.append(
                f"Only {available_days} days available (ideal: {lt_required})"
            )
        
        # Evaluate each behavior
        for behavior_name in BEHAVIOR_EVIDENCE.keys():
            bs = self.evaluate_behavior(behavior_name, df)
            behavior_scores.append(bs)
            
            if bs.evidence_missing:
                known_limitations.append(
                    f"{behavior_name}: missing {len(bs.evidence_missing)} evidence sources"
                )
        
        # Create final capability object
        return StructuralCapability.create(
            symbol=symbol,
            behavior_scores=behavior_scores,
            weights=self.behavior_weights,
            known_limitations=known_limitations,
            version=config.VERSION,
        )
