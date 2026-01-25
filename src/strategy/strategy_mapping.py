"""
Strategy Mapping (L10 - Strategy).
Maps strategy definitions to task graphs for orchestration binding.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class StrategyDefinition(BaseModel):
    """
    Declarative strategy definition.
    
    Invariants:
    - Strategies declare intent, they do not compute state.
    - All dependencies are explicit references.
    - No executable logic permitted.
    """
    strategy_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Human-readable name")
    version: str = Field(..., description="Semantic version")
    owner: str = Field(..., description="Human author")
    
    # Epistemic dependencies (declarative only)
    required_beliefs: List[str] = Field(default_factory=list, description="Belief references required")
    required_factors: List[str] = Field(default_factory=list, description="Factor permissions required")
    regime_compatibility: List[str] = Field(default_factory=list, description="Permitted regime states")
    
    # Orchestration binding (reference only)
    task_graph_ref: str = Field(..., description="Reference to execution graph")
    decision_ledger_ref: str = Field(..., description="Authorizing decision")


class StrategyMapping:
    """
    Maps strategy definitions to their corresponding task graphs.
    
    This is a pure lookup structure—no computation, no inference.
    """
    
    def __init__(self):
        self._mappings: Dict[str, StrategyDefinition] = {}
    
    def register(self, definition: StrategyDefinition) -> None:
        """Register a strategy definition."""
        if definition.strategy_id in self._mappings:
            raise ValueError(f"Strategy already registered: {definition.strategy_id}")
        self._mappings[definition.strategy_id] = definition
    
    def get(self, strategy_id: str) -> Optional[StrategyDefinition]:
        """Retrieve a strategy definition by ID."""
        return self._mappings.get(strategy_id)
    
    def get_task_graph_ref(self, strategy_id: str) -> Optional[str]:
        """Get the task graph reference for a strategy."""
        defn = self._mappings.get(strategy_id)
        return defn.task_graph_ref if defn else None
    
    def list_all(self) -> List[str]:
        """List all registered strategy IDs."""
        return list(self._mappings.keys())
