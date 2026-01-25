"""
Decision Specification (L11 - Decision Plane).
Defines immutable, versioned decision objects.

SAFETY INVARIANTS:
- Decisions represent choices, not actions.
- Decisions cannot execute; they must be routed.
- Decisions are immutable once formed.
- All decisions are auditable.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DecisionRouting(str, Enum):
    """Where a decision is routed for processing."""
    HITL = "HITL"           # Human-in-the-Loop approval required
    SHADOW = "SHADOW"       # Paper/simulation execution only
    PENDING = "PENDING"     # Not yet routed


class DecisionStatus(str, Enum):
    """Lifecycle state of a decision."""
    PROPOSED = "PROPOSED"       # Just created, awaiting routing
    ROUTED = "ROUTED"           # Sent to HITL or SHADOW
    APPROVED = "APPROVED"       # HITL approved (ready for shadow or future exec)
    REJECTED = "REJECTED"       # HITL rejected
    SHADOW_EXECUTED = "SHADOW_EXECUTED"  # Executed in paper mode
    ARCHIVED = "ARCHIVED"       # Final state, no further transitions


class ProposedAction(BaseModel):
    """
    What the decision recommends.
    
    This is DECLARATIVE only—it describes what SHOULD happen,
    not what WILL happen. Execution is separate.
    """
    action_type: str = Field(..., description="e.g., BUY, SELL, HOLD, REBALANCE")
    target: Optional[str] = Field(None, description="e.g., symbol, asset class")
    quantity_hint: Optional[str] = Field(None, description="Descriptive, not binding")
    rationale: str = Field(..., description="Why this action is proposed")


class StateSnapshot(BaseModel):
    """
    Immutable snapshot of system state at decision time.
    """
    regime: Optional[str] = None
    macro_context: Dict[str, Any] = Field(default_factory=dict)
    factor_context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class DecisionSpec(BaseModel):
    """
    Immutable, versioned decision object.
    
    SAFETY GUARANTEES:
    - decision_id is unique and stable.
    - Once created, the decision cannot be modified.
    - Modifications require a new decision with a new ID.
    - All fields are required for audit completeness.
    """
    # Identity
    decision_id: str = Field(..., description="Unique, stable identifier")
    version: str = Field(default="1.0.0", description="Semantic version")
    
    # Binding
    strategy_ref: str = Field(..., description="Reference to registered strategy")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # State context (immutable snapshot)
    state_snapshot: StateSnapshot = Field(default_factory=StateSnapshot)
    
    # The proposed action (declarative only)
    proposed_action: ProposedAction
    
    # Routing
    routing: DecisionRouting = DecisionRouting.PENDING
    status: DecisionStatus = DecisionStatus.PROPOSED
    
    # Audit
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        frozen = True  # Immutable after creation


class DecisionFactory:
    """
    Factory for creating decision objects.
    
    Ensures all decisions are properly formed and auditable.
    """
    
    _counter: int = 0
    
    @classmethod
    def create(
        cls,
        strategy_ref: str,
        proposed_action: ProposedAction,
        state_snapshot: Optional[StateSnapshot] = None,
        routing: DecisionRouting = DecisionRouting.PENDING
    ) -> DecisionSpec:
        """
        Create a new decision object.
        
        Returns an immutable DecisionSpec.
        """
        cls._counter += 1
        decision_id = f"DEC-{cls._counter:06d}"
        
        if state_snapshot is None:
            state_snapshot = StateSnapshot()
        
        decision = DecisionSpec(
            decision_id=decision_id,
            strategy_ref=strategy_ref,
            proposed_action=proposed_action,
            state_snapshot=state_snapshot,
            routing=routing,
            audit_trail=[{
                "event": "CREATED",
                "timestamp": datetime.now().isoformat(),
                "routing": routing.value
            }]
        )
        
        return decision
