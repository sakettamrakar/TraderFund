import json
import subprocess
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict

# Import Phase Q Validators
from automation.quality.semantic import SemanticValidator
from automation.quality.visual import VisualValidator
from automation.quality.report import QualityReporter

logger = logging.getLogger(__name__)

@dataclass
class ValidationPlan:
    unit_tests: bool = True
    domain_contracts: bool = True
    semantic_validation: bool = True  # Phase Q: REQUIRED
    visual_validation: bool = False
    observability_validation: bool = False

    def to_dict(self):
        return {
            "unit_tests": self.unit_tests,
            "domain_contracts": self.domain_contracts,
            "semantic_validation": self.semantic_validation,
            "visual_validation": self.visual_validation,
            "observability_validation": self.observability_validation
        }

class ValidationPlanner:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def create_plan(self, changed_files: List[str]) -> ValidationPlan:
        plan = ValidationPlan()

        for file in changed_files:
            if "src/dashboard" in file or "src/frontend" in file:
                plan.visual_validation = True
            if "src/ingestion" in file or "pipelines" in file:
                plan.observability_validation = True

        return plan

class ValidationRunner:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def run_unit_tests(self) -> (bool, str):
        """Runs pytest and returns (success, output)."""
        logger.info("Running unit tests...")
        try:
            result = subprocess.run(
                ["pytest"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            success = result.returncode == 0
            return success, result.stdout + "\n" + result.stderr
        except Exception as e:
            logger.error(f"Failed to run pytest: {e}")
            return False, str(e)

    def check_domain_contracts(self, changed_files: List[str]) -> (bool, str):
        """Checks domain architectural rules."""
        logger.info("Checking domain contracts...")
        errors = []

        # Rule 1: Ring-1 (Truth) components (macro, evolution) should not import Ring-3 (Intelligence)
        ring_1_paths = ["src/macro", "src/evolution"]
        ring_3_paths = ["src/decision", "src/dashboard"]

        for file in changed_files:
            if not file.endswith(".py"):
                continue

            full_path = self.project_root / file
            if not full_path.exists():
                continue

            try:
                content = full_path.read_text()

                # Check if current file is in Ring-1
                is_ring_1 = any(p in file for p in ring_1_paths)

                if is_ring_1:
                    for r3 in ring_3_paths:
                        module_name = r3.replace("src/", "").replace("/", ".")
                        if f"import {module_name}" in content or f"from {module_name}" in content:
                            errors.append(f"OBL-INTELLIGENCE-RESEARCH-RESPECT Violation: {file} imports {module_name}")

            except Exception as e:
                errors.append(f"Error checking {file}: {e}")

        if errors:
            return False, "\n".join(errors)
        return True, "All domain contracts passed."

    def run_semantic_validators(self, run_dir: Path, plan: ValidationPlan) -> (bool, str):
        """
        Runs Phase Q semantic validators.
        """
        if not plan.semantic_validation:
            return True, "Semantic validation skipped."

        logger.info("Running Semantic Validators...")
        semantic_validator = SemanticValidator(self.project_root)
        visual_validator = VisualValidator(self.project_root)
        reporter = QualityReporter(run_dir)

        # 1. Semantic Check (Distribution)
        dist_results = semantic_validator.check_distributions(run_dir)
        with open(run_dir / "semantic_checks.json", "w") as f:
            json.dump(dist_results, f, indent=2)

        # 2. Stability Check
        stability_results = semantic_validator.check_stability(run_dir)
        with open(run_dir / "stability_report.json", "w") as f:
            json.dump(stability_results, f, indent=2)

        # 3. Coherence Check
        coherence_results = semantic_validator.check_coherence(run_dir)
        with open(run_dir / "coherence_report.json", "w") as f:
            json.dump(coherence_results, f, indent=2)

        # 4. Visual Check (if planned)
        visual_results = {}
        if plan.visual_validation:
            visual_results = visual_validator.validate(run_dir)
            with open(run_dir / "visual_report.json", "w") as f:
                json.dump(visual_results, f, indent=2)

        # 5. Generate Report
        summary = reporter.generate_report(
            dist_results,
            stability_results,
            coherence_results,
            visual_results
        )

        # Check for REQUIRED failures
        # Semantic, Stability, Coherence are REQUIRED if enabled
        failures = []
        if dist_results["status"] == "FAIL":
            failures.append("Semantic Distribution Check Failed")
        if stability_results["status"] == "FAIL":
            failures.append("Stability Check Failed")
        if coherence_results["status"] == "FAIL":
            failures.append("Coherence Check Failed")

        if failures:
            return False, "\n".join(failures)

        return True, "All semantic validators passed."

    def run_optional_validators(self, plan: ValidationPlan) -> (bool, str):
        """Runs optional validators based on plan."""
        report = []
        success = True

        if plan.observability_validation:
            logger.info("Running Observability Validator (Stub)...")
            report.append("Observability Validation: SKIPPED (Not implemented)")

        return success, "\n".join(report)
