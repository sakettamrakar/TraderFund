import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ContractEnforcer:
    """
    Enforces architectural contracts and constraints on code changes.
    """

    def __init__(self):
        pass

    def check_violations(self, diff: str, changed_files: List[str]) -> List[Dict[str, str]]:
        """
        Analyzes the diff and changed files for contract violations.
        """
        violations = []

        # Rule 1: Protected Paths
        # docs/memory should not be modified by execution agents (unless specifically authorized)
        # However, Phase S runs *after* execution, so if it was modified, we should flag it if it wasn't intended.
        # Note: run_build_loop checks this too, but we add a record here.
        for file in changed_files:
            if "docs/memory/" in file:
                 violations.append({
                    "type": "CONSTRAINT_BREAK",
                    "description": f"Direct modification of memory file {file} during execution phase.",
                    "severity": "HIGH"
                })

        # Rule 2: Heuristic Check for 'Lens bypassing L4 permission'
        # If 'src/lens/' imports 'src/execution/' directly, that might be a violation.
        # We check the diff for added lines containing imports.

        # This is a basic heuristic.
        for line in diff.splitlines():
            if line.startswith("+") and "import" in line:
                if "src/execution" in line and any("src/lens" in f for f in changed_files):
                     violations.append({
                        "type": "LAYER_SKIP",
                        "description": "Potential layer violation: Lens component importing Execution layer.",
                        "severity": "MEDIUM"
                    })

        return violations
