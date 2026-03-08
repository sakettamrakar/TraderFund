from __future__ import annotations

import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .diagnosis_engine import Diagnosis


@dataclass(slots=True)
class RemediationAction:
    phase: str
    task: str
    action_id: str
    title: str
    description: str
    mode: str
    safe_to_apply: bool
    command: List[str] | None = None
    skill_name: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RemediationEngine:
    NEVER_TOUCH_PATTERNS = ("capital", "execution", "data/raw")

    def __init__(self, repo_root: str, available_skills: Iterable[str]):
        self.repo_root = Path(repo_root).resolve()
        self.available_skills = set(available_skills)

    def propose(self, diagnoses: Iterable[Diagnosis], metadata: Optional[Dict[str, Any]] = None) -> List[RemediationAction]:
        metadata = metadata or {}
        actions: List[RemediationAction] = []
        for diagnosis in diagnoses:
            actions.extend(self._actions_for_diagnosis(diagnosis, metadata))
        return actions

    def apply_safe_actions(self, actions: Iterable[RemediationAction], limit: int = 1) -> List[Dict[str, Any]]:
        applied: List[Dict[str, Any]] = []
        remaining = limit
        for action in actions:
            if remaining <= 0:
                break
            if not action.safe_to_apply:
                continue
            if action.mode == "command" and action.command:
                command_text = " ".join(action.command)
                if any(pattern in command_text for pattern in self.NEVER_TOUCH_PATTERNS):
                    continue
                result = subprocess.run(
                    action.command,
                    cwd=str(self.repo_root),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                applied.append(
                    {
                        "action_id": action.action_id,
                        "returncode": result.returncode,
                        "stdout": result.stdout[-2000:],
                        "stderr": result.stderr[-2000:],
                    }
                )
                remaining -= 1
            elif action.mode == "skill" and action.skill_name and action.skill_name in self.available_skills:
                result = subprocess.run(
                    [sys.executable, "bin/run-skill.py", action.skill_name, "--user", "validation-system"],
                    cwd=str(self.repo_root),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                applied.append(
                    {
                        "action_id": action.action_id,
                        "returncode": result.returncode,
                        "stdout": result.stdout[-2000:],
                        "stderr": result.stderr[-2000:],
                    }
                )
                remaining -= 1
        return applied

    def _actions_for_diagnosis(self, diagnosis: Diagnosis, metadata: Dict[str, Any]) -> List[RemediationAction]:
        phase = diagnosis.phase
        task = diagnosis.task
        actions: List[RemediationAction] = []

        if phase == "ingestion":
            if task in {"schema_validation", "null_handling"}:
                actions.append(
                    RemediationAction(
                        phase=phase,
                        task=task,
                        action_id="rebuild_intraday_canonical",
                        title="Rebuild canonical intraday layer",
                        description="Recompute processed intraday parquet from append-only raw candles.",
                        mode="command",
                        safe_to_apply=True,
                        command=[sys.executable, "processing/intraday_candles_processor.py"],
                    )
                )
            if "constraint-validator" in self.available_skills:
                actions.append(
                    RemediationAction(
                        phase=phase,
                        task=task,
                        action_id="skill_constraint_validator",
                        title="Run constraint validator skill",
                        description="Use desk skills to inspect schema and contract mismatches before a manual fix.",
                        mode="skill",
                        safe_to_apply=True,
                        skill_name="constraint-validator",
                    )
                )

        if phase == "research":
            if "cognitive-order-validator" in self.available_skills:
                actions.append(
                    RemediationAction(
                        phase=phase,
                        task=task,
                        action_id="skill_cognitive_order_validator",
                        title="Run cognitive order validator",
                        description="Use desk skills to inspect regime-gating and layer-order violations.",
                        mode="skill",
                        safe_to_apply=True,
                        skill_name="cognitive-order-validator",
                    )
                )

        if phase == "evaluation":
            profile = metadata.get("profile")
            if profile:
                actions.append(
                    RemediationAction(
                        phase=phase,
                        task=task,
                        action_id="rerun_evaluation_profile",
                        title="Rerun evaluation profile",
                        description="Regenerate evaluation artifacts for the bound profile.",
                        mode="command",
                        safe_to_apply=True,
                        command=[sys.executable, "src/evolution/pipeline_runner.py", str(profile)],
                    )
                )
            if "decision-ledger-curator" in self.available_skills:
                actions.append(
                    RemediationAction(
                        phase=phase,
                        task=task,
                        action_id="skill_decision_ledger_curator",
                        title="Run decision ledger curator",
                        description="Use desk skills to inspect evaluation/evolution ledger integrity.",
                        mode="skill",
                        safe_to_apply=True,
                        skill_name="decision-ledger-curator",
                    )
                )

        if phase == "dashboard" and "audit-log-viewer" in self.available_skills:
            actions.append(
                RemediationAction(
                    phase=phase,
                    task=task,
                    action_id="skill_audit_log_viewer",
                    title="Run audit log viewer",
                    description="Use desk skills to inspect provenance, freshness, and read-only failures through audit artifacts.",
                    mode="skill",
                    safe_to_apply=True,
                    skill_name="audit-log-viewer",
                )
            )

        return actions