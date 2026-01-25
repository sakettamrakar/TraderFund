"""Narrative Evolution - Evolution Tracker (handles state transitions)"""
import logging
from typing import Optional
from datetime import datetime
from . import config
from .models import Narrative, NarrativeState, LifecycleStatus, StageEvidence

logger = logging.getLogger(__name__)

class NarrativeEvolver:
    """Handles narrative state evolution over time."""
    
    def __init__(self):
        self.thresholds = config.EVOLUTION_THRESHOLDS
    
    def compute_evidence_delta(self, current: StageEvidence, 
                               previous: dict) -> float:
        """Compute average score change between evidence snapshots."""
        current_dict = current.to_dict()
        deltas = []
        for key in ["structural_score", "energy_score", "participation_score", 
                    "momentum_score", "risk_score"]:
            curr = current_dict.get(key)
            prev = previous.get(key)
            if curr is not None and prev is not None:
                deltas.append(curr - prev)
        return sum(deltas) / len(deltas) if deltas else 0
    
    def evolve(self, current: Narrative, previous: Optional[Narrative],
               evidence: StageEvidence) -> Narrative:
        """Evolve narrative state based on changes."""
        
        if previous is None:
            # First narrative - starts as emerging
            current.narrative_state = NarrativeState.EMERGING.value
            current.days_in_state = 1
            return current
        
        # Track days in same type
        if previous.narrative_type == current.narrative_type:
            current.days_in_state = previous.days_in_state + 1
        else:
            current.days_in_state = 1
            current.narrative_state = NarrativeState.EMERGING.value
            current.what_changed = f"New type: {previous.narrative_type} → {current.narrative_type}"
            return current
        
        # Compute evidence delta
        delta = self.compute_evidence_delta(evidence, previous.supporting_evidence)
        prev_state = NarrativeState(previous.narrative_state)
        
        # State transition logic
        new_state = prev_state
        
        if delta >= self.thresholds["strengthen_delta"]:
            if prev_state in [NarrativeState.EMERGING, NarrativeState.STABLE]:
                new_state = NarrativeState.STRENGTHENING
                current.what_changed = f"Evidence strengthening (+{delta:.1f})"
        
        elif delta <= self.thresholds["weaken_delta"]:
            if prev_state in [NarrativeState.STABLE, NarrativeState.STRENGTHENING]:
                new_state = NarrativeState.WEAKENING
                current.what_changed = f"Evidence weakening ({delta:.1f})"
        
        elif abs(delta) < 5:  # Stable range
            if prev_state == NarrativeState.EMERGING and current.days_in_state >= 3:
                new_state = NarrativeState.STABLE
                current.what_changed = "Stabilized after 3+ days"
            elif prev_state == NarrativeState.STRENGTHENING:
                new_state = NarrativeState.STABLE
                current.what_changed = "Strength stabilized"
        
        # Check for invalidation
        if prev_state == NarrativeState.WEAKENING:
            if current.days_in_state >= self.thresholds["invalidate_days"]:
                new_state = NarrativeState.INVALIDATED
                current.lifecycle_status = LifecycleStatus.ARCHIVED.value
                current.what_changed = f"Invalidated after {current.days_in_state} days of weakness"
        
        # Check for decay
        if prev_state == NarrativeState.STABLE:
            if current.days_in_state >= self.thresholds["decay_days"] and abs(delta) < 2:
                current.lifecycle_status = LifecycleStatus.DECAYING.value
                current.what_changed = f"Decaying - no significant change for {current.days_in_state} days"
        
        current.narrative_state = new_state.value
        current.previous_state = previous.narrative_state
        current.narrative_id = previous.narrative_id  # Preserve ID for continuity
        current.created_at = previous.created_at  # Preserve creation time
        
        return current
