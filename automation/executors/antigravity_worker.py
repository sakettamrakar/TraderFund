import time
import subprocess
import logging
import json
from pathlib import Path
from typing import Tuple, Dict, Any

from automation.executors.base import BaseExecutor
from automation.workers.manager import WorkerManager
from automation.workers.router import AccountRouter

logger = logging.getLogger(__name__)

class AntigravityExecutor(BaseExecutor):
    def __init__(self, project_root: Path):
        super().__init__(project_root)
        self.worker_manager = WorkerManager()
        self.account_router = AccountRouter()

    def execute(self, task: Dict[str, Any], run_dir: Path) -> Tuple[str, str]:
        """
        Executes task using Antigravity Worker (Playwright).
        """
        logger.info("Executing task via Antigravity Worker...")

        # 1. Select Profile
        # Ensure profiles directory exists
        (self.project_root / "automation" / "profiles").mkdir(parents=True, exist_ok=True)

        profile_path = self.account_router.get_next_profile_path()
        logger.info(f"Selected profile: {profile_path}")

        # 2. Launch Worker
        worker = None
        try:
            # Launch visibly as requested
            worker = self.worker_manager.launch_worker(profile_path, headless=False)

            # 3. Paste Action Plan
            # Since we can't reliably automate the UI interactions without knowing selectors,
            # we will simulate the "paste" by logging and writing to a file in the repo root
            # that the "human" or "worker" would see.
            action_plan_file = self.project_root / "current_action_plan.json"
            with open(action_plan_file, "w") as f:
                json.dump(task, f, indent=2)

            logger.info(f"Action plan written to {action_plan_file}")

            # Navigate to repo (already done in launch_worker but good to confirm)
            try:
                worker.page.goto(f"file://{self.project_root}")
            except Exception as e:
                logger.warning(f"Failed to navigate to repo: {e}")

            # Try to find chat input (heuristic)
            try:
                # Common selectors for chat inputs
                selectors = ["textarea", "input[type='text']", "[contenteditable]"]
                found_input = False
                for selector in selectors:
                    if worker.page.is_visible(selector):
                        worker.page.fill(selector, f"Execute task: {task.get('task_id')}")
                        worker.page.press(selector, "Enter")
                        logger.info(f"Pasted command into {selector}")
                        found_input = True
                        break
                if not found_input:
                    logger.info("No chat input found (expected if no UI extension installed). Waiting for manual/external changes.")
            except Exception as e:
                logger.warning(f"Could not interact with page UI: {e}")

            # 4. Wait for Code Changes
            logger.info("Waiting for code changes...")
            start_diff = self._get_git_diff()

            # Wait loop
            timeout = 300 # 5 minutes max
            start_time = time.time()
            changed = False

            while (time.time() - start_time) < timeout:
                current_diff = self._get_git_diff()
                if current_diff != start_diff:
                    logger.info("Changes detected!")
                    changed = True
                    # Wait for stability (e.g. 5 seconds of no further changes)
                    stability_start = time.time()
                    last_stable_diff = current_diff
                    while (time.time() - stability_start) < 5:
                        time.sleep(1)
                        check_diff = self._get_git_diff()
                        if check_diff != last_stable_diff:
                            logger.info("More changes detected, resetting stability timer.")
                            last_stable_diff = check_diff
                            stability_start = time.time()

                    break
                time.sleep(2)

            if not changed:
                logger.warning("No code changes detected within timeout.")
                return "", "Timeout: No changes detected."

            # 5. Return Diff + Logs
            final_diff = self._get_git_diff()
            logs = "Antigravity execution completed."

            # Cleanup temporary action plan file
            if action_plan_file.exists():
                action_plan_file.unlink()

            return final_diff, logs

        except Exception as e:
            logger.error(f"Antigravity execution failed: {e}")
            return "", f"Error: {e}"
        finally:
            if worker:
                worker.close()

    def _get_git_diff(self) -> str:
        try:
            result = subprocess.run(
                ["git", "diff"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception:
            return ""
