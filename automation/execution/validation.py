import json
import subprocess
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict

logger = logging.getLogger(__name__)

@dataclass
class ValidationPlan:
    unit_tests: bool = True
    domain_contracts: bool = True
    visual_validation: bool = False
    observability_validation: bool = False

    def to_dict(self):
        return {
            "unit_tests": self.unit_tests,
            "domain_contracts": self.domain_contracts,
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

    def run_optional_validators(self, plan: ValidationPlan) -> (bool, str):
        """Runs optional validators based on plan."""
        report = []
        success = True

        if plan.visual_validation:
            logger.info("Running Visual Validator (Stub)...")
            # In Phase 3, this is a placeholder or basic check
            report.append("Visual Validation: SKIPPED (Not implemented)")

        if plan.observability_validation:
            logger.info("Running Observability Validator (Stub)...")
            report.append("Observability Validation: SKIPPED (Not implemented)")

        return success, "\n".join(report)
