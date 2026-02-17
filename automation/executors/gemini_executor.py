"""
Deterministic Gemini executor plugin.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict

from automation.executors.base_executor import BaseExecutor, ExecutionResult
from automation.executors.gemini_fallback import (
    GEMINI_PATH,
    GeminiExecutor as LegacyGeminiExecutor,
)


class GeminiExecutor(BaseExecutor):
    name = "GEMINI"
    mode = "AUTONOMOUS"

    def is_available(self) -> bool:
        if os.environ.get("MOCK_GEMINI"):
            return True

        configured = (os.environ.get("GEMINI_CLI_PATH") or "").strip()
        if configured:
            if Path(configured).exists():
                return True
            if shutil.which(configured):
                return True

        if GEMINI_PATH and Path(str(GEMINI_PATH)).exists():
            return True

        return shutil.which("gemini") is not None

    def execute(self, action_plan: Dict[str, Any], run_context: Dict[str, Any]) -> ExecutionResult:
        run_dir = self._resolve_run_dir(run_context)
        run_dir.mkdir(parents=True, exist_ok=True)
        project_root = self._resolve_project_root(run_context)

        task_payload = dict(action_plan or {})
        task_payload.setdefault("task_id", run_context.get("task_id", run_context.get("run_id", "unknown")))

        legacy = LegacyGeminiExecutor(project_root=Path(project_root))

        try:
            diff, logs = legacy.execute(task_payload, run_dir)
        except Exception as exc:
            return ExecutionResult(
                success=False,
                executor_name=self.name,
                artifacts_path=str(run_dir),
                error_message=str(exc),
            )

        (run_dir / "gemini_executor.log").write_text(logs or "", encoding="utf-8")
        (run_dir / "gemini_executor.diff.patch").write_text(diff or "", encoding="utf-8")

        failed = "execution failed" in (logs or "").lower()
        if failed and not (diff or "").strip():
            return ExecutionResult(
                success=False,
                executor_name=self.name,
                artifacts_path=str(run_dir),
                error_message=logs or "Gemini execution failed.",
            )

        return ExecutionResult(
            success=True,
            executor_name=self.name,
            artifacts_path=str(run_dir),
        )
