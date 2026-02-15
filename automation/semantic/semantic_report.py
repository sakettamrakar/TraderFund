import json
import logging
from pathlib import Path
from typing import Dict, Any
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class SemanticReportGenerator:
    """
    Generates and prints the semantic report.
    """

    def generate(self, report: Dict[str, Any], output_path: Path):
        """
        Writes JSON report and prints summary.
        """
        # Ensure directory exists
        try:
            if not isinstance(output_path, Path):
                output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            logger.info(f"Semantic Report written to {output_path}")
        except Exception as e:
            logger.error(f"Failed to write semantic report: {e}")

        # Console Summary
        self._print_summary(report)

    def _print_summary(self, report: Dict[str, Any]):
        print("\n" + "=" * 60)
        print(f"  PHASE S — SEMANTIC VALIDATION REPORT")
        print("=" * 60)

        score = report.get("intent_alignment_score", 0.0)
        rec = report.get("recommendation", "UNKNOWN")
        drift = report.get("drift_detected", False)

        color = Fore.GREEN
        if rec == "REVISE":
            color = Fore.YELLOW
        elif rec == "ESCALATE":
            color = Fore.RED

        print(f"  Recommendation: {color}{rec}{Style.RESET_ALL}")
        print(f"  Alignment Score: {score:.2f}")
        print(f"  Drift Detected: {'YES' if drift else 'NO'}")

        violations = report.get("violations", [])
        if violations:
            print(f"\n  {Fore.RED}Violations:{Style.RESET_ALL}")
            for v in violations:
                print(f"    - [{v.get('type')}] {v.get('description')} ({v.get('severity')})")

        if drift:
            print(f"\n  {Fore.YELLOW}Drift Reasoning:{Style.RESET_ALL}")
            print(f"    {report.get('drift_reasoning', '')}")

        print("=" * 60 + "\n")
