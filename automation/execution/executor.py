import datetime
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from automation.execution.code_ops import CodeOps
from automation.execution.failure import FailureAnalyzer
from automation.execution.validation import ValidationPlanner, ValidationRunner
from automation.executors.registry import get_executor_by_name
from automation.router import TaskRouter

logger = logging.getLogger(__name__)


class TaskExecutor:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.code_ops = CodeOps(self.project_root)
        self.validation_planner = ValidationPlanner(self.project_root)
        self.validation_runner = ValidationRunner(self.project_root)
        self.router = TaskRouter(self.project_root)

        self.tasks_dir = self.project_root / "automation" / "tasks"
        self.runs_dir = self.project_root / "automation" / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def process_task(self, task_file: Path):
        """
        Executes a single task.
        """
        task_id = task_file.stem.replace("task_", "")
        logger.info("Processing task %s from %s", task_id, task_file.name)

        try:
            with open(task_file, "r", encoding="utf-8") as handle:
                task = json.load(handle)
        except Exception as exc:
            logger.error("Failed to load task file: %s", exc)
            return

        task["status"] = "ASSIGNED"
        self._update_task_file(task_file, task)

        run_id = f"{task_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        task["run_id"] = run_id
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        failure_analyzer = FailureAnalyzer(run_dir)
        executor_type = "UNKNOWN"
        reason = "Routing not performed"

        try:
            # 1. Routing
            executor_type, reason = self.router.route(task)
            logger.info("Routing decision for %s: %s (%s)", task_id, executor_type, reason)

            with open(run_dir / "routing.json", "w", encoding="utf-8") as handle:
                json.dump(
                    {"executor": executor_type, "reason": reason, "timestamp": time.time()},
                    handle,
                    indent=2,
                )

            # 2. Deterministic executor lookup (no fallback chain)
            executor = get_executor_by_name(
                executor_type,
                project_root=self.project_root,
                include_unavailable=True,
            )
            if executor is None:
                raise RuntimeError(f"Unknown executor type: {executor_type}")

            run_context = {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "task_id": task_id,
                "project_root": str(self.project_root),
                "escalation_reason": reason,
            }

            result = executor.execute(task, run_context)

            with open(run_dir / "execution_log.txt", "w", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "executor_name": result.executor_name,
                            "success": result.success,
                            "artifacts_path": result.artifacts_path,
                            "error_message": result.error_message,
                            "lifecycle_state": result.lifecycle_state,
                            "jules_task_id": result.jules_task_id,
                            "pr_url": result.pr_url,
                            "failure_reason": result.failure_reason,
                            "duration_seconds": result.duration_seconds,
                        },
                        indent=2,
                    )
                )

            # HUMAN_SUPERVISED is a controlled non-autonomous handoff, not a silent fallback.
            if executor.mode == "HUMAN":
                task["status"] = "HUMAN_REQUIRED"
                task["run_id"] = run_id
                self._update_task_file(task_file, task)
                logger.info("Task %s escalated to HUMAN_SUPERVISED.", task_id)
                return

            if not result.success:
                raise RuntimeError(result.error_message or f"{executor_type} execution failed")

            if executor_type == "JULES" and str(result.lifecycle_state or "").upper() == "PR_CREATED":
                gate_result = self._handle_jules_pr_control(
                    run_id=run_id,
                    run_dir=run_dir,
                    task=task,
                    result=result,
                )
                if not gate_result.get("success"):
                    raise RuntimeError(gate_result.get("reason") or "Pre-merge semantic gate failed.")

                task["status"] = "COMPLETE"
                task["run_id"] = run_id
                self._update_task_file(task_file, task)

                summary = {
                    "status": "SUCCESS",
                    "run_id": run_id,
                    "task_id": task.get("task_id"),
                    "executor": executor_type,
                    "lifecycle_state": result.lifecycle_state,
                    "jules_task_id": result.jules_task_id,
                    "pr_url": result.pr_url,
                    "merge_control": gate_result,
                }
                with open(run_dir / "summary.json", "w", encoding="utf-8") as handle:
                    json.dump(summary, handle, indent=2)

                logger.info("Task %s completed via Jules merge-control flow.", task_id)
                return

            # Capture diff for audit.
            diff = ""
            try:
                diff_proc = self.code_ops.generate_diffs()
                diff = diff_proc if isinstance(diff_proc, str) else ""
            except Exception:
                pass

            (run_dir / "diffs").mkdir(exist_ok=True)
            with open(run_dir / "diffs" / "changes.diff", "w", encoding="utf-8") as handle:
                handle.write(diff)

            modified_files = self.code_ops.get_changed_files()
            if not modified_files and not diff.strip():
                logger.warning("No files modified by %s.", executor_type)

            self._validate_and_finalize(task, task_file, run_dir, modified_files, executor_type)

        except Exception as exc:
            logger.error("Task %s FAILED: %s", task_id, exc)
            task["status"] = "FAILED"
            task["run_id"] = run_id
            self._update_task_file(task_file, task)

            extra_context = {"classification_reason": reason}
            failure_analyzer.generate_failure_tree(
                exc,
                task,
                f"Execution ({executor_type})",
                str(exc),
                extra_context=extra_context,
            )

    def _handle_jules_pr_control(self, run_id, run_dir, task, result):
        from automation.merge_controller import handle_pr_with_semantic

        pr_meta = self._load_json_file(run_dir / "jules_pr.json")
        test_summary = self._load_json_file(run_dir / "jules_test_summary.json")

        action_plan = task.get("action_plan", {})
        if not isinstance(action_plan, dict):
            action_plan = {}

        pr_info = {
            "pr_url": result.pr_url or pr_meta.get("pr_url"),
            "branch": pr_meta.get("branch"),
            "commit_sha": pr_meta.get("commit_sha"),
            "task_id": result.jules_task_id or pr_meta.get("task_id"),
            "action_plan": action_plan,
            "changed_files": task.get("changed_memory_files", []),
            "intent_source": (
                task.get("intent_file")
                or action_plan.get("objective")
                or task.get("purpose")
                or "Jules pre-merge semantic gate"
            ),
            "jules_context": {
                "jules_pr": pr_meta if isinstance(pr_meta, dict) else {},
                "jules_test_summary": test_summary if isinstance(test_summary, dict) else {},
            },
        }

        gate_result = handle_pr_with_semantic(run_id=run_id, pr_info=pr_info)
        with open(run_dir / "merge_control_result.json", "w", encoding="utf-8") as handle:
            json.dump(gate_result, handle, indent=2)
        return gate_result

    def _load_json_file(self, path: Path):
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                value = json.load(handle)
            if isinstance(value, dict):
                return value
        except Exception:
            pass
        return {}

    def _validate_and_finalize(self, task, task_file, run_dir, modified_files, executor_type):
        """
        Runs validation and updates task status.
        """
        plan = self.validation_planner.create_plan(modified_files)
        with open(run_dir / "validation_plan.json", "w", encoding="utf-8") as handle:
            json.dump(plan.to_dict(), handle, indent=2)

        success, output = self.validation_runner.run_unit_tests()
        with open(run_dir / "test_output.txt", "w", encoding="utf-8") as handle:
            handle.write(output)
        if not success:
            raise RuntimeError("Unit tests failed")

        success, output = self.validation_runner.check_domain_contracts(modified_files)
        with open(run_dir / "domain_validation.txt", "w", encoding="utf-8") as handle:
            handle.write(output)
        if not success:
            raise RuntimeError(f"Domain contract violation: {output}")

        success, output = self.validation_runner.run_semantic_validators(run_dir, plan)
        with open(run_dir / "semantic_validation_log.txt", "w", encoding="utf-8") as handle:
            handle.write(output)
        if not success:
            raise RuntimeError(f"Semantic validation failed: {output}")

        success, output = self.validation_runner.run_optional_validators(plan)
        with open(run_dir / "optional_validation.txt", "w", encoding="utf-8") as handle:
            handle.write(output)
        if not success:
            raise RuntimeError(f"Optional validation failed: {output}")

        task["status"] = "COMPLETE"
        task["run_id"] = run_id = run_dir.name
        self._update_task_file(task_file, task)

        summary = {
            "status": "SUCCESS",
            "run_id": run_id,
            "task_id": task.get("task_id"),
            "executor": executor_type,
            "modified_files": modified_files,
            "validations": plan.to_dict(),
        }
        with open(run_dir / "summary.json", "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)

        logger.info("Task %s COMPLETED successfully via %s.", task.get("task_id"), executor_type)

    def _update_task_file(self, task_file, task_data):
        try:
            with open(task_file, "w", encoding="utf-8") as handle:
                json.dump(task_data, handle, indent=2)
        except Exception as exc:
            logger.error("Failed to update task file %s: %s", task_file, exc)
