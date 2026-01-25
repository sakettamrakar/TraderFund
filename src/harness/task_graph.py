"""
Task Graph Model (L11 - Orchestration).
Implements DAG structure for deterministic task sequencing.
"""
from typing import List, Dict, Set, Optional
from collections import deque
from .task_spec import TaskSpec, TaskStatus


class TaskGraph:
    """
    Directed Acyclic Graph for task orchestration.
    
    Invariants:
    - No cycles allowed (validated on add).
    - Execution order is deterministic (topological sort).
    - Partial execution must be explicit via selectors.
    """
    
    def __init__(self):
        self._tasks: Dict[str, TaskSpec] = {}
        self._edges: Dict[str, Set[str]] = {}  # task_id -> set of dependents
    
    def add_task(self, spec: TaskSpec) -> None:
        """Add a task to the graph."""
        if spec.task_id in self._tasks:
            raise ValueError(f"Duplicate task_id: {spec.task_id}")
        
        self._tasks[spec.task_id] = spec
        self._edges[spec.task_id] = set()
        
        # Register edges from dependencies
        for dep_id in spec.depends_on:
            if dep_id not in self._edges:
                self._edges[dep_id] = set()
            self._edges[dep_id].add(spec.task_id)
    
    def get_task(self, task_id: str) -> Optional[TaskSpec]:
        """Retrieve a task by ID."""
        return self._tasks.get(task_id)
    
    def get_execution_order(self) -> List[str]:
        """
        Return deterministic topological order of tasks.
        Identical input state = identical output sequence.
        """
        in_degree: Dict[str, int] = {tid: 0 for tid in self._tasks}
        
        for spec in self._tasks.values():
            for dep_id in spec.depends_on:
                if dep_id in in_degree:
                    in_degree[spec.task_id] += 1
        
        # Kahn's algorithm with stable sort for determinism
        queue = deque(sorted([tid for tid, deg in in_degree.items() if deg == 0]))
        result: List[str] = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for dependent in sorted(self._edges.get(current, [])):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self._tasks):
            raise ValueError("Cycle detected in task graph")
        
        return result
    
    def select_range(self, from_task: str, to_task: str) -> List[str]:
        """Select tasks in range [from_task, to_task] inclusive."""
        order = self.get_execution_order()
        try:
            start_idx = order.index(from_task)
            end_idx = order.index(to_task)
            return order[start_idx:end_idx + 1]
        except ValueError as e:
            raise ValueError(f"Invalid range: {e}")
    
    def select_prefix(self, prefix: str) -> List[str]:
        """Select all tasks matching a prefix (e.g., 'OP-2')."""
        order = self.get_execution_order()
        return [tid for tid in order if tid.startswith(prefix)]
