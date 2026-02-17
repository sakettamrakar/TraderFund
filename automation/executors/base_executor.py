"""
Standardized executor interface for deterministic routing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ExecutionResult:
    success: bool
    executor_name: str
    artifacts_path: Optional[str] = None
    error_message: Optional[str] = None


class BaseExecutor(ABC):
    """
    Standard base class for modular executor plugins.
    """

    name: str = "BASE"
    mode: str = "AUTONOMOUS"  # "AUTONOMOUS" | "HUMAN"

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else None

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def execute(self, action_plan: Dict[str, Any], run_context: Dict[str, Any]) -> ExecutionResult:
        pass

    def _resolve_project_root(self, run_context: Dict[str, Any]) -> Path:
        if self.project_root:
            return self.project_root
        ctx_root = run_context.get("project_root")
        if ctx_root:
            return Path(ctx_root)
        return Path(__file__).resolve().parents[2]

    def _resolve_run_dir(self, run_context: Dict[str, Any]) -> Path:
        run_dir = run_context.get("run_dir")
        if run_dir:
            return Path(run_dir)
        root = self._resolve_project_root(run_context)
        run_id = str(run_context.get("run_id", "temp"))
        return root / "automation" / "runs" / run_id
