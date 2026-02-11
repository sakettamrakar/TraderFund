import json
import logging
import time
import datetime
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from automation.workers.manager import WorkerManager
from automation.workers.router import AccountRouter
from automation.execution.code_ops import CodeOps
from automation.execution.validation import ValidationPlanner, ValidationRunner
from automation.execution.failure import FailureAnalyzer
from automation.router import TaskRouter
from automation.jules.adapter import JulesAdapter

logger = logging.getLogger(__name__)

class TaskExecutor:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.worker_manager = WorkerManager()
        self.account_router = AccountRouter()
        self.code_ops = CodeOps(self.project_root)
        self.validation_planner = ValidationPlanner(self.project_root)
        self.validation_runner = ValidationRunner(self.project_root)
        self.router = TaskRouter(self.project_root)
        self.jules_adapter = JulesAdapter()

        self.tasks_dir = self.project_root / "automation" / "tasks"
        self.runs_dir = self.project_root / "automation" / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def process_task(self, task_file: Path):
        """
        Executes a single task.
        """
        task_id = task_file.stem.replace("task_", "")
        logger.info(f"Processing task {task_id} from {task_file.name}")

        try:
            with open(task_file, 'r') as f:
                task = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load task file: {e}")
            return

        # 1. Assign Task
        task["status"] = "ASSIGNED"
        self._update_task_file(task_file, task)

        # Create Run Directory
        run_id = f"{task_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        failure_analyzer = FailureAnalyzer(run_dir)
        executor_type = "UNKNOWN"
        reason = "Routing not performed"

        try:
            # 2. Routing
            executor_type, reason = self.router.route(task)
            logger.info(f"Routing decision for {task_id}: {executor_type} ({reason})")

            with open(run_dir / "routing.json", "w") as f:
                json.dump({"executor": executor_type, "reason": reason, "timestamp": time.time()}, f)

            modified_files = []

            # 3. Execution
            if executor_type == "JULES":
                modified_files = self._execute_jules(task, run_dir)
            else:
                modified_files = self._execute_ag(task, run_dir)

            # 4. Validation & Finalization
            self._validate_and_finalize(task, task_file, run_dir, modified_files, executor_type)

        except Exception as e:
            logger.error(f"Task {task_id} FAILED: {e}")
            task["status"] = "FAILED"
            task["run_id"] = run_id
            self._update_task_file(task_file, task)

            extra_context = {"classification_reason": reason}
            failure_analyzer.generate_failure_tree(e, task, f"Execution ({executor_type})", str(e), extra_context=extra_context)

            # Optional: Revert changes on failure?
            # self.code_ops.reset_changes()

    def _execute_ag(self, task, run_dir) -> list:
        """
        Executes task using Antigravity (Local Worker + CodeOps).
        """
        worker = None
        try:
            # Allocate Worker
            profile_path = self.account_router.get_next_profile_path()
            logger.info(f"Allocating worker with profile {profile_path}")
            worker = self.worker_manager.launch_worker(profile_path, headless=True)

            # Code Ops
            memory_files = task.get("changed_memory_files", [])
            changes = self.code_ops.infer_changes(memory_files)

            if not changes:
                logger.warning("No code changes inferred from memory files.")

            modified_files = self.code_ops.apply_changes(changes)

            # Generate Tests if missing
            for f in modified_files:
                 if f.endswith(".py"):
                     self.code_ops.generate_test_if_missing(f)

            # Generate Diffs
            diff_output = self.code_ops.generate_diffs()
            (run_dir / "diffs").mkdir(exist_ok=True)
            with open(run_dir / "diffs" / "changes.diff", "w") as f:
                f.write(diff_output)

            return modified_files

        finally:
            if worker:
                worker.close()

    def _execute_jules(self, task, run_dir) -> list:
        """
        Executes task using Jules Batch Backend.
        """
        # Prepare instructions
        changed_files = task.get("changed_memory_files", [])
        instructions = ""
        for f in changed_files:
            path = self.project_root / f
            if path.exists():
                instructions += f"### FILE: {f}\n{path.read_text()}\n"

        # Submit Job
        payload = self.jules_adapter.create_job(task, instructions)
        job_id = self.jules_adapter.submit_job(payload)

        # Poll Job
        status = self.jules_adapter.poll_job(job_id)

        # Get Results (even if failed, to get logs)
        results = {}
        try:
            results = self.jules_adapter.get_results(job_id)
        except Exception as e:
            logger.warning(f"Failed to fetch results for job {job_id}: {e}")

        if status == "FAILED":
            error_msg = results.get("logs", "No logs provided")
            raise RuntimeError(f"Jules job {job_id} failed. Logs: {error_msg}")

        # Save Results
        with open(run_dir / "jules_result.json", "w") as f:
            json.dump(results, f, indent=2)

        # Apply Diff
        diff_content = results.get("diff", "")
        success = self.code_ops.apply_diff(diff_content)

        if not success:
            raise RuntimeError("Failed to apply Jules diff.")

        # Determine modified files using git diff --name-only
        modified_files = self.code_ops.get_changed_files()

        # Save the applied diff to run_dir/diffs
        current_diff = self.code_ops.generate_diffs()
        (run_dir / "diffs").mkdir(exist_ok=True)
        with open(run_dir / "diffs" / "changes.diff", "w") as f:
            f.write(current_diff)

        return modified_files

    def _validate_and_finalize(self, task, task_file, run_dir, modified_files, executor_type):
        """
        Runs validation and updates task status.
        """
        # Validation Planning
        plan = self.validation_planner.create_plan(modified_files)
        with open(run_dir / "validation_plan.json", "w") as f:
            json.dump(plan.to_dict(), f, indent=2)

        # Validation Execution
        # A. Unit Tests (Mandatory)
        success, output = self.validation_runner.run_unit_tests()
        with open(run_dir / "test_output.txt", "w") as f:
            f.write(output)

        if not success:
            raise RuntimeError("Unit tests failed")

        # B. Domain Contracts (Mandatory)
        success, output = self.validation_runner.check_domain_contracts(modified_files)
        with open(run_dir / "domain_validation.txt", "w") as f:
            f.write(output)

        if not success:
            raise RuntimeError(f"Domain contract violation: {output}")

        # C. Phase Q Semantic Validators (REQUIRED)
        success, output = self.validation_runner.run_semantic_validators(run_dir, plan)
        with open(run_dir / "semantic_validation_log.txt", "w") as f:
            f.write(output)

        if not success:
            raise RuntimeError(f"Semantic validation failed: {output}")

        # D. Optional Validators
        success, output = self.validation_runner.run_optional_validators(plan)
        with open(run_dir / "optional_validation.txt", "w") as f:
            f.write(output)

        if not success:
             raise RuntimeError(f"Optional validation failed: {output}")

        # Success
        task["status"] = "COMPLETE"
        task["run_id"] = run_id = run_dir.name
        self._update_task_file(task_file, task)

        # Summary
        summary = {
            "status": "SUCCESS",
            "run_id": run_id,
            "task_id": task.get("task_id"),
            "executor": executor_type,
            "modified_files": modified_files,
            "validations": plan.to_dict()
        }
        with open(run_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Task {task.get('task_id')} COMPLETED successfully via {executor_type}.")

    def _update_task_file(self, task_file, task_data):
        try:
            with open(task_file, 'w') as f:
                json.dump(task_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update task file {task_file}: {e}")
