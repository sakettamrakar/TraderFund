"""
Deterministic Jules executor with explicit lifecycle state machine.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
from pathlib import Path
from time import monotonic, sleep
from typing import Any, Dict, List, Optional, Tuple

from automation.automation_config import config
from automation.executors.base_executor import BaseExecutor, ExecutionResult
from automation.executors.jules_lifecycle import JulesExecutionContext, JulesLifecycleState
from automation.jules.adapter import JulesAdapter
from automation.jules_supervisor.artifact_collector import collect_jules_artifacts
from automation.jules_supervisor.cli_api import (
    jules_api_available,
    jules_cli_available,
    parse_cli_output,
    run_cli_command,
)
from automation.jules_supervisor.monitor import jules_status_details
from automation.jules_supervisor.pr_handler import detect_jules_pr, persist_jules_pr

logger = logging.getLogger(__name__)

EXECUTOR_VERSION = "jules-executor-lifecycle-v1"
DEFAULT_TIMEOUT_SECONDS = 1200
DEFAULT_POLL_INTERVAL_SECONDS = 20
DEFAULT_POLL_ERROR_THRESHOLD = 3
TASK_ID_RE = re.compile(r"\b(?:sessions|tasks)/[A-Za-z0-9._-]+\b")


class JulesExecutor(BaseExecutor):
    name = "JULES"
    mode = "AUTONOMOUS"

    def is_available(self) -> bool:
        api_key = (os.environ.get("JULES_API_KEY") or "").strip()
        if api_key:
            return True
        return jules_api_available() or jules_cli_available()

    def execute(self, action_plan: Dict[str, Any], run_context: Dict[str, Any]) -> ExecutionResult:
        run_dir = self._resolve_run_dir(run_context)
        run_dir.mkdir(parents=True, exist_ok=True)
        run_id = str(run_context.get("run_id", "unknown"))
        project_root = self._resolve_project_root(run_context)

        started = monotonic()
        policy = self._resolve_pr_policy()
        timeout_seconds = int(getattr(config, "JULES_POLL_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS))
        poll_interval = int(getattr(config, "JULES_POLL_INTERVAL_SECONDS", DEFAULT_POLL_INTERVAL_SECONDS))
        poll_error_threshold = int(getattr(config, "JULES_POLL_ERROR_THRESHOLD", DEFAULT_POLL_ERROR_THRESHOLD))

        exec_context = JulesExecutionContext(
            tenant_id=str(run_context.get("tenant_id", "default")),
            execution_context_id=str(
                run_context.get("execution_context_id")
                or run_context.get("run_id")
                or ""
            ),
        )

        task_payload = self._build_task_payload(action_plan, run_context)
        instruction_blob = self._build_instruction_blob(task_payload, project_root)
        poll_log: List[Dict[str, Any]] = []
        task_id: Optional[str] = None
        pr_metadata: Optional[Dict[str, Any]] = None
        terminal_state = JulesLifecycleState.FAILED
        failure_reason: Optional[str] = None

        # Always persist a creation artifact for deterministic run shape.
        self._write_json(
            run_dir / "jules_task.json",
            {
                "executor": self.name,
                "executor_version": EXECUTOR_VERSION,
                "state": JulesLifecycleState.CREATED.value,
                "task_id": None,
                "policy_used": policy,
                "tenant_id": exec_context.tenant_id,
                "execution_context_id": exec_context.execution_context_id,
                "payload_preview": {
                    "task_id": task_payload.get("task_id"),
                    "purpose": task_payload.get("purpose"),
                    "changed_memory_files": task_payload.get("changed_memory_files", []),
                },
            },
        )

        try:
            task_id, submit_source = self._create_task(
                task_payload=task_payload,
                instruction_blob=instruction_blob,
                run_dir=run_dir,
            )

            self._write_json(
                run_dir / "jules_task.json",
                {
                    "executor": self.name,
                    "executor_version": EXECUTOR_VERSION,
                    "state": JulesLifecycleState.CREATED.value,
                    "task_id": task_id,
                    "submit_source": submit_source,
                    "policy_used": policy,
                    "tenant_id": exec_context.tenant_id,
                    "execution_context_id": exec_context.execution_context_id,
                },
            )

            poll_result = self._poll_task(
                task_id=task_id,
                timeout_seconds=max(1, timeout_seconds),
                poll_interval=max(1, poll_interval),
                poll_error_threshold=max(1, poll_error_threshold),
            )
            poll_log = poll_result["poll_log"]
            terminal_state = poll_result["state"]
            failure_reason = poll_result.get("failure_reason")
            pr_metadata = poll_result.get("pr_metadata")

            if pr_metadata:
                pr_payload = dict(pr_metadata)
                pr_payload["task_id"] = task_id
                persist_jules_pr(run_id, pr_payload)

            if terminal_state == JulesLifecycleState.PR_CREATED and pr_metadata:
                state_after_policy, policy_failure = self._apply_pr_policy(
                    task_id=task_id,
                    pr_metadata=pr_metadata,
                    policy=policy,
                    run_dir=run_dir,
                )
                terminal_state = state_after_policy
                failure_reason = policy_failure or failure_reason

            self._write_json(run_dir / "jules_poll_log.json", poll_log)
            self._collect_artifacts(task_id=task_id, run_id=run_id, task_status=terminal_state.value)

            duration_seconds = round(monotonic() - started, 2)
            self._write_terminal_state(
                run_dir=run_dir,
                final_state=terminal_state,
                duration_seconds=duration_seconds,
                task_id=task_id,
                pr_url=(pr_metadata or {}).get("pr_url"),
                policy_used=policy,
                failure_reason=failure_reason,
            )

            success = self._is_success(terminal_state, policy)
            return ExecutionResult(
                success=success,
                executor_name=self.name,
                artifacts_path=str(run_dir),
                error_message=None if success else (failure_reason or terminal_state.value),
                lifecycle_state=terminal_state.value,
                jules_task_id=task_id,
                pr_url=(pr_metadata or {}).get("pr_url"),
                failure_reason=failure_reason,
                duration_seconds=duration_seconds,
            )

        except Exception as exc:
            failure_reason = str(exc)
            terminal_state = JulesLifecycleState.FAILED
            duration_seconds = round(monotonic() - started, 2)

            if task_id:
                self._collect_artifacts(task_id=task_id, run_id=run_id, task_status=terminal_state.value)

            self._write_json(run_dir / "jules_poll_log.json", poll_log)
            self._write_terminal_state(
                run_dir=run_dir,
                final_state=terminal_state,
                duration_seconds=duration_seconds,
                task_id=task_id,
                pr_url=(pr_metadata or {}).get("pr_url"),
                policy_used=policy,
                failure_reason=failure_reason,
            )

            return ExecutionResult(
                success=False,
                executor_name=self.name,
                artifacts_path=str(run_dir),
                error_message=failure_reason,
                lifecycle_state=terminal_state.value,
                jules_task_id=task_id,
                pr_url=(pr_metadata or {}).get("pr_url"),
                failure_reason=failure_reason,
                duration_seconds=duration_seconds,
            )

    def _build_task_payload(
        self,
        action_plan: Dict[str, Any],
        run_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = dict(action_plan or {})
        payload.setdefault("task_id", run_context.get("task_id", run_context.get("run_id", "unknown")))
        if "action_plan" not in payload and isinstance(action_plan, dict):
            payload["action_plan"] = action_plan.get("action_plan", {})
        return payload

    def _build_instruction_blob(self, task_payload: Dict[str, Any], project_root: Path) -> str:
        lines: List[str] = []
        action_plan = task_payload.get("action_plan", {})
        if isinstance(action_plan, dict):
            objective = action_plan.get("objective")
            if objective:
                lines.append(f"Objective: {objective}")
            instructions = action_plan.get("detailed_instructions", [])
            if isinstance(instructions, list) and instructions:
                lines.append("Instructions:")
                for entry in instructions:
                    lines.append(f"- {entry}")

        changed_files = task_payload.get("changed_memory_files", [])
        if isinstance(changed_files, list):
            for relative_path in changed_files:
                path = project_root / str(relative_path)
                if not path.exists():
                    continue
                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                lines.append("")
                lines.append(f"### FILE: {relative_path}")
                lines.append(content)

        if not lines:
            lines.append(json.dumps(task_payload, indent=2, default=str))
        return "\n".join(lines)

    def _create_task(
        self,
        task_payload: Dict[str, Any],
        instruction_blob: str,
        run_dir: Path,
    ) -> Tuple[str, str]:
        if jules_api_available():
            adapter = JulesAdapter()
            payload = adapter.create_job(task_payload, instruction_blob)
            task_id = adapter.submit_job(payload)
            if not isinstance(task_id, str) or not task_id.strip():
                raise RuntimeError("Jules API returned empty task id.")
            return task_id.strip(), "API"

        if jules_cli_available():
            task_id = self._create_task_cli(task_payload, instruction_blob, run_dir)
            return task_id, "CLI"

        raise RuntimeError("Jules is unavailable: neither API credentials nor CLI were found.")

    def _create_task_cli(
        self,
        task_payload: Dict[str, Any],
        instruction_blob: str,
        run_dir: Path,
    ) -> str:
        payload = {
            "task": task_payload,
            "instructions": instruction_blob,
        }
        payload_path = run_dir / "jules_submit_payload.json"
        payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        commands = [
            ["jules", "create-task", "--input", str(payload_path), "--json"],
            ["jules", "task", "create", "--input", str(payload_path), "--json"],
            ["jules", "submit", "--input", str(payload_path), "--json"],
        ]
        errors: List[str] = []
        for command in commands:
            result = run_cli_command(command, timeout=120)
            if not result.get("ok"):
                errors.append(result.get("stderr") or f"returncode={result.get('returncode')}")
                continue
            task_id = self._extract_task_id(result.get("stdout", ""))
            if task_id:
                return task_id
            errors.append("CLI returned success but no task id was found in output.")

        raise RuntimeError(f"Jules CLI task creation failed: {' | '.join(errors)}")

    def _extract_task_id(self, stdout: str) -> Optional[str]:
        parsed = parse_cli_output(stdout or "")
        if isinstance(parsed, dict):
            for key in ("task_id", "id", "name", "session", "task"):
                value = parsed.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

            items = parsed.get("items")
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    value = item.get("task_id") or item.get("id") or item.get("name")
                    if isinstance(value, str) and value.strip():
                        return value.strip()

        match = TASK_ID_RE.search(stdout or "")
        if match:
            return match.group(0)
        return None

    def _poll_task(
        self,
        task_id: str,
        timeout_seconds: int,
        poll_interval: int,
        poll_error_threshold: int,
    ) -> Dict[str, Any]:
        started = monotonic()
        poll_index = 0
        poll_errors = 0
        poll_log: List[Dict[str, Any]] = []

        while monotonic() - started < timeout_seconds:
            poll_index += 1
            status_record = jules_status_details(task_id)
            if not isinstance(status_record, dict):
                return {
                    "state": JulesLifecycleState.FAILED,
                    "poll_log": poll_log,
                    "failure_reason": "Jules status response was non-structured.",
                    "pr_metadata": None,
                }

            mapped_state = self._map_status_to_lifecycle(status_record.get("status"))
            status_error = status_record.get("error")

            if status_error:
                poll_errors += 1
            elif mapped_state is None:
                poll_errors += 1

            entry = {
                "poll_index": poll_index,
                "elapsed_seconds": round(monotonic() - started, 2),
                "status": status_record.get("status"),
                "raw_status": status_record.get("raw_status"),
                "mapped_state": mapped_state.value if mapped_state else "UNKNOWN",
                "source": status_record.get("source"),
                "error": status_error,
                "error_count": poll_errors,
            }

            pr_metadata = None
            try:
                pr_metadata = detect_jules_pr(task_id)
            except Exception as exc:
                poll_errors += 1
                entry["pr_detection_error"] = str(exc)

            if pr_metadata:
                entry["pr_detected"] = True
                entry["pr_url"] = pr_metadata.get("pr_url")
                if not pr_metadata.get("branch"):
                    poll_log.append(entry)
                    return {
                        "state": JulesLifecycleState.FAILED,
                        "poll_log": poll_log,
                        "failure_reason": "PR was created but branch metadata is missing.",
                        "pr_metadata": pr_metadata,
                    }

                poll_log.append(entry)
                return {
                    "state": JulesLifecycleState.PR_CREATED,
                    "poll_log": poll_log,
                    "failure_reason": None,
                    "pr_metadata": pr_metadata,
                }

            poll_log.append(entry)

            if poll_errors > poll_error_threshold:
                return {
                    "state": JulesLifecycleState.FAILED,
                    "poll_log": poll_log,
                    "failure_reason": (
                        f"Polling error threshold exceeded ({poll_errors} > {poll_error_threshold})."
                    ),
                    "pr_metadata": None,
                }

            if mapped_state == JulesLifecycleState.FAILED:
                return {
                    "state": JulesLifecycleState.FAILED,
                    "poll_log": poll_log,
                    "failure_reason": status_error or "Jules task reported FAILED status.",
                    "pr_metadata": None,
                }
            if mapped_state == JulesLifecycleState.TIMEOUT:
                return {
                    "state": JulesLifecycleState.TIMEOUT,
                    "poll_log": poll_log,
                    "failure_reason": status_error or "Jules task reported TIMED_OUT status.",
                    "pr_metadata": None,
                }
            if mapped_state == JulesLifecycleState.COMPLETED:
                return {
                    "state": JulesLifecycleState.COMPLETED,
                    "poll_log": poll_log,
                    "failure_reason": None,
                    "pr_metadata": None,
                }

            sleep(poll_interval)

        return {
            "state": JulesLifecycleState.TIMEOUT,
            "poll_log": poll_log,
            "failure_reason": f"Polling timed out after {timeout_seconds} seconds.",
            "pr_metadata": None,
        }

    def _map_status_to_lifecycle(self, status: Any) -> Optional[JulesLifecycleState]:
        token = str(status or "").upper().replace("-", "_").replace(" ", "_")
        if token in {"QUEUED", "PENDING"}:
            return JulesLifecycleState.QUEUED
        if token in {"RUNNING", "IN_PROGRESS"}:
            return JulesLifecycleState.RUNNING
        if token in {"FAILED", "ERROR", "CANCELLED"}:
            return JulesLifecycleState.FAILED
        if token in {"TIMED_OUT", "TIMEOUT"}:
            return JulesLifecycleState.TIMEOUT
        if token in {"COMPLETED", "DONE", "SUCCESS", "SUCCEEDED"}:
            return JulesLifecycleState.COMPLETED
        return None

    def _apply_pr_policy(
        self,
        task_id: str,
        pr_metadata: Dict[str, Any],
        policy: str,
        run_dir: Path,
    ) -> Tuple[JulesLifecycleState, Optional[str]]:
        if policy == "WAIT_FOR_SEMANTIC":
            return JulesLifecycleState.PR_CREATED, None

        if policy == "MANUAL_REVIEW":
            (run_dir / "manual_review_required.txt").write_text(
                f"Task {task_id} requires manual PR review.\nPR: {pr_metadata.get('pr_url', '')}\n",
                encoding="utf-8",
            )
            return JulesLifecycleState.PR_CLOSED, "Manual review required by policy."

        if policy == "AUTO_MERGE":
            pr_url = str(pr_metadata.get("pr_url") or "")
            if not pr_url:
                return JulesLifecycleState.FAILED, "AUTO_MERGE policy requires pr_url."

            if shutil.which("gh") is None:
                return JulesLifecycleState.FAILED, "AUTO_MERGE policy requires GitHub CLI (gh)."

            merge = run_cli_command(
                ["gh", "pr", "merge", pr_url, "--merge", "--delete-branch"],
                timeout=180,
            )
            if merge.get("ok"):
                return JulesLifecycleState.PR_MERGED, None

            stderr = (merge.get("stderr") or "").strip()
            stdout = (merge.get("stdout") or "").strip()
            combined = " ".join([stdout, stderr]).strip().lower()
            if "already merged" in combined:
                return JulesLifecycleState.PR_MERGED, None

            return JulesLifecycleState.FAILED, stderr or stdout or "AUTO_MERGE failed."

        return JulesLifecycleState.FAILED, f"Unsupported Jules PR policy: {policy}"

    def _resolve_pr_policy(self) -> str:
        raw = str(getattr(config, "JULES_PR_POLICY", "WAIT_FOR_SEMANTIC")).strip().upper()
        allowed = {"WAIT_FOR_SEMANTIC", "AUTO_MERGE", "MANUAL_REVIEW"}
        if raw not in allowed:
            return "WAIT_FOR_SEMANTIC"
        return raw

    def _collect_artifacts(self, task_id: str, run_id: str, task_status: str) -> None:
        try:
            collect_jules_artifacts(task_id=task_id, run_id=run_id, task_status=task_status)
        except Exception as exc:
            logger.warning("Artifact collection failed for task %s: %s", task_id, exc)

    def _write_terminal_state(
        self,
        run_dir: Path,
        final_state: JulesLifecycleState,
        duration_seconds: float,
        task_id: Optional[str],
        pr_url: Optional[str],
        policy_used: str,
        failure_reason: Optional[str],
    ) -> None:
        payload = {
            "final_state": final_state.value,
            "duration": duration_seconds,
            "task_id": task_id,
            "pr_url": pr_url,
            "executor_version": EXECUTOR_VERSION,
            "policy_used": policy_used,
            "failure_reason": failure_reason,
        }
        self._write_json(run_dir / "jules_terminal_state.json", payload)

    def _is_success(self, terminal_state: JulesLifecycleState, policy: str) -> bool:
        if terminal_state in {JulesLifecycleState.FAILED, JulesLifecycleState.TIMEOUT, JulesLifecycleState.PR_CLOSED}:
            return False
        if terminal_state == JulesLifecycleState.PR_CREATED and policy == "MANUAL_REVIEW":
            return False
        return terminal_state in {
            JulesLifecycleState.COMPLETED,
            JulesLifecycleState.PR_CREATED,
            JulesLifecycleState.PR_MERGED,
        }

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
