"""
Deterministic lifecycle definitions for Jules executor runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class JulesLifecycleState(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    PR_CREATED = "PR_CREATED"
    PR_MERGED = "PR_MERGED"
    PR_CLOSED = "PR_CLOSED"
    COMPLETED = "COMPLETED"
    TIMEOUT = "TIMEOUT"


@dataclass
class JulesExecutionContext:
    """
    SaaS-upgradeable context hooks (parameterized only).
    """

    tenant_id: str = "default"
    execution_context_id: str = ""
