"""
Action Plan Generator
=====================
Synthesizes planner outputs into a concrete execution plan for workers.
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("action_planner")

def generate_plan(impact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs the Action Plan.
    This is the critical step: converting "Intent" into "Instructions".
    """
    
    files = impact.get("impacted_files", [])
    components = impact.get("impacted_components", [])
    intents = impact.get("intents", [])
    
    if not intents:
        return {"status": "NO_ACTION_REQUIRED", "reason": "No intent detected."}

    # Synthesize instructions
    actions = []
    for intent in intents:
        concept = intent.get("concept")
        raw_diff = intent.get("original_diff", {}).get("content", "")
        actions.append(f"Implementing '{concept}' logic based on update: \"{raw_diff}\"")
        
    # Construct the final plan object
    # This structure mirrors what ComponentAgent expects (or will expect)
    plan = {
        "status": "ACTION_REQUIRED",
        "objective": f"Implement {len(intents)} memory updates.",
        "target_files": files,
        "target_components": [c["name"] for c in components],
        "detailed_instructions": actions,
        "forbidden_paths": ["docs/memory/**", ".git/**"],
        "context": {
            "intents": intents
        }
    }
    
    return plan

def main():
    parser = argparse.ArgumentParser(description="Action Plan Generator")
    parser.add_argument("--impact", default="automation/tasks/current_impact.json", help="Input impact JSON")
    parser.add_argument("--output", default="automation/tasks/action_plan.json", help="Output plan JSON")
    args = parser.parse_args()
    
    impact_path = Path(args.impact)
    if not impact_path.exists():
        logger.warning("No impact file found.")
        return

    impact = json.loads(impact_path.read_text(encoding="utf-8"))
    plan = generate_plan(impact)
    
    output_path = Path(args.output)
    output_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    
    logger.info(f"Generated Action Plan: {plan['status']}")

if __name__ == "__main__":
    main()
