"""
Decision Audit Integration (L11 - Decision Plane).
Wires decision creation to Ledger + DID generation.

SAFETY INVARIANTS:
- Every decision produces a ledger entry.
- Every decision produces a DID artifact.
- Decisions without audit trail are INVALID.
- Audit data loss is FORBIDDEN.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .decision_spec import DecisionSpec, DecisionStatus


class AuditEntry:
    """A single audit log entry for a decision."""
    def __init__(
        self,
        decision_id: str,
        event: str,
        details: Dict[str, Any]
    ):
        self.decision_id = decision_id
        self.event = event
        self.details = details
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "event": self.event,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class DecisionAuditIntegration:
    """
    Wires decisions to Ledger and DID generation.
    
    SAFETY GUARANTEES:
    - Every decision creation is logged.
    - Every routing decision is logged.
    - Every approval/rejection is logged.
    - Every execution (shadow) is logged.
    - Audit log is append-only.
    """
    
    def __init__(self):
        self._audit_log: List[AuditEntry] = []
        self._did_artifacts: Dict[str, Dict[str, Any]] = {}
    
    def record_creation(self, decision: DecisionSpec) -> AuditEntry:
        """Record decision creation in audit log."""
        entry = AuditEntry(
            decision_id=decision.decision_id,
            event="DECISION_CREATED",
            details={
                "strategy_ref": decision.strategy_ref,
                "routing": decision.routing.value,
                "proposed_action": decision.proposed_action.action_type,
                "state_snapshot_timestamp": decision.state_snapshot.timestamp.isoformat()
            }
        )
        self._audit_log.append(entry)
        self._generate_did(decision, "creation")
        return entry
    
    def record_routing(self, decision_id: str, routing: str, authority: str) -> AuditEntry:
        """Record decision routing in audit log."""
        entry = AuditEntry(
            decision_id=decision_id,
            event="DECISION_ROUTED",
            details={
                "routing": routing,
                "authority": authority
            }
        )
        self._audit_log.append(entry)
        return entry
    
    def record_approval(self, decision_id: str, action: str, authority: str, reason: Optional[str]) -> AuditEntry:
        """Record approval/rejection in audit log."""
        entry = AuditEntry(
            decision_id=decision_id,
            event=f"DECISION_{action}",
            details={
                "action": action,
                "authority": authority,
                "reason": reason
            }
        )
        self._audit_log.append(entry)
        self._generate_did_update(decision_id, action)
        return entry
    
    def record_execution(self, decision_id: str, mode: str, outcome: Dict[str, Any]) -> AuditEntry:
        """Record execution (shadow) in audit log."""
        entry = AuditEntry(
            decision_id=decision_id,
            event="DECISION_EXECUTED",
            details={
                "mode": mode,
                "is_real": mode != "SHADOW",
                "outcome_summary": str(outcome)[:200]  # Truncate for log
            }
        )
        self._audit_log.append(entry)
        self._generate_did_update(decision_id, "executed")
        return entry
    
    def _generate_did(self, decision: DecisionSpec, event_type: str) -> None:
        """Generate DID artifact for a decision."""
        did = {
            "decision_id": decision.decision_id,
            "event_type": event_type,
            "strategy_ref": decision.strategy_ref,
            "created_at": datetime.now().isoformat(),
            "state_hash": hash(str(decision.state_snapshot.timestamp))
        }
        self._did_artifacts[decision.decision_id] = did
    
    def _generate_did_update(self, decision_id: str, event_type: str) -> None:
        """Update DID artifact with new event."""
        if decision_id in self._did_artifacts:
            self._did_artifacts[decision_id][f"{event_type}_at"] = datetime.now().isoformat()
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the complete audit log."""
        return [entry.to_dict() for entry in self._audit_log]
    
    def get_audit_for_decision(self, decision_id: str) -> List[Dict[str, Any]]:
        """Get audit entries for a specific decision."""
        return [
            entry.to_dict() for entry in self._audit_log
            if entry.decision_id == decision_id
        ]
    
    def get_did(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get DID artifact for a decision."""
        return self._did_artifacts.get(decision_id)
    
    def export_ledger_entry(self, decision_id: str) -> str:
        """Export a decision's audit trail as a ledger entry."""
        entries = self.get_audit_for_decision(decision_id)
        did = self.get_did(decision_id)
        
        ledger_entry = {
            "decision_id": decision_id,
            "audit_trail": entries,
            "did": did,
            "exported_at": datetime.now().isoformat()
        }
        
        return json.dumps(ledger_entry, indent=2)
