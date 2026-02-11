"""
Execution Harness (L11 - Orchestration).
Wires task execution to Belief, Factor, and Validator layers.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import subprocess

from .task_spec import TaskSpec, TaskStatus
from .task_graph import TaskGraph


class ExecutionMode(str, Enum):
    """Execution mode semantics."""
    DRY_RUN = "DRY_RUN"    # Simulate only, no side effects
    REAL_RUN = "REAL_RUN"  # Execute with full side effects


class ExecutionResult:
    """Result of a single task execution."""
    def __init__(self, task_id: str, status: TaskStatus, artifacts: List[str], error: Optional[str] = None):
        self.task_id = task_id
        self.status = status
        self.artifacts = artifacts
        self.error = error
        self.timestamp = datetime.now()


class ExecutionHarness:
    """
    Orchestration harness that binds to Control Plane governance.
    
    Invariants:
    - Cannot execute without valid Control Plane state (checked via belief_layer).
    - All side effects must be declared in task artifacts/impacts.
    - DRY_RUN must accurately predict REAL_RUN outcomes.
    """

    def __init__(self, graph: TaskGraph, standalone_mode: bool = False):
        self._graph = graph
        self._results: Dict[str, ExecutionResult] = {}
        self._belief_layer = None
        self._factor_layer = None
        self._standalone_mode = standalone_mode
    
    def bind_belief_layer(self, belief_layer: Any) -> None:
        """Bind to Belief Layer for epistemic context."""
        self._belief_layer = belief_layer
    
    def bind_factor_layer(self, factor_layer: Any) -> None:
        """Bind to Factor Layer for permission checks."""
        self._factor_layer = factor_layer
    
    def validate_preconditions(self) -> bool:
        """Validate Control Plane governance is active."""
        if self._standalone_mode:
            return True
        if self._belief_layer is None:
            return False
        return True
    
    def execute(self, task_ids: List[str], mode: ExecutionMode) -> List[ExecutionResult]:
        """
        Execute tasks in order.
        
        DRY_RUN: Returns projected outcomes without side effects.
        REAL_RUN: Executes with full side effects and post hooks.
        """
        if not self.validate_preconditions():
            raise RuntimeError("Control Plane governance not bound. Cannot execute.")
        
        results: List[ExecutionResult] = []
        
        for task_id in task_ids:
            spec = self._graph.get_task(task_id)
            if spec is None:
                results.append(ExecutionResult(task_id, TaskStatus.FAILED, [], f"Task not found: {task_id}"))
                continue
            
            # Check dependencies
            deps_satisfied = True
            for dep_id in spec.depends_on:
                dep_result = self._results.get(dep_id)
                if dep_result is None or dep_result.status != TaskStatus.SUCCESS:
                    if spec.blocking:
                        results.append(ExecutionResult(task_id, TaskStatus.FAILED, [], f"Dependency not satisfied: {dep_id}"))
                        deps_satisfied = False
                        break
            if not deps_satisfied:
                continue

            # Execute based on mode
            if mode == ExecutionMode.DRY_RUN:
                result = ExecutionResult(task_id, TaskStatus.SUCCESS, spec.artifacts)
            else:
                # REAL_RUN: Execute the command
                print(f"Executing task: {task_id} with command: {' '.join(spec.command)}")
                try:
                    process = subprocess.run(
                        spec.command,
                        capture_output=True,
                        text=True,
                        check=True # Raise CalledProcessError for non-zero exit codes
                    )
                    print(process.stdout)
                    result = ExecutionResult(task_id, TaskStatus.SUCCESS, spec.artifacts)
                except subprocess.CalledProcessError as e:
                    print(f"Task {task_id} FAILED:\n{e.stderr}")
                    result = ExecutionResult(task_id, TaskStatus.FAILED, spec.artifacts, error=e.stderr)
            
            self._results[task_id] = result
            results.append(result)
        
        return results
    
    def get_execution_report(self) -> Dict[str, Any]:
        """Generate execution report for audit."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(self._results),
            "success": sum(1 for r in self._results.values() if r.status == TaskStatus.SUCCESS),
            "failed": sum(1 for r in self._results.values() if r.status == TaskStatus.FAILED),
            "results": {tid: {"status": r.status.value, "artifacts": r.artifacts} for tid, r in self._results.items()}
        }
