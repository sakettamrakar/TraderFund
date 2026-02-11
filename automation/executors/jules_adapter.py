import re
import requests
import logging
import json
from pathlib import Path
from typing import Tuple, Dict, Any

from automation.executors.base import BaseExecutor
from automation.jules.adapter import JulesAdapter
from automation.execution.code_ops import CodeOps

logger = logging.getLogger(__name__)

class JulesExecutor(BaseExecutor):
    def __init__(self, project_root: Path):
        super().__init__(project_root)
        self.adapter = JulesAdapter()
        self.code_ops = CodeOps(project_root)

    def execute(self, task: Dict[str, Any], run_dir: Path) -> Tuple[str, str]:
        logger.info("Executing task via Jules Batch Backend...")

        # 1. Prepare Instructions
        changed_files = task.get("changed_memory_files", [])
        instructions = ""
        for f in changed_files:
            path = self.project_root / f
            if path.exists():
                instructions += f"### FILE: {f}\n{path.read_text()}\n"

        # 2. Submit Job
        try:
            payload = self.adapter.create_job(task, instructions)
            job_id = self.adapter.submit_job(payload)
        except Exception as e:
            return "", f"Failed to submit Jules job: {e}"

        # 3. Poll
        status = "UNKNOWN"
        try:
            status = self.adapter.poll_job(job_id)
        except Exception as e:
            logger.error(f"Jules polling failed: {e}")
            return "", f"Polling failed: {e}"

        # 4. Get Results
        try:
            results = self.adapter.get_results(job_id)
        except Exception as e:
             return "", f"Failed to get results: {e}"

        logs = results.get("logs", "")

        # Save raw result
        try:
            with open(run_dir / "jules_result.json", "w") as f:
                json.dump(results, f, indent=2)
        except Exception:
            pass

        if status != "COMPLETE":
             return "", f"Jules job failed or timed out. Logs:\n{logs}"

        # 5. Fetch and Apply Patch
        # Extract PR URL
        # Logs format: "Generated Pull Requests:\nTitle - https://github.com/.../pull/123"
        match = re.search(r"(https://github\.com/[^/]+/[^/]+/pull/\d+)", logs)
        patch_content = ""
        if match:
            pr_url = match.group(1)
            patch_url = pr_url + ".diff"
            logger.info(f"Fetching patch from {patch_url}")
            try:
                resp = requests.get(patch_url)
                if resp.status_code == 200:
                    patch_content = resp.text
                    # Apply patch
                    success = self.code_ops.apply_diff(patch_content)
                    if not success:
                        logger.warning("Failed to apply Jules patch locally.")
                        logs += "\nWARNING: Failed to apply patch locally."
                    else:
                        logs += "\nPatch applied successfully."
                else:
                    logger.warning(f"Failed to fetch patch: {resp.status_code}")
                    logs += f"\nWARNING: Failed to fetch patch from {patch_url}"
            except Exception as e:
                logger.error(f"Error fetching/applying patch: {e}")
                logs += f"\nERROR: {e}"
        else:
            logger.warning("No PR URL found in Jules logs.")
            logs += "\nWARNING: No PR URL found, cannot apply changes locally."

            # Fallback: If "diff" is in results (e.g. mock mode)
            if results.get("diff"):
                patch_content = results["diff"]
                self.code_ops.apply_diff(patch_content)

        return patch_content, logs
