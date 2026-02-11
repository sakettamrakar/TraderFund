import json
import logging
import time
import uuid
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

logger = logging.getLogger(__name__)

class TaskExecutor:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.worker_manager = WorkerManager()
        self.account_router = AccountRouter()
        self.code_ops = CodeOps(self.project_root)
        self.validation_planner = ValidationPlanner(self.project_root)
        self.validation_runner = ValidationRunner(self.project_root)

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
        worker = None

        try:
            # 2. Allocate Worker
            profile_path = self.account_router.get_next_profile_path()
            logger.info(f"Allocating worker with profile {profile_path}")
            worker = self.worker_manager.launch_worker(profile_path, headless=True)

            # 3. Execution (Code Ops)
            memory_files = task.get("changed_memory_files", [])
            changes = self.code_ops.infer_changes(memory_files)

            if not changes:
                logger.warning("No code changes inferred from memory files.")
                # Could be a research task, but for now we proceed

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

            # 4. Validation Planning
            plan = self.validation_planner.create_plan(modified_files)
            with open(run_dir / "validation_plan.json", "w") as f:
                json.dump(plan.to_dict(), f, indent=2)

            # 5. Validation Execution
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

            # C. Optional Validators
            success, output = self.validation_runner.run_optional_validators(plan)
            with open(run_dir / "optional_validation.txt", "w") as f:
                f.write(output)

            if not success:
                 raise RuntimeError(f"Optional validation failed: {output}")

            # 6. Success
            task["status"] = "COMPLETE"
            task["run_id"] = run_id
            self._update_task_file(task_file, task)

            # Summary
            summary = {
                "status": "SUCCESS",
                "run_id": run_id,
                "task_id": task_id,
                "modified_files": modified_files,
                "validations": plan.to_dict()
            }
            with open(run_dir / "summary.json", "w") as f:
                json.dump(summary, f, indent=2)

            logger.info(f"Task {task_id} COMPLETED successfully.")

        except Exception as e:
            logger.error(f"Task {task_id} FAILED: {e}")
            task["status"] = "FAILED"
            task["run_id"] = run_id
            self._update_task_file(task_file, task)

            failure_analyzer.generate_failure_tree(e, task, "Execution/Validation", str(e))

            # Revert changes? Maybe not, keep for inspection
            # self.code_ops.reset_changes()

        finally:
            if worker:
                worker.close()

    def _update_task_file(self, task_file, task_data):
        try:
            with open(task_file, 'w') as f:
                json.dump(task_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update task file {task_file}: {e}")
