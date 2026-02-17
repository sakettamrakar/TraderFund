"""
Modular executor registry.

Router and task execution must resolve executors through this registry
instead of hard-coding class names.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from automation.executors.base_executor import BaseExecutor
from automation.executors.gemini_executor import GeminiExecutor
from automation.executors.human_executor import HumanSupervisedExecutor
from automation.executors.jules_executor import JulesExecutor

# Plugin registry (autonomous only). Add future executors here.
REGISTERED_EXECUTORS = [
    JulesExecutor(),
    GeminiExecutor(),
]


def _instantiate(template: BaseExecutor, project_root: Optional[Path] = None) -> BaseExecutor:
    cls = template.__class__
    return cls(project_root=project_root)


def get_registered_autonomous_executors(project_root: Optional[Path] = None) -> List[BaseExecutor]:
    return [_instantiate(executor, project_root=project_root) for executor in REGISTERED_EXECUTORS]


def get_available_autonomous_executors(project_root: Optional[Path] = None) -> List[BaseExecutor]:
    return [
        executor
        for executor in get_registered_autonomous_executors(project_root=project_root)
        if executor.mode == "AUTONOMOUS" and executor.is_available()
    ]


def get_human_executor(project_root: Optional[Path] = None) -> BaseExecutor:
    return HumanSupervisedExecutor(project_root=project_root)


def get_executor_by_name(
    name: str,
    project_root: Optional[Path] = None,
    include_unavailable: bool = False,
) -> Optional[BaseExecutor]:
    normalized = (name or "").strip().upper()
    if normalized in {"HUMAN", "HUMAN_SUPERVISED"}:
        return get_human_executor(project_root=project_root)

    for executor in get_registered_autonomous_executors(project_root=project_root):
        if executor.name.upper() != normalized:
            continue
        if include_unavailable or executor.is_available():
            return executor
        return None
    return None
