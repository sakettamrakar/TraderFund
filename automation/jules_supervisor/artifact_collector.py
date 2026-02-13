import json
import logging
import re
import requests
from pathlib import Path
from automation.jules.adapter import JulesAdapter

logger = logging.getLogger(__name__)

class ArtifactCollector:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.run_dir = Path("automation/runs") / run_id
        self.adapter = JulesAdapter()
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def collect(self, task_id: str):
        """
        Fetches results via JulesAdapter and saves artifacts.
        """
        logger.info(f"Collector: Fetching artifacts for task {task_id}...")

        pr_info = {
            "pr_url": None,
            "branch": None,
            "commit_sha": None
        }

        logs = ""
        tests = ""
        diff = ""

        try:
            results = self.adapter.get_results(task_id)
            logs = results.get("logs", "")
            tests = results.get("tests", "")
            diff = results.get("diff", "")

            # Extract PR URL from logs
            match = re.search(r"(https://github\.com/[^/]+/[^/]+/pull/\d+)", logs)
            if match:
                pr_url = match.group(1)
                pr_info["pr_url"] = pr_url

                # Fetch PR diff if adapter didn't return it
                if not diff:
                    patch_url = pr_url + ".diff"
                    try:
                        logger.info(f"Fetching diff from {patch_url}")
                        resp = requests.get(patch_url, timeout=10)
                        if resp.status_code == 200:
                            diff = resp.text
                        else:
                            logger.warning(f"Failed to fetch diff: {resp.status_code}")
                    except Exception as e:
                        logger.warning(f"Error fetching diff: {e}")

            # Save Artifacts
            # 1. Logs
            with open(self.run_dir / "jules_logs.txt", "w", encoding="utf-8") as f:
                f.write(str(logs))

            # 2. Diff
            with open(self.run_dir / "jules_diff.patch", "w", encoding="utf-8") as f:
                f.write(str(diff))

            # 3. Tests
            with open(self.run_dir / "jules_tests.txt", "w", encoding="utf-8") as f:
                f.write(str(tests))

            # 4. PR Info
            with open(self.run_dir / "jules_pr.json", "w", encoding="utf-8") as f:
                json.dump(pr_info, f, indent=2)

            logger.info("Collector: Artifacts saved.")

        except Exception as e:
            logger.error(f"Collector failed: {e}")
            with open(self.run_dir / "jules_logs.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\nERROR Collecting Artifacts: {e}")
