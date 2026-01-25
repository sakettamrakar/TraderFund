"""
HITL Approval Gate (L11 - Decision Plane).
Implements Human-in-the-Loop approval interface.

SAFETY INVARIANTS:
- Decisions CANNOT act without explicit human approval.
- Automatic approval is FORBIDDEN.
- Timeout-based approval is FORBIDDEN.
- All approvals are audited.
"""
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum

from .decision_spec import DecisionSpec, DecisionStatus, DecisionRouting


class ApprovalAction(str, Enum):
    """Actions a human can take on a decision."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    DEFER = "DEFER"  # Send back to pending for later review


class ApprovalResult:
    """Result of an approval action."""
    def __init__(
        self,
        decision_id: str,
        action: ApprovalAction,
        authority: str,
        reason: Optional[str] = None
    ):
        self.decision_id = decision_id
        self.action = action
        self.authority = authority
        self.reason = reason
        self.timestamp = datetime.now()


class HITLGate:
    """
    Human-in-the-Loop approval gate.
    
    SAFETY GUARANTEES:
    - No decision passes without explicit human action.
    - No timeout-based auto-approval.
    - All actions are logged.
    - Approval authority is recorded.
    """
    
    def __init__(self):
        self._pending_decisions: Dict[str, DecisionSpec] = {}
        self._approval_log: list = []
        self._approval_callback: Optional[Callable] = None
    
    def submit_for_approval(self, decision: DecisionSpec) -> str:
        """
        Submit a decision for human approval.
        
        Returns the decision ID for tracking.
        """
        if decision.routing != DecisionRouting.HITL:
            raise ValueError(f"Decision {decision.decision_id} not routed to HITL")
        
        self._pending_decisions[decision.decision_id] = decision
        
        self._approval_log.append({
            "event": "SUBMITTED",
            "decision_id": decision.decision_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return decision.decision_id
    
    def get_pending(self) -> list:
        """Get all decisions awaiting approval."""
        return list(self._pending_decisions.values())
    
    def approve(self, decision_id: str, authority: str, reason: Optional[str] = None) -> ApprovalResult:
        """
        Approve a decision.
        
        This is an EXPLICIT human action, not automatic.
        """
        if decision_id not in self._pending_decisions:
            raise ValueError(f"Decision {decision_id} not found in pending queue")
        
        result = ApprovalResult(
            decision_id=decision_id,
            action=ApprovalAction.APPROVE,
            authority=authority,
            reason=reason
        )
        
        del self._pending_decisions[decision_id]
        
        self._approval_log.append({
            "event": "APPROVED",
            "decision_id": decision_id,
            "authority": authority,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        if self._approval_callback:
            self._approval_callback(result)
        
        return result
    
    def reject(self, decision_id: str, authority: str, reason: str) -> ApprovalResult:
        """
        Reject a decision.
        
        Reason is REQUIRED for rejections.
        """
        if decision_id not in self._pending_decisions:
            raise ValueError(f"Decision {decision_id} not found in pending queue")
        
        result = ApprovalResult(
            decision_id=decision_id,
            action=ApprovalAction.REJECT,
            authority=authority,
            reason=reason
        )
        
        del self._pending_decisions[decision_id]
        
        self._approval_log.append({
            "event": "REJECTED",
            "decision_id": decision_id,
            "authority": authority,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def get_audit_log(self) -> list:
        """Get the complete approval audit log."""
        return self._approval_log.copy()
    
    def set_approval_callback(self, callback: Callable[[ApprovalResult], None]) -> None:
        """Set a callback to be invoked when a decision is approved."""
        self._approval_callback = callback
    
    # =========================================
    # FORBIDDEN OPERATIONS (NOT IMPLEMENTED)
    # =========================================
    # The following operations are EXPLICITLY FORBIDDEN:
    # - auto_approve()
    # - approve_after_timeout()
    # - approve_all()
    # - bypass_approval()
    # Any function that approves without human action is INVALID.
