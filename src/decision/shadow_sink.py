"""
Shadow Execution Sink (L11 - Decision Plane).
Implements paper trading / simulation environment.

SAFETY INVARIANTS:
- Shadow execution affects ZERO real capital.
- No broker connections exist.
- No market interaction occurs.
- All results are clearly labeled as SHADOW.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from .decision_spec import DecisionSpec, DecisionStatus, DecisionRouting


class ShadowResult:
    """Result of shadow/paper execution."""
    def __init__(
        self,
        decision_id: str,
        simulated_outcome: Dict[str, Any],
        execution_timestamp: datetime
    ):
        self.decision_id = decision_id
        self.simulated_outcome = simulated_outcome
        self.execution_timestamp = execution_timestamp
        self.is_real = False  # ALWAYS False
        self.mode = "SHADOW"  # ALWAYS SHADOW


class ShadowExecutionSink:
    """
    Paper trading / simulation environment.
    
    SAFETY GUARANTEES:
    - Operates on SIMULATED state only.
    - Affects ZERO real capital.
    - Produces audit trail identical to real execution.
    - All results labeled as SHADOW.
    - NO broker connections.
    - NO API keys loaded.
    - NO network calls to trading endpoints.
    """
    
    def __init__(self):
        self._executed_decisions: Dict[str, ShadowResult] = {}
        self._execution_log: list = []
        self._simulated_positions: Dict[str, float] = {}  # Simulated holdings
        self._simulated_cash: float = 1_000_000.0  # Paper money
    
    def execute(self, decision: DecisionSpec) -> ShadowResult:
        """
        Execute a decision in shadow/paper mode.
        
        This is SIMULATION ONLY. No real capital is affected.
        """
        if decision.routing != DecisionRouting.SHADOW:
            raise ValueError(f"Decision {decision.decision_id} not routed to SHADOW")
        
        # Simulate the execution (no real market interaction)
        simulated_outcome = self._simulate_execution(decision)
        
        result = ShadowResult(
            decision_id=decision.decision_id,
            simulated_outcome=simulated_outcome,
            execution_timestamp=datetime.now()
        )
        
        self._executed_decisions[decision.decision_id] = result
        
        self._execution_log.append({
            "event": "SHADOW_EXECUTED",
            "decision_id": decision.decision_id,
            "mode": "SHADOW",
            "is_real": False,
            "simulated_outcome": simulated_outcome,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _simulate_execution(self, decision: DecisionSpec) -> Dict[str, Any]:
        """
        Simulate execution without real market interaction.
        
        This produces realistic-looking but FAKE results.
        """
        action = decision.proposed_action
        
        # Simple simulation logic (no real data)
        return {
            "action_type": action.action_type,
            "target": action.target,
            "simulated_price": 100.0,  # Placeholder
            "simulated_quantity": action.quantity_hint or "unspecified",
            "simulated_fill": "COMPLETE",
            "simulation_note": "This is PAPER execution - no real capital affected",
            "is_real": False
        }
    
    def get_result(self, decision_id: str) -> Optional[ShadowResult]:
        """Get the shadow execution result for a decision."""
        return self._executed_decisions.get(decision_id)
    
    def get_execution_log(self) -> list:
        """Get the complete shadow execution log."""
        return self._execution_log.copy()
    
    def get_simulated_positions(self) -> Dict[str, float]:
        """Get simulated (paper) positions."""
        return self._simulated_positions.copy()
    
    def reset_simulation(self) -> None:
        """Reset the simulation state."""
        self._simulated_positions = {}
        self._simulated_cash = 1_000_000.0
        self._execution_log.append({
            "event": "SIMULATION_RESET",
            "timestamp": datetime.now().isoformat()
        })
    
    # =========================================
    # FORBIDDEN OPERATIONS (NOT IMPLEMENTED)
    # =========================================
    # The following operations are EXPLICITLY FORBIDDEN:
    # - connect_broker()
    # - execute_real()
    # - place_order()
    # - get_real_positions()
    # - load_api_keys()
    # Any function that interacts with real markets is INVALID.
