"""
Strategy Registry (L10 - Strategy).
The only legal place where strategies may exist.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from .strategy_mapping import StrategyDefinition


class LifecycleState(str, Enum):
    """Strategy lifecycle states."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class RegistryEntry(BaseModel):
    """
    A governed strategy registry entry.
    
    Invariants:
    - strategy_id is immutable after registration.
    - lifecycle_state transitions are governed.
    - audit_log is append-only.
    """
    # Identity
    strategy_id: str
    definition: StrategyDefinition
    
    # Governance
    lifecycle_state: LifecycleState = LifecycleState.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    created_under_decision: str
    last_modified_at: datetime = Field(default_factory=datetime.now)
    last_modified_decision: Optional[str] = None
    
    # Audit
    audit_log: List[Dict[str, Any]] = Field(default_factory=list)


class StrategyRegistry:
    """
    Governed strategy registry.
    
    Invariants:
    - Strategies must begin in DRAFT state.
    - Only ACTIVE strategies may be executed.
    - RETIRED is terminal and irreversible.
    - All transitions are logged.
    """
    
    def __init__(self):
        self._entries: Dict[str, RegistryEntry] = {}
    
    def register(self, definition: StrategyDefinition, decision_ref: str) -> RegistryEntry:
        """
        Register a new strategy in DRAFT state.
        
        REG-1: All required fields must be present.
        REG-2: lifecycle_state must be DRAFT on initial registration.
        REG-3: created_under_decision must reference a valid Decision.
        """
        if definition.strategy_id in self._entries:
            raise ValueError(f"Strategy already exists: {definition.strategy_id}")
        
        entry = RegistryEntry(
            strategy_id=definition.strategy_id,
            definition=definition,
            lifecycle_state=LifecycleState.DRAFT,
            created_under_decision=decision_ref,
        )
        entry.audit_log.append({
            "event": "REGISTERED",
            "state": LifecycleState.DRAFT.value,
            "decision": decision_ref,
            "timestamp": datetime.now().isoformat()
        })
        
        self._entries[definition.strategy_id] = entry
        return entry
    
    def get(self, strategy_id: str) -> Optional[RegistryEntry]:
        """Retrieve a registry entry by strategy ID."""
        return self._entries.get(strategy_id)
    
    def is_executable(self, strategy_id: str) -> bool:
        """Check if a strategy can be executed (ACTIVE only)."""
        entry = self._entries.get(strategy_id)
        return entry is not None and entry.lifecycle_state == LifecycleState.ACTIVE
    
    def list_by_state(self, state: LifecycleState) -> List[str]:
        """List all strategies in a given lifecycle state."""
        return [sid for sid, entry in self._entries.items() if entry.lifecycle_state == state]
    
    def count(self) -> Dict[str, int]:
        """Count strategies by lifecycle state."""
        counts = {state.value: 0 for state in LifecycleState}
        for entry in self._entries.values():
            counts[entry.lifecycle_state.value] += 1
        return counts
