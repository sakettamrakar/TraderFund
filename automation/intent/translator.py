"""
Human Intent Translator
=======================
Translates memory changes into structured human-readable intent.
"""

import json
import logging
import argparse
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("intent_translator")

def translate_intent(intent_path: Path, diff_path: Path, run_id: str) -> Dict[str, Any]:
    """
    Translates machine-generated intent and diffs into a human-readable structure.
    """
    intents = []
    if intent_path.exists():
        intents = json.loads(intent_path.read_text(encoding="utf-8"))

    diffs = []
    if diff_path.exists():
        diffs = json.loads(diff_path.read_text(encoding="utf-8"))

    # Synthesize fields
    goals = set()
    layers = set()
    behavior_changes = []

    for item in intents:
        if item.get("concept"):
            goals.add(item.get("concept"))
        if item.get("domain_level"):
            layers.add(item.get("domain_level"))
        if item.get("intent"):
            behavior_changes.append(item.get("intent"))

    # Create the structured object
    human_intent = {
        "run_id": run_id,
        "memory_change_summary": f"Detected {len(diffs)} changes across {len(intents)} intent clusters.",
        "user_intent": {
            "goal": ", ".join(sorted(goals)) if goals else "Unspecified update",
            "expected_behavior_change": "; ".join(behavior_changes) if behavior_changes else "No specific behavior change extracted.",
            "affected_layers": sorted(list(layers)),
            "risk_profile": "moderate", # Defaulting to moderate
            "non_goals": "Do not regress existing functionality.",
            "visual_expectations": "N/A",
            "constraints": "Ensure all tests pass.",
            "acceptance_signal": "Validation pipeline success."
        },
        "auto_generated": True,
        "manually_modified": False,
        "original_intents": intents,
        "timestamp": datetime.datetime.now().isoformat()
    }

    return human_intent

def main():
    parser = argparse.ArgumentParser(description="Human Intent Translator")
    parser.add_argument("--intent", required=True, help="Input intent JSON")
    parser.add_argument("--diff", required=True, help="Input memory diff JSON")
    parser.add_argument("--run-id", required=True, help="Current Run ID")
    parser.add_argument("--output", required=True, help="Output human_intent.json path")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    human_intent = translate_intent(Path(args.intent), Path(args.diff), args.run_id)

    output_path.write_text(json.dumps(human_intent, indent=2), encoding="utf-8")
    logger.info(f"Generated Human Intent at {output_path}")

if __name__ == "__main__":
    main()
