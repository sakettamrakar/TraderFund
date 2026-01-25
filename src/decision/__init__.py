# Decision Package
"""
Decision Package (L11 - Decision Plane).
Provides decision specification, HITL gate, shadow execution, and audit.

SAFETY: This package enables CHOICE FORMATION, not CHOICE EXECUTION.
All real market interaction is FORBIDDEN.
"""
from .decision_spec import (
    DecisionSpec,
    DecisionFactory,
    DecisionRouting,
    DecisionStatus,
    ProposedAction,
    StateSnapshot
)
from .hitl_gate import HITLGate, ApprovalAction, ApprovalResult
from .shadow_sink import ShadowExecutionSink, ShadowResult
from .audit_integration import DecisionAuditIntegration, AuditEntry

__all__ = [
    # Decision spec
    "DecisionSpec",
    "DecisionFactory",
    "DecisionRouting",
    "DecisionStatus",
    "ProposedAction",
    "StateSnapshot",
    # HITL
    "HITLGate",
    "ApprovalAction",
    "ApprovalResult",
    # Shadow
    "ShadowExecutionSink",
    "ShadowResult",
    # Audit
    "DecisionAuditIntegration",
    "AuditEntry",
]
