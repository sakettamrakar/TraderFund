"""
Strategy Lifecycle Governance (L10 - Strategy).
Implements DRAFT → ACTIVE → SUSPENDED → RETIRED state machine.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from .registry import StrategyRegistry, RegistryEntry, LifecycleState


class TransitionError(Exception):
    """Raised when a lifecycle transition is invalid."""
    pass


# Valid transitions: (from_state, to_state)
VALID_TRANSITIONS = {
    (LifecycleState.DRAFT, LifecycleState.ACTIVE),
    (LifecycleState.DRAFT, LifecycleState.RETIRED),
    (LifecycleState.ACTIVE, LifecycleState.SUSPENDED),
    (LifecycleState.ACTIVE, LifecycleState.RETIRED),
    (LifecycleState.SUSPENDED, LifecycleState.ACTIVE),
    (LifecycleState.SUSPENDED, LifecycleState.RETIRED),
}


class LifecycleGovernor:
    """
    Governs strategy lifecycle transitions.
    
    Invariants:
    - Transitions must follow valid state machine edges.
    - RETIRED is terminal; no further transitions allowed.
    - All transitions require a decision reference.
    - All transitions are audited.
    """
    
    def __init__(self, registry: StrategyRegistry):
        self._registry = registry
    
    def can_transition(self, strategy_id: str, to_state: LifecycleState) -> bool:
        """Check if a transition is valid."""
        entry = self._registry.get(strategy_id)
        if entry is None:
            return False
        
        transition = (entry.lifecycle_state, to_state)
        return transition in VALID_TRANSITIONS
    
    def transition(self, strategy_id: str, to_state: LifecycleState, decision_ref: str) -> RegistryEntry:
        """
        Transition a strategy to a new lifecycle state.
        
        LCT-1: Transition requires decision reference.
        LCT-2: Transition must follow valid state machine edges.
        LCT-3: RETIRED is terminal.
        """
        entry = self._registry.get(strategy_id)
        if entry is None:
            raise TransitionError(f"Strategy not found: {strategy_id}")
        
        if entry.lifecycle_state == LifecycleState.RETIRED:
            raise TransitionError(f"Cannot transition RETIRED strategy: {strategy_id}")
        
        transition = (entry.lifecycle_state, to_state)
        if transition not in VALID_TRANSITIONS:
            raise TransitionError(
                f"Invalid transition: {entry.lifecycle_state.value} → {to_state.value}"
            )
        
        # Perform transition
        old_state = entry.lifecycle_state
        entry.lifecycle_state = to_state
        entry.last_modified_at = datetime.now()
        entry.last_modified_decision = decision_ref
        
        # Audit log
        entry.audit_log.append({
            "event": "TRANSITION",
            "from_state": old_state.value,
            "to_state": to_state.value,
            "decision": decision_ref,
            "timestamp": datetime.now().isoformat()
        })
        
        return entry
    
    def activate(self, strategy_id: str, decision_ref: str) -> RegistryEntry:
        """Convenience: Transition from DRAFT/SUSPENDED to ACTIVE."""
        return self.transition(strategy_id, LifecycleState.ACTIVE, decision_ref)
    
    def suspend(self, strategy_id: str, decision_ref: str) -> RegistryEntry:
        """Convenience: Transition from ACTIVE to SUSPENDED."""
        return self.transition(strategy_id, LifecycleState.SUSPENDED, decision_ref)
    
    def retire(self, strategy_id: str, decision_ref: str) -> RegistryEntry:
        """Convenience: Transition any state to RETIRED (terminal)."""
        return self.transition(strategy_id, LifecycleState.RETIRED, decision_ref)
    
    def get_audit_log(self, strategy_id: str) -> list:
        """Get the audit log for a strategy."""
        entry = self._registry.get(strategy_id)
        return entry.audit_log if entry else []
