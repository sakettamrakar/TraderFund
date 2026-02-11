import json
import logging
import traceback
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class FailureAnalyzer:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir

    def generate_failure_tree(self, error: Exception, task: Dict, stage: str, evidence: str = ""):
        """
        Generates a failure tree JSON file in the run directory.
        """
        failure_tree = {
            "task_id": task.get("task_id", "unknown"),
            "run_id": self.run_dir.name,
            "root_cause_guess": str(error),
            "memory_files_involved": task.get("changed_memory_files", []),
            "component_involved": self._infer_component(task.get("changed_memory_files", [])),
            "validation_stage_failed": stage,
            "evidence_excerpt": evidence[:2000] if evidence else traceback.format_exc()[:2000]
        }

        try:
            with open(self.run_dir / "failure_tree.json", "w") as f:
                json.dump(failure_tree, f, indent=2)
            logger.info(f"Failure tree generated at {self.run_dir / 'failure_tree.json'}")
        except Exception as e:
            logger.error(f"Failed to write failure tree: {e}")

    def _infer_component(self, files: list[str]) -> str:
        """Simple heuristic to guess component."""
        if not files:
            return "unknown"

        counts = {}
        for f in files:
            parts = f.split('/')
            if len(parts) > 1:
                top_level = parts[0]
                if top_level == "src":
                    component = parts[1] if len(parts) > 2 else "core"
                else:
                    component = top_level
                counts[component] = counts.get(component, 0) + 1

        if not counts:
            return "unknown"

        return max(counts, key=counts.get)
