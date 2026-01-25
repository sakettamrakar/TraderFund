"""
Decision Cycle Replay Engine (L12 - Evolution Phase).
Replays decision cycles in shadow mode for evaluation.

SAFETY INVARIANTS:
- Replay produces audit trail.
- All decisions visible.
- No real execution.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

import sys
sys.path.insert(0, '..')
from decision.decision_spec import DecisionSpec, StateSnapshot, DecisionRouting
from decision.audit_integration import DecisionAuditIntegration


@dataclass
class ReplayStep:
    """A single step in a replay cycle."""
    step_index: int
    strategy_id: str
    decision: Optional[DecisionSpec]
    state_at_step: StateSnapshot
    outcome: str
    timestamp: datetime


class ReplayResult:
    """Complete result of a replay session."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.steps: List[ReplayStep] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.total_decisions = 0
        self.total_failures = 0
    
    def add_step(self, step: ReplayStep) -> None:
        self.steps.append(step)
        self.total_decisions += 1 if step.decision else 0
        self.total_failures += 1 if step.outcome == "FAILURE" else 0
    
    def complete(self) -> None:
        self.end_time = datetime.now()


class ReplayEngine:
    """
    Decision cycle replay engine.
    
    SAFETY GUARANTEES:
    - All replay is shadow mode only.
    - Every decision is audited.
    - Full state visibility at each step.
    - No real capital affected.
    """
    
    def __init__(self):
        self._audit = DecisionAuditIntegration()
        self._session_counter = 0
        self._sessions: Dict[str, ReplayResult] = {}
    
    def create_session(self) -> str:
        """Create a new replay session."""
        self._session_counter += 1
        session_id = f"REPLAY-{self._session_counter:06d}"
        self._sessions[session_id] = ReplayResult(session_id)
        return session_id
    
    def replay_decision(
        self,
        session_id: str,
        strategy_id: str,
        decision: DecisionSpec,
        state: StateSnapshot
    ) -> ReplayStep:
        """
        Replay a single decision.
        
        Returns the step with full visibility.
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        
        # Record in audit
        self._audit.record_creation(decision)
        
        # Create replay step
        step = ReplayStep(
            step_index=len(session.steps),
            strategy_id=strategy_id,
            decision=decision,
            state_at_step=state,
            outcome="SUCCESS",
            timestamp=datetime.now()
        )
        
        session.add_step(step)
        return step
    
    def record_failure(
        self,
        session_id: str,
        strategy_id: str,
        state: StateSnapshot,
        failure_reason: str
    ) -> ReplayStep:
        """
        Record a failure during replay.
        
        Failures are first-class signals.
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        
        step = ReplayStep(
            step_index=len(session.steps),
            strategy_id=strategy_id,
            decision=None,
            state_at_step=state,
            outcome="FAILURE",
            timestamp=datetime.now()
        )
        
        session.add_step(step)
        return step
    
    def complete_session(self, session_id: str) -> ReplayResult:
        """Complete a replay session."""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self._sessions[session_id]
        session.complete()
        return session
    
    def get_session(self, session_id: str) -> Optional[ReplayResult]:
        """Get a replay session by ID."""
        return self._sessions.get(session_id)
    
    def get_decision_visibility(self, session_id: str, step_index: int) -> Dict[str, Any]:
        """
        Get full visibility for a decision step.
        
        OBL-EV-VISIBILITY: Every decision exposes full context.
        """
        session = self._sessions.get(session_id)
        if not session or step_index >= len(session.steps):
            return {}
        
        step = session.steps[step_index]
        
        return {
            "session_id": session_id,
            "step_index": step_index,
            "strategy_id": step.strategy_id,
            "decision_id": step.decision.decision_id if step.decision else None,
            "state": {
                "regime": step.state_at_step.regime,
                "macro": step.state_at_step.macro_context,
                "factor": step.state_at_step.factor_context,
                "timestamp": step.state_at_step.timestamp.isoformat()
            },
            "outcome": step.outcome,
            "timestamp": step.timestamp.isoformat()
        }
