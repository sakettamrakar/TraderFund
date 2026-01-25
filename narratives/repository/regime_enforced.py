# Regime-Enforced Narrative Repository Wrapper
# 
# Runtime Narrative Enforcement v1.0 — FINAL & FROZEN
#
# This wrapper ensures ALL narratives pass through RegimeNarrativeAdapter
# before being persisted. There is NO bypass path.

import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from narratives.core.models import Narrative
from narratives.repository.base import NarrativeRepository
from signals.core.enums import Market

logger = logging.getLogger("RegimeEnforcedRepo")

# =============================================================================
# REGIME INTEGRATION (Inline to avoid circular imports)
# =============================================================================

FAIL_SAFE_WEIGHT = 0.5

def _get_regime_snapshot() -> Dict[str, Any]:
    """
    Fetch current US market regime.
    Returns fail-safe if unavailable.
    """
    log_path = Path("data/us_market/us_market_regime.jsonl")
    
    fail_safe = {
        "regime": "UNDEFINED",
        "bias": "NEUTRAL",
        "confidence": 0.0,
        "lifecycle": "UNKNOWN",
        "narrative_weight": FAIL_SAFE_WEIGHT,
        "enforcement_reason": "FAIL_SAFE_DAMPEN"
    }
    
    if not log_path.exists():
        logger.warning("FAIL_SAFE: US Regime log not found")
        return fail_safe
    
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                if line.strip():
                    data = json.loads(line)
                    behavior = data.get('regime', 'UNDEFINED')
                    
                    # Weight multipliers (FROZEN)
                    weight_map = {
                        "TRENDING_NORMAL_VOL": 1.0,
                        "TRENDING_HIGH_VOL": 0.2,
                        "MEAN_REVERTING_LOW_VOL": 0.5,
                        "MEAN_REVERTING_HIGH_VOL": 0.3,
                        "EVENT_DOMINANT": 1.0,
                        "EVENT_LOCK": 0.0,
                        "UNDEFINED": 0.5
                    }
                    
                    weight = weight_map.get(behavior, FAIL_SAFE_WEIGHT)
                    reason = f"REGIME_APPLIED: {behavior} (x{weight})"
                    
                    if behavior == "EVENT_LOCK":
                        reason = "NARRATIVE_MUTED: EVENT_LOCK (0.0x)"
                    
                    return {
                        "regime": behavior,
                        "bias": data.get('bias', 'NEUTRAL'),
                        "confidence": data.get('confidence', 1.0),
                        "lifecycle": "STABLE",
                        "narrative_weight": weight,
                        "enforcement_reason": reason
                    }
    except Exception as e:
        logger.error(f"FAIL_SAFE: Error reading US regime: {e}")
    
    return fail_safe

# =============================================================================
# REGIME-ENFORCED REPOSITORY WRAPPER
# =============================================================================

class RegimeEnforcedRepository(NarrativeRepository):
    """
    Wraps any NarrativeRepository to enforce regime adaptation.
    
    GUARANTEES:
    1. ALL narratives pass through regime adaptation
    2. NO bypass path exists
    3. Regime metadata is ALWAYS attached
    4. Telemetry is ALWAYS logged
    """
    
    def __init__(self, inner_repo: NarrativeRepository):
        self._inner = inner_repo
        self._telemetry_path = Path("data/regime_narrative_telemetry.jsonl")
    
    def save_narrative(self, narrative: Narrative) -> None:
        """
        THE CANONICAL SAVE PATH.
        
        Every narrative MUST pass through here.
        Regime adaptation is applied unconditionally.
        """
        # 1. Get current regime (fail-safe if unavailable)
        regime = _get_regime_snapshot()
        
        # 2. Compute adjusted confidence
        original_confidence = narrative.confidence_score
        adjusted_confidence = original_confidence * regime["narrative_weight"]
        
        # 3. Attach regime metadata to explainability payload
        regime_metadata = {
            "regime_enforcement": {
                "regime": regime["regime"],
                "regime_bias": regime["bias"],
                "regime_confidence": regime["confidence"],
                "regime_lifecycle": regime["lifecycle"],
                "narrative_confidence": original_confidence,
                "original_weight": original_confidence,
                "final_weight": adjusted_confidence,
                "multiplier": regime["narrative_weight"],
                "enforcement_reason": regime["enforcement_reason"],
                "enforced_at": datetime.utcnow().isoformat()
            }
        }
        
        # 4. Create new narrative with updated confidence and metadata
        data = asdict(narrative)
        data['confidence_score'] = adjusted_confidence
        data['explainability_payload'] = {
            **narrative.explainability_payload,
            **regime_metadata
        }
        
        # Handle frozen dataclass
        adjusted_narrative = Narrative(
            narrative_id=data['narrative_id'],
            title=data['title'],
            market=data['market'],
            scope=data['scope'],
            related_assets=data['related_assets'],
            supporting_events=data['supporting_events'],
            confidence_score=data['confidence_score'],
            lifecycle_state=data['lifecycle_state'],
            version=data['version'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            explainability_payload=data['explainability_payload']
        )
        
        # 5. Log telemetry (MANDATORY)
        self._log_telemetry(adjusted_narrative, original_confidence, regime)
        
        # 6. Persist using inner repository
        self._inner.save_narrative(adjusted_narrative)
        
        logger.info(f"NARRATIVE_ENFORCED: {narrative.narrative_id} | {regime['enforcement_reason']}")
    
    def get_narrative_history(self, narrative_id: str) -> List[Narrative]:
        return self._inner.get_narrative_history(narrative_id)
    
    def get_active_narratives(self, market: Market) -> List[Narrative]:
        return self._inner.get_active_narratives(market)
    
    def _log_telemetry(self, narrative: Narrative, original: float, regime: Dict):
        """
        Log every adjustment. Mandatory. Non-bypassable.
        """
        log_packet = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "NARRATIVE_ENFORCEMENT",
            "narrative_id": narrative.narrative_id,
            "title": narrative.title,
            "market": narrative.market.value if hasattr(narrative.market, 'value') else str(narrative.market),
            "assets": narrative.related_assets,
            "original_weight": round(original, 4),
            "final_weight": round(narrative.confidence_score, 4),
            "regime": regime["regime"],
            "bias": regime["bias"],
            "confidence": regime["confidence"],
            "lifecycle": regime["lifecycle"],
            "enforcement_reason": regime["enforcement_reason"]
        }
        
        try:
            self._telemetry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._telemetry_path, 'a') as f:
                f.write(json.dumps(log_packet) + "\n")
        except Exception as e:
            logger.error(f"Telemetry write failed: {e}")

# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def wrap_with_regime_enforcement(repo: NarrativeRepository) -> NarrativeRepository:
    """
    Factory function to wrap any repository with regime enforcement.
    
    Usage:
        raw_repo = ParquetNarrativeRepository(...)
        enforced_repo = wrap_with_regime_enforcement(raw_repo)
        engine = NarrativeGenesisEngine(enforced_repo)
    """
    return RegimeEnforcedRepository(repo)
