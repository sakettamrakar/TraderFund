import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ConstraintValidator")

class ConstraintValidator:
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.report = {
            "status": "PASS",
            "violations": []
        }

    def validate_narrative(self, data: Dict[str, Any]):
        """Validates a Narrative artifact."""
        required_fields = ["genesis_timestamp", "regime_context", "theses", "invalidation_criteria"]
        self._check_required_fields("Narrative", data, required_fields)
        
        # Logic Check: Genesis Time must be past/present
        if "genesis_timestamp" in data:
            try:
                gen_time = datetime.fromisoformat(data["genesis_timestamp"])
                if gen_time > datetime.now():
                     self._add_violation("Narrative genesis timestamp is in the future (Time Leak).")
            except ValueError:
                self._add_violation("Invalid ISO format for genesis_timestamp.")

    def validate_decision(self, data: Dict[str, Any]):
        """Validates a Decision artifact."""
        required_fields = ["decision_id", "narrative_ref", "action", "rationale", "risk_parameters"]
        self._check_required_fields("Decision", data, required_fields)
        
        # Logic Check: Rationale must be non-empty
        if "rationale" in data and len(str(data["rationale"]).strip()) < 10:
             self._add_violation("Decision rationale is too short or empty.")
             
        # Logic Check: Action must be valid
        valid_actions = ["ENTER", "EXIT", "HOLD", "DO_NOTHING"]
        if "action" in data and data["action"] not in valid_actions:
             self._add_violation(f"Invalid Action: {data['action']}. Must be one of {valid_actions}")

    def _check_required_fields(self, artifact_type: str, data: Dict, fields: List[str]):
        for f in fields:
            if f not in data:
                self._add_violation(f"{artifact_type} missing required field: '{f}'")

    def _add_violation(self, msg: str):
        self.report["status"] = "FAIL"
        self.report["violations"].append(msg)

    def run_validation(self, mode: str, target_file: str):
        logger.info(f"Validating {mode}: {target_file}")
        
        if not os.path.exists(target_file):
            self._add_violation(f"Target file not found: {target_file}")
            print(json.dumps(self.report, indent=2))
            return

        try:
            with open(target_file, 'r') as f:
                data = json.load(f)
                
            if mode == "narrative":
                self.validate_narrative(data)
            elif mode == "decision":
                self.validate_decision(data)
            else:
                self._add_violation(f"Unknown validation mode: {mode}")
                
        except json.JSONDecodeError:
             self._add_violation("Invalid JSON format.")
        except Exception as e:
             self._add_violation(f"System Error: {str(e)}")

        print(json.dumps(self.report, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Constraint Validator Skill")
    parser.add_argument("--mode", required=True, choices=["narrative", "decision"])
    parser.add_argument("--target", required=True, help="Path to JSON artifact")
    
    args = parser.parse_args()
    
    root = Path(os.getcwd())
    validator = ConstraintValidator(root)
    validator.run_validation(args.mode, args.target)

if __name__ == "__main__":
    main()
