import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ResultSummary:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.run_dir = Path("automation/runs") / run_id

    def generate(self):
        """
        Aggregates artifacts into a summary JSON.
        """
        logger.info("Summary: Generating result summary...")

        summary = {
            "executor": "JULES",
            "task_status": "UNKNOWN",
            "pr_created": False,
            "tests_passed": False,
            "files_modified": 0,
            "insertions": 0,
            "deletions": 0,
            "branch": None,
            "pr_url": None
        }

        try:
            # Load Status
            status_file = self.run_dir / "jules_status.json"
            if status_file.exists():
                try:
                    with open(status_file, "r") as f:
                        status_data = json.load(f)
                        summary["task_status"] = status_data.get("status", "UNKNOWN")
                except json.JSONDecodeError:
                    pass

            # Load PR Info
            pr_file = self.run_dir / "jules_pr.json"
            if pr_file.exists():
                try:
                    with open(pr_file, "r") as f:
                        pr_data = json.load(f)
                        summary["pr_url"] = pr_data.get("pr_url")
                        summary["branch"] = pr_data.get("branch")
                        if summary["pr_url"]:
                            summary["pr_created"] = True
                except json.JSONDecodeError:
                    pass

            # Analyze Diff
            diff_file = self.run_dir / "jules_diff.patch"
            files_modified = 0
            insertions = 0
            deletions = 0

            if diff_file.exists():
                diff_text = diff_file.read_text(encoding="utf-8")
                if diff_text:
                    files_modified = diff_text.count("diff --git")

                    for line in diff_text.splitlines():
                        if line.startswith("+") and not line.startswith("+++"):
                            insertions += 1
                        if line.startswith("-") and not line.startswith("---"):
                            deletions += 1

            summary["files_modified"] = files_modified
            summary["insertions"] = insertions
            summary["deletions"] = deletions

            # Check Tests
            tests_file = self.run_dir / "jules_tests.txt"
            if tests_file.exists():
                tests_text = tests_file.read_text(encoding="utf-8").lower()
                # Heuristic: "PASS" or "passed" without "fail"
                if ("pass" in tests_text or "success" in tests_text) and "fail" not in tests_text:
                    summary["tests_passed"] = True

            # Save Summary
            with open(self.run_dir / "jules_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)

            logger.info("Summary: jules_summary.json generated.")

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
