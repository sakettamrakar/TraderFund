import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class QualityReporter:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.summary = {
            "grade": "U",
            "score": 0.0,
            "components": {},
            "verdict": "UNKNOWN",
            "pass_rate": 0.0,
            "total_checks": 0,
            "passed_checks": 0
        }

    def generate_report(self, semantic_results: Dict, stability_results: Dict, coherence_results: Dict, visual_results: Dict) -> Dict:
        """
        Aggregates component results and calculates a final grade.
        Writes summary to disk.
        """
        # Calculate component stats
        self.summary["components"]["semantic"] = self._summarize_component(semantic_results)
        self.summary["components"]["stability"] = self._summarize_component(stability_results)
        self.summary["components"]["coherence"] = self._summarize_component(coherence_results)
        self.summary["components"]["visual"] = self._summarize_component(visual_results)

        # Aggregate stats
        total_checks = 0
        passed_checks = 0
        has_failure = False

        all_results = [semantic_results, stability_results, coherence_results, visual_results]

        for res in all_results:
            if res.get("status") == "FAIL":
                has_failure = True

            # Count checks
            # Assuming 'checks' is list of dicts with 'status'
            for check in res.get("checks", []):
                status = check.get("status")
                if status != "SKIPPED":
                    total_checks += 1
                    if status == "PASS":
                        passed_checks += 1

        pass_rate = (passed_checks / total_checks) if total_checks > 0 else 1.0

        self.summary["total_checks"] = total_checks
        self.summary["passed_checks"] = passed_checks
        self.summary["pass_rate"] = pass_rate

        # Grading Logic
        if has_failure:
            # If any required component FAILED, grade is F (or D)
            self.summary["grade"] = "D"
            self.summary["verdict"] = "FAIL"
        elif pass_rate >= 0.95:
            self.summary["grade"] = "A"
            self.summary["verdict"] = "EXCELLENT"
        elif pass_rate >= 0.8:
            self.summary["grade"] = "B"
            self.summary["verdict"] = "GOOD"
        else:
            self.summary["grade"] = "C"
            self.summary["verdict"] = "MARGINAL"

        # Write to disk
        try:
            with open(self.run_dir / "quality_summary.json", "w") as f:
                json.dump(self.summary, f, indent=2)
            logger.info(f"Quality report generated at {self.run_dir / 'quality_summary.json'}")
        except Exception as e:
            logger.error(f"Failed to write quality summary: {e}")

        return self.summary

    def _summarize_component(self, results: Dict) -> Dict:
        return {
            "status": results.get("status", "UNKNOWN"),
            "failure_count": len(results.get("failures", [])),
            "check_count": len(results.get("checks", []))
        }
