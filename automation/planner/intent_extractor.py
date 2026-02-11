"""
Domain Intent Extractor
=======================
Maps memory diffs to domain concepts (L1-L9) and explicit intent.
"""

import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("intent_extractor")

DOMAIN_MODEL_PATH = Path("docs/memory/03_domain/domain_model.md")

# Naive mapping for now - this should be evolved into a richer ontology
KEYWORD_MAP = {
    "regime": "L1",
    "market": "L1",
    "volatility": "L1",
    "momentum": "L2",
    "trend": "L2",
    "evaluation": "L3",
    "meta-analysis": "L3",
    "factor": "L4",
    "component": "L5",
    "discovery": "L6",
    "convergence": "L7",
    "score": "L7",
    "ranking": "L7",
    "portfolio": "L8",
    "sizing": "L8",
    "risk": "L9",
    "execution": "L10",
    "harness": "L11",
}

def load_diffs(diff_path: Path) -> List[Dict[str, Any]]:
    if not diff_path.exists():
        logger.warning(f"Diff file {diff_path} not found.")
        return []
    return json.loads(diff_path.read_text(encoding="utf-8"))

def extract_intent(diffs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    intents = []
    
    for diff in diffs:
        content = diff.get("content", "").lower()
        section = diff.get("section", "").lower()
        
        # Determine Domain Level
        domain_level = "Unknown"
        concept = "Unknown"
        
        # Check section first
        for key, level in KEYWORD_MAP.items():
            if key in section:
                domain_level = level
                concept = section
                break
        
        # Check content if section didn't match
        if domain_level == "Unknown":
            for key, level in KEYWORD_MAP.items():
                if key in content:
                    domain_level = level
                    concept = key.capitalize()
                    break
        
        # Construct Intent
        intent_desc = f"Update {concept} ({domain_level}): {diff.get('content')}"
        
        intents.append({
            "source_file": diff.get("file"),
            "domain_level": domain_level,
            "concept": concept,
            "intent": intent_desc,
            "original_diff": diff
        })
        
    return intents

def main():
    parser = argparse.ArgumentParser(description="Domain Intent Extractor")
    parser.add_argument("--input", default="automation/planner/memory_diff.json", help="Input diff JSON")
    parser.add_argument("--output", default="automation/tasks/current_intent.json", help="Output intent JSON")
    args = parser.parse_args()
    
    diffs = load_diffs(Path(args.input))
    intents = extract_intent(diffs)
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(intents, indent=2), encoding="utf-8")
    
    logger.info(f"Extracted {len(intents)} intents to {output_path}")

if __name__ == "__main__":
    main()
