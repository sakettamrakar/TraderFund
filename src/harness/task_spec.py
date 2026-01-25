"""
Task Specification Type (L11 - Orchestration).
Defines the formal structure for harness-consumable tasks.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Lifecycle status of a task."""
    ACTIVE = "ACTIVE"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class TaskSpec(BaseModel):
    """
    Formal specification for a harness-executable task.
    
    Invariants:
    - task_id must be unique within the task graph.
    - depends_on must reference valid task_ids.
    - artifacts and impacts must be explicit paths.
    """
    task_id: str = Field(..., description="Unique identifier (e.g., 'OP-2.1')")
    status: TaskStatus = Field(default=TaskStatus.ACTIVE)
    dwbs_ref: str = Field(..., description="Reference to DWBS item (e.g., '4.2.1')")
    plane: str = Field(..., description="Plane scope (Control, Orchestration, Strategy, etc.)")
    blocking: bool = Field(default=True, description="If TRUE, failure halts execution")
    purpose: str = Field(..., description="Human-readable intent")
    
    # Dependencies
    inputs: List[str] = Field(default_factory=list, description="Required input files/states")
    depends_on: List[str] = Field(default_factory=list, description="Predecessor task IDs")
    
    # Outputs
    artifacts: List[str] = Field(default_factory=list, description="Files produced by this task")
    impacts: List[str] = Field(default_factory=list, description="Documents affected by this task")
    
    # Governance
    post_hooks: List[str] = Field(default_factory=list, description="Skills invoked after success")
    validator: Optional[str] = Field(default=None, description="Validator rules to apply")
    satisfies: List[str] = Field(default_factory=list, description="Obligation IDs this task satisfies")


def validate_task_spec(spec: TaskSpec) -> bool:
    """Validate a TaskSpec against basic integrity rules."""
    if not spec.task_id:
        return False
    if spec.blocking and not spec.purpose:
        return False
    return True
