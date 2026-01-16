# Narrative Regime Enforcement v1.0 — HARD & FROZEN
#
# This module enforces regime-based narrative weight adjustment.
# HARD mode only — no bypass, no toggles, no exceptions.
#
# FROZEN: Weight mappings are locked. Changes require version bump.

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, NamedTuple
from pathlib import Path
from pydantic import BaseModel

from traderfund.regime.types import MarketBehavior

logger = logging.getLogger(__name__)

# =============================================================================
# FROZEN WEIGHT MAPPINGS — DO NOT MODIFY WITHOUT VERSION BUMP
# =============================================================================

WEIGHT_MULTIPLIERS = {
    # Trending regimes: full weight
    MarketBehavior.TRENDING_NORMAL_VOL: 1.0,
    MarketBehavior.TRENDING_HIGH_VOL: 0.2,  # HIGH_VOL dampened
    
    # Mean reverting regimes: dampened
    MarketBehavior.MEAN_REVERTING_LOW_VOL: 0.5,
    MarketBehavior.MEAN_REVERTING_HIGH_VOL: 0.3,
    
    # Event regimes
    MarketBehavior.EVENT_DOMINANT: 1.0,  # Cap at 1.0 (was 1.2x)
    MarketBehavior.EVENT_LOCK: 0.0,      # MUTED completely
    
    # Fallback
    MarketBehavior.UNDEFINED: 0.5,       # Fail-safe dampen
}

# Fail-safe defaults
FAIL_SAFE_WEIGHT = 0.5
CONFIDENCE_THRESHOLD = 0.3

# =============================================================================
# REGIME QUERY INTERFACE
# =============================================================================

class RegimeSnapshot(BaseModel):
    """Clean regime snapshot for narrative consumers."""
    regime: str
    bias: str
    confidence: float
    lifecycle: str
    posture: str
    narrative_weight: float
    timestamp: str

def get_current_us_market_regime() -> RegimeSnapshot:
    """
    Query interface for US Market Regime.
    Returns fail-safe if regime unavailable.
    """
    log_path = Path("data/us_market/us_market_regime.jsonl")
    
    # FAIL-SAFE default
    fail_safe = RegimeSnapshot(
        regime="UNDEFINED",
        bias="NEUTRAL",
        confidence=0.0,
        lifecycle="UNKNOWN",
        posture="CAUTIOUS",
        narrative_weight=FAIL_SAFE_WEIGHT,
        timestamp=datetime.now().isoformat()
    )
    
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
                    
                    # Derive weight from frozen mapping
                    try:
                        beh_enum = MarketBehavior(behavior)
                        weight = WEIGHT_MULTIPLIERS.get(beh_enum, FAIL_SAFE_WEIGHT)
                    except ValueError:
                        weight = FAIL_SAFE_WEIGHT
                    
                    # Derive posture
                    posture = "NORMAL"
                    if "HIGH_VOL" in behavior: posture = "CAUTIOUS"
                    if "EVENT" in behavior: posture = "RISK_OFF"
                    
                    return RegimeSnapshot(
                        regime=behavior,
                        bias=data.get('bias', 'NEUTRAL'),
                        confidence=data.get('confidence', 1.0),
                        lifecycle="STABLE",
                        posture=posture,
                        narrative_weight=weight,
                        timestamp=data.get('timestamp', datetime.now().isoformat())
                    )
    except Exception as e:
        logger.error(f"FAIL_SAFE: Error reading US regime: {e}")
    
    return fail_safe

# =============================================================================
# DATA MODELS
# =============================================================================

class NarrativeSignal(BaseModel):
    """Narrative signal to be adjusted by regime."""
    symbol: str
    weight: float
    confidence: float
    narrative_id: str
    summary: str

class AdjustedNarrative(NamedTuple):
    original_weight: float
    final_weight: float
    adjustment_factor: float
    regime: str
    confidence: float
    lifecycle: str
    enforcement_reason: str

# =============================================================================
# CANONICAL NARRATIVE ADAPTER — HARD ENFORCEMENT ONLY
# =============================================================================

class RegimeNarrativeAdapter:
    """
    Canonical Regime → Narrative Adapter.
    
    HARD ENFORCEMENT ONLY:
    - No bypass
    - No toggles
    - No exceptions
    
    All narrative weight adjustments MUST go through this adapter.
    """
    
    def __init__(self):
        self.telemetry_path = Path("data/regime_narrative_telemetry.jsonl")
        # Expose frozen mappings for external reference
        self.WEIGHT_MULTIPLIERS = WEIGHT_MULTIPLIERS

    def adjust_signal(self, signal: NarrativeSignal) -> AdjustedNarrative:
        """
        Compute final narrative weight based on current regime.
        
        This is the ONLY entry point for narrative weight adjustment.
        No bypass path exists.
        """
        # 1. Fetch current regime (never skip)
        snapshot = get_current_us_market_regime()
        
        # 2. Determine weight factor
        try:
            behavior = MarketBehavior(snapshot.regime)
            factor = WEIGHT_MULTIPLIERS.get(behavior, FAIL_SAFE_WEIGHT)
        except ValueError:
            factor = FAIL_SAFE_WEIGHT
            
        # 3. Apply fail-safe rules
        reason = f"REGIME_APPLIED: {snapshot.regime} (x{factor})"
        
        # Fail-safe: low confidence
        if snapshot.confidence < CONFIDENCE_THRESHOLD:
            factor = FAIL_SAFE_WEIGHT
            reason = f"FAIL_SAFE_DAMPEN: Low confidence ({snapshot.confidence:.2f})"
        
        # Fail-safe: lifecycle transition
        if snapshot.lifecycle == "TRANSITION":
            factor = FAIL_SAFE_WEIGHT
            reason = "FAIL_SAFE_DAMPEN: Regime in transition"
        
        # 4. Compute final weight
        raw_weight = signal.weight * factor
        final_weight = min(1.0, max(0.0, raw_weight))
        
        # 5. Special case: EVENT_LOCK
        if snapshot.regime == "EVENT_LOCK":
            final_weight = 0.0
            reason = "NARRATIVE_MUTED: EVENT_LOCK (0.0x)"
        
        # 6. Build result
        result = AdjustedNarrative(
            original_weight=signal.weight,
            final_weight=final_weight,
            adjustment_factor=factor,
            regime=snapshot.regime,
            confidence=snapshot.confidence,
            lifecycle=snapshot.lifecycle,
            enforcement_reason=reason
        )
        
        # 7. Mandatory telemetry (never skip)
        self._log_telemetry(signal, result)
        
        return result

    def _log_telemetry(self, signal: NarrativeSignal, result: AdjustedNarrative):
        """
        Log every adjustment. Mandatory. Non-bypassable.
        """
        log_packet = {
            "timestamp": datetime.now().isoformat(),
            "type": "NARRATIVE_ENFORCEMENT",
            "symbol": signal.symbol,
            "narrative_id": signal.narrative_id,
            "original_weight": round(result.original_weight, 4),
            "final_weight": round(result.final_weight, 4),
            "adjustment_factor": result.adjustment_factor,
            "regime": result.regime,
            "confidence": round(result.confidence, 4),
            "lifecycle": result.lifecycle,
            "enforcement_reason": result.enforcement_reason
        }
        
        # Write to file
        try:
            self.telemetry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.telemetry_path, 'a') as f:
                f.write(json.dumps(log_packet) + "\n")
        except Exception as e:
            logger.error(f"Telemetry write failed: {e}")
        
        # Console logging
        if result.adjustment_factor == 0.0:
            logger.warning(f"NARRATIVE_MUTED: {signal.symbol} | {result.enforcement_reason}")
        elif result.adjustment_factor < 1.0:
            logger.info(f"NARRATIVE_DAMPENED: {signal.symbol} | {result.enforcement_reason}")
        else:
            logger.debug(f"NARRATIVE_FULL: {signal.symbol}")

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Singleton adapter instance
_adapter_instance = None

def get_narrative_adapter() -> RegimeNarrativeAdapter:
    """Get singleton adapter instance."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = RegimeNarrativeAdapter()
    return _adapter_instance

def apply_regime_to_narrative(signal: NarrativeSignal) -> AdjustedNarrative:
    """
    One-liner for applying regime to any narrative signal.
    This is the CANONICAL entry point.
    """
    return get_narrative_adapter().adjust_signal(signal)

def get_regime_weight_for_behavior(behavior_str: str) -> float:
    """
    Quick lookup of weight multiplier for a behavior string.
    Uses frozen mappings.
    """
    try:
        behavior = MarketBehavior(behavior_str)
        return WEIGHT_MULTIPLIERS.get(behavior, FAIL_SAFE_WEIGHT)
    except ValueError:
        return FAIL_SAFE_WEIGHT
