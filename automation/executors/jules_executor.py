"""
Deterministic Jules executor plugin.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from automation.executors.base_executor import BaseExecutor, ExecutionResult
from automation.executors.jules_adapter import JulesExecutor as LegacyJulesExecutor
from automation.jules_supervisor.cli_api import jules_cli_available


class JulesExecutor(BaseExecutor):
    name = "JULES"
    mode = "AUTONOMOUS"

    def is_available(self) -> bool:
        api_key = (os.environ.get("JULES_API_KEY") or "").strip()
        if api_key:
            return True

        try:
            from automation.jules.config import JULES_API_KEY

            if (JULES_API_KEY or "").strip():
                return True
        except Exception:
            pass

        return jules_cli_available()

    def execute(self, action_plan: Dict[str, Any], run_context: Dict[str, Any]) -> ExecutionResult:
        run_dir = self._resolve_run_dir(run_context)
        run_dir.mkdir(parents=True, exist_ok=True)
        project_root = self._resolve_project_root(run_context)

        task_payload = dict(action_plan or {})
        task_payload.setdefault("task_id", run_context.get("task_id", run_context.get("run_id", "unknown")))

        legacy = LegacyJulesExecutor(project_root=Path(project_root))

        try:
            diff, logs = legacy.execute(task_payload, run_dir)
        except Exception as exc:
            return ExecutionResult(
                success=False,
                executor_name=self.name,
                artifacts_path=str(run_dir),
                error_message=str(exc),
            )

        (run_dir / "jules_executor.log").write_text(logs or "", encoding="utf-8")
        (run_dir / "jules_executor.diff.patch").write_text(diff or "", encoding="utf-8")

        log_lower = (logs or "").lower()
        failure_tokens = (
            "failed to submit",
            "polling failed",
            "failed to get results",
            "timed out",
            "timeout",
            "jules job failed",
        )
        failed = any(token in log_lower for token in failure_tokens)

        if failed and not (diff or "").strip():
            return ExecutionResult(
                success=False,
                executor_name=self.name,
                artifacts_path=str(run_dir),
                error_message=(logs or "Jules execution failed."),
            )

        return ExecutionResult(
            success=True,
            executor_name=self.name,
            artifacts_path=str(run_dir),
        )
