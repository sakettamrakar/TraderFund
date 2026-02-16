import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Protected paths that agents MUST NOT modify
PROTECTED_PREFIXES = ["docs/memory/", "docs/epistemic/"]

# Layer hierarchy — violations occur when a lower layer imports a higher one
# Lenses (observation) must NOT import from Execution (action) layers
# IMPORTANT: Python imports use dot notation (src.execution), file paths use slash (src/execution/)
#            We check both formats to catch violations in diffs regardless of context.
LAYER_RULES = [
    {
        "source_patterns": ["src/lens/", "src/layers/", "src/narratives/"],
        "forbidden_import_patterns": [
            "src/execution/", "src.execution",
            "src/capital/", "src.capital",
            "src/decision/", "src.decision",
        ],
        "violation_type": "LAYER_SKIP",
        "severity": "MEDIUM",
        "description": "Lens/Layer component importing Execution/Capital/Decision layer."
    },
    {
        "source_patterns": ["src/ingestion/"],
        "forbidden_import_patterns": [
            "src/execution/", "src.execution",
            "src/decision/", "src.decision",
            "src/strategy/", "src.strategy",
        ],
        "violation_type": "LAYER_SKIP",
        "severity": "HIGH",
        "description": "Ingestion layer importing Execution/Decision/Strategy layer."
    },
]


class ContractEnforcer:
    """
    Enforces architectural contracts and constraints on code changes.

    Rules:
      1. Protected Paths — docs/memory/ and docs/epistemic/ must not be modified by agents.
      2. Layer Hierarchy — Observation layers must not import from Execution layers.
      3. Config Integrity — automation_config.py DRY_RUN must not be changed to False.
    """

    def __init__(self):
        pass

    def check_violations(self, diff: str, changed_files: List[str]) -> List[Dict[str, str]]:
        """
        Analyzes the diff and changed files for contract violations.
        """
        violations = []

        # Rule 1: Protected Paths
        violations.extend(self._check_protected_paths(changed_files))

        # Rule 2: Layer Hierarchy
        violations.extend(self._check_layer_violations(diff, changed_files))

        # Rule 3: Config Integrity
        violations.extend(self._check_config_integrity(diff, changed_files))

        return violations

    def _check_protected_paths(self, changed_files: List[str]) -> List[Dict[str, str]]:
        """Check if any changed files are in protected directories."""
        violations = []
        for file in changed_files:
            for prefix in PROTECTED_PREFIXES:
                if prefix in file:
                    violations.append({
                        "type": "CONSTRAINT_BREAK",
                        "description": f"Direct modification of protected file {file} during execution phase.",
                        "severity": "HIGH"
                    })
                    break  # Don't double-flag same file
        return violations

    def _check_layer_violations(self, diff: str, changed_files: List[str]) -> List[Dict[str, str]]:
        """Check if any added import lines violate the layer hierarchy."""
        violations = []

        for line in diff.splitlines():
            # Only check added lines that contain imports
            if not (line.startswith("+") and "import" in line):
                continue

            for rule in LAYER_RULES:
                # Check if any changed file belongs to a source layer
                source_match = any(
                    any(pattern in f for pattern in rule["source_patterns"])
                    for f in changed_files
                )
                if not source_match:
                    continue

                # Check if the import line references a forbidden layer
                for forbidden in rule["forbidden_import_patterns"]:
                    if forbidden in line:
                        violations.append({
                            "type": rule["violation_type"],
                            "description": f"{rule['description']} Import: {line.strip()}",
                            "severity": rule["severity"]
                        })

        return violations

    def _check_config_integrity(self, diff: str, changed_files: List[str]) -> List[Dict[str, str]]:
        """Check if automation config is being tampered with."""
        violations = []
        config_files = [f for f in changed_files if "automation_config" in f]
        if config_files:
            for line in diff.splitlines():
                if line.startswith("+") and "dry_run" in line.lower() and "false" in line.lower():
                    violations.append({
                        "type": "CONFIG_TAMPER",
                        "description": "Attempted to disable DRY_RUN in automation_config.py.",
                        "severity": "HIGH"
                    })
        return violations
