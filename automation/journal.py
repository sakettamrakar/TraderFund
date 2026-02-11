"""
Run Journal
===========
Tracks the execution of autonomous runs for auditability and observability.
"""

import json
import time
import uuid
from pathlib import Path

class RunJournal:
    def __init__(self, run_id=None, worker_id="manual", dry_run=False):
        self.run_id = run_id or str(uuid.uuid4())
        self.data = {
            "run_id": self.run_id,
            "timestamp_start": time.time(),
            "timestamp_end": None,
            "worker_identifier": worker_id,
            "changed_memory_files": [],  # Trigger files (specs)
            "files_modified": [],        # Files changed by agents
            "test_status": "NOT_RUN",
            "failure_reason": None,
            "guard_violations": [],
            "dry_run": dry_run
        }
        # Ensure logs directory exists
        self.log_dir = Path(__file__).parent / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_change(self, filepath: str):
        """Record a file modification."""
        if filepath not in self.data["files_modified"]:
            self.data["files_modified"].append(filepath)

    def log_violation(self, violation: str):
        """Record a safety violation."""
        self.data["guard_violations"].append(violation)

    def fail(self, reason: str):
        """Mark the run as failed with a reason."""
        self.data["failure_reason"] = reason
        self.finish()

    def set_test_status(self, status: str):
        """Update test status (PASS/FAIL)."""
        self.data["test_status"] = status

    def set_changed_specs(self, specs: list[str]):
        """Record which spec files triggered the run."""
        self.data["changed_memory_files"] = specs

    def finish(self):
        """Mark run as complete and write to disk."""
        if not self.data["timestamp_end"]:
            self.data["timestamp_end"] = time.time()
        self.write()

    def write(self):
        """Write the journal to a JSON file."""
        filepath = self.log_dir / f"run_{self.run_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        return filepath
