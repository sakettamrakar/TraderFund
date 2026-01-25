"""
Permission Revocation Handler (SS-5.3).
Implements mid-execution revocation mechanism.

SAFETY INVARIANTS:
- Revocation must be immediate and auditable.
- No strategy may continue after permission revocation.
- Revocation does not affect other strategies.
"""
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum


class RevocationReason(str, Enum):
    """Reason for permission revocation."""
    POLICY_VIOLATION = "POLICY_VIOLATION"
    KILL_SWITCH = "KILL_SWITCH"
    BOUNDS_EXCEEDED = "BOUNDS_EXCEEDED"
    MANUAL_OPERATOR = "MANUAL_OPERATOR"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"


class RevocationEvent:
    """Record of a revocation event."""
    def __init__(
        self,
        strategy_id: str,
        reason: RevocationReason,
        authority: str,
        revoked_permissions: List[str]
    ):
        self.strategy_id = strategy_id
        self.reason = reason
        self.authority = authority
        self.revoked_permissions = revoked_permissions
        self.timestamp = datetime.now()
        self.is_audited = True  # Always audited


class RevocationHandler:
    """
    Handles mid-execution permission revocation.
    
    SAFETY GUARANTEES:
    - Revocation is immediate (no grace period).
    - Revocation is audited (logged with timestamp).
    - Revocation is isolated (affects only target strategy).
    - Revocation is irreversible until manually cleared.
    """
    
    def __init__(self):
        self._revoked_strategies: Set[str] = set()
        self._revocation_log: List[RevocationEvent] = []
        self._kill_switch_active: bool = False
    
    def revoke(
        self,
        strategy_id: str,
        reason: RevocationReason,
        authority: str,
        permissions: Optional[List[str]] = None
    ) -> RevocationEvent:
        """
        Revoke permissions for a strategy.
        
        This is IMMEDIATE and AUDITED.
        """
        if permissions is None:
            permissions = ["ALL"]
        
        event = RevocationEvent(
            strategy_id=strategy_id,
            reason=reason,
            authority=authority,
            revoked_permissions=permissions
        )
        
        self._revoked_strategies.add(strategy_id)
        self._revocation_log.append(event)
        
        return event
    
    def is_revoked(self, strategy_id: str) -> bool:
        """Check if a strategy has been revoked."""
        return strategy_id in self._revoked_strategies or self._kill_switch_active
    
    def activate_kill_switch(self, authority: str) -> List[RevocationEvent]:
        """
        Activate global kill-switch.
        
        OBL-SS-KILLSWITCH: Immediately halts all execution.
        """
        self._kill_switch_active = True
        
        # Record kill-switch event
        event = RevocationEvent(
            strategy_id="GLOBAL",
            reason=RevocationReason.KILL_SWITCH,
            authority=authority,
            revoked_permissions=["ALL"]
        )
        self._revocation_log.append(event)
        
        return [event]
    
    def deactivate_kill_switch(self, authority: str) -> None:
        """
        Deactivate kill-switch (manual reset).
        
        This requires explicit authorization.
        """
        if not self._kill_switch_active:
            return
        
        self._kill_switch_active = False
        
        # Record deactivation
        event = RevocationEvent(
            strategy_id="GLOBAL",
            reason=RevocationReason.MANUAL_OPERATOR,
            authority=authority,
            revoked_permissions=[]
        )
        self._revocation_log.append(event)
    
    def clear_revocation(self, strategy_id: str, authority: str) -> bool:
        """
        Clear revocation for a strategy (manual reset).
        
        Returns True if cleared, False if not revoked.
        """
        if strategy_id not in self._revoked_strategies:
            return False
        
        self._revoked_strategies.remove(strategy_id)
        
        # Record clearance
        event = RevocationEvent(
            strategy_id=strategy_id,
            reason=RevocationReason.MANUAL_OPERATOR,
            authority=authority,
            revoked_permissions=[]
        )
        self._revocation_log.append(event)
        
        return True
    
    def get_audit_log(self) -> List[RevocationEvent]:
        """Get the complete revocation audit log."""
        return self._revocation_log.copy()
    
    def is_kill_switch_active(self) -> bool:
        """Check if kill-switch is active."""
        return self._kill_switch_active
