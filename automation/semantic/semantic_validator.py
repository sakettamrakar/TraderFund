import logging
import json
from pathlib import Path
from typing import List, Dict, Any

from automation.semantic.contract_enforcer import ContractEnforcer
from automation.semantic.drift_analyzer import DriftAnalyzer
# SemanticReportGenerator is imported inside the method or handled later?
# No, let's assume it's available.
try:
    from automation.semantic.semantic_report import SemanticReportGenerator
except ImportError:
    pass # Might not exist yet if running step by step

logger = logging.getLogger(__name__)

class SemanticValidator:
    """
    Orchestrates the semantic validation process.
    """

    def __init__(self, run_id: str, project_root: str):
        self.run_id = run_id
        self.project_root = Path(project_root)
        self.contract_enforcer = ContractEnforcer()
        self.drift_analyzer = DriftAnalyzer()
        try:
            self.report_generator = SemanticReportGenerator()
        except NameError:
             # Fallback if class not imported (should not happen in full run)
             from automation.semantic.semantic_report import SemanticReportGenerator
             self.report_generator = SemanticReportGenerator()

    def validate(self, intent_path: str, action_plan: Dict[str, Any], changed_files: List[str], diff: str) -> Dict[str, Any]:
        """
        Runs the semantic validation pipeline.
        """
        logger.info("Starting Semantic Validation...")

        # 1. Load Intent
        intent = ""
        if intent_path and Path(intent_path).exists():
            intent = Path(intent_path).read_text(encoding="utf-8")

        # 2. Check Contracts
        violations = self.contract_enforcer.check_violations(diff, changed_files)

        # 2.5 Load Success Criteria
        success_criteria_path = self.project_root / "docs" / "memory" / "02_success" / "success_criteria.md"
        success_criteria = ""
        if success_criteria_path.exists():
            success_criteria = success_criteria_path.read_text(encoding="utf-8")

        # 3. Detect Drift
        drift_result = self.drift_analyzer.detect_drift(intent, action_plan, diff, success_criteria)

        # 4. Synthesize Result
        drift_detected = drift_result.get("drift_detected", False)
        alignment_score = drift_result.get("alignment_score", 0.0)

        # Determine Recommendation
        recommendation = "ACCEPT"
        if drift_detected or alignment_score < 0.7:
            recommendation = "REVISE"
        if any(v["severity"] == "HIGH" for v in violations):
            recommendation = "ESCALATE"

        report = {
            "run_id": self.run_id,
            "intent_alignment_score": alignment_score,
            "success_criteria_alignment": 1.0 if not drift_detected else 0.5, # Placeholder until S2
            "layer_integrity": "FAIL" if violations else "PASS",
            "drift_detected": drift_detected,
            "violations": violations,
            "recommendation": recommendation,
            "drift_reasoning": drift_result.get("reasoning", "")
        }

        # 5. Generate Report Artifact
        output_path = self.project_root / "automation" / "runs" / self.run_id / "semantic_report.json"
        self.report_generator.generate(report, output_path)

        return report
