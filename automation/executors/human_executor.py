"""
Human-supervised executor (non-LLM, non-autonomous).
"""

from __future__ import annotations

import json
from typing import Any, Dict

from automation.executors.base_executor import BaseExecutor, ExecutionResult


class HumanSupervisedExecutor(BaseExecutor):
    name = "HUMAN_SUPERVISED"
    mode = "HUMAN"

    def is_available(self) -> bool:
        return True

    def execute(self, action_plan: Dict[str, Any], run_context: Dict[str, Any]) -> ExecutionResult:
        run_dir = self._resolve_run_dir(run_context)
        run_dir.mkdir(parents=True, exist_ok=True)

        plan = action_plan.get("action_plan", action_plan)
        reason = (
            run_context.get("escalation_reason")
            or "Routed to HUMAN_SUPERVISED mode."
        )
        summary_path = run_dir / "human_required.txt"

        objective = plan.get("objective", "")
        target_components = plan.get("target_components", [])
        instructions = plan.get("detailed_instructions", [])

        summary_lines = [
            "HUMAN SUPERVISION REQUIRED",
            "==========================",
            f"Run ID: {run_context.get('run_id', 'unknown')}",
            f"Task ID: {run_context.get('task_id', 'unknown')}",
            "",
            "Reason for escalation:",
            reason,
            "",
            "Action Plan Summary:",
            f"Objective: {objective}",
            f"Target Components: {', '.join(target_components) if target_components else '(none)'}",
            "",
            "Instructions:",
        ]

        if instructions:
            summary_lines.extend([f"- {item}" for item in instructions])
        else:
            summary_lines.append("- (none)")

        summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

        # Keep a structured mirror for audit tooling.
        (run_dir / "human_required.json").write_text(
            json.dumps(
                {
                    "run_id": run_context.get("run_id"),
                    "task_id": run_context.get("task_id"),
                    "reason": reason,
                    "objective": objective,
                    "target_components": target_components,
                    "instructions": instructions,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        return ExecutionResult(
            success=False,
            executor_name=self.name,
            artifacts_path=str(summary_path),
            error_message=reason,
        )
