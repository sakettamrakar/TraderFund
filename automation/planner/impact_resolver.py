"""
Component Impact Resolver
=========================
Identifies which components and files are affected by a domain intent.
"""

import json
import logging
import argparse
from pathlib import Path
import yaml
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("impact_resolver")

COMPONENTS_DIR = Path("docs/memory/05_components")

def load_components() -> List[Dict[str, Any]]:
    components = []
    if not COMPONENTS_DIR.exists():
        logger.warning(f"Components dir {COMPONENTS_DIR} not found.")
        return []
        
    for path in COMPONENTS_DIR.glob("*.yaml"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                comp = yaml.safe_load(f)
                comp["_filename"] = path.name
                components.append(comp)
        except Exception as e:
            logger.error(f"Failed to load component {path}: {e}")
    return components

# Mapping from spec filename stem to source files (mirrors ComponentAgent)
SPEC_TO_SOURCE_MAP = {
    "regime_engine": ["src/layers/", "src/evolution/regime_context_builder.py"],
    "narrative_engine": ["src/narratives/"],
    "meta_engine": ["src/intelligence/"],
    "factor_engine": ["src/layers/factor_layer.py", "src/layers/factor_live.py", "src/evolution/factor_context_builder.py"],
    "strategy_selector": ["src/strategy/", "src/evolution/strategy_eligibility_resolver.py"],
    "convergence_engine": ["src/evolution/"],
    "constraint_engine": ["src/capital/"],
    "portfolio_intelligence": ["src/decision/"],
    "dashboard": ["src/dashboard/"],
    "governance": ["src/governance/"],
    "momentum_engine": ["src/core_modules/momentum_engine/"],
    "ingestion_us": ["src/ingestion/"],
    "ingestion_india": ["src/ingestion/"],
    "ingestion_events": ["src/ingestion/"],
    "factor_lens": ["src/layers/factor_layer.py"],
    "fundamental_lens": ["src/layers/"],
    "narrative_lens": ["src/narratives/"],
    "strategy_lens": ["src/strategy/"],
    "technical_lens": ["src/layers/"],
}

def parse_human_intent(human_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Converts human_intent.json structure into list of intent objects."""
    intents = []
    user_intent = human_intent.get("user_intent", {})

    goal = user_intent.get("goal", "Unknown Goal")
    behavior = user_intent.get("expected_behavior_change", "")
    layers = user_intent.get("affected_layers", [])

    # If no layers specified, try to infer from goal
    if not layers:
        layers = ["Unknown"]

    for layer in layers:
        intents.append({
            "concept": goal,
            "domain_level": layer,
            "intent": behavior,
            "source": "human_intent"
        })

    return intents

def resolve_impact(intents: List[Dict[str, Any]], components: List[Dict[str, Any]]) -> Dict[str, Any]:
    impact_plan = {
        "impacted_components": [],
        "impacted_files": set(),
        "intents": intents
    }
    
    for intent in intents:
        concept = intent.get("concept", "").lower()
        level = intent.get("domain_level", "")
        
        # Find matching components
        for comp in components:
            match = False
            
            # Broad search: Check if concept is present anywhere in the component definition
            # This covers name, responsibility, domain_entities, success_criteria_refs, etc.
            comp_str = str(comp).lower()
            if concept in comp_str:
                match = True
            
            # Fallback: if concept is "2. opportunity discovery...", fuzzy match keywords
            if "discovery" in concept and "convergence" in comp_str:
                match = True 
            if "score" in concept and "convergence" in comp_str:
                match = True

            if match:
                c_name = comp.get("name", "Unknown")
                filename = comp.get("_filename", "")
                spec_key = Path(filename).stem
                
                # Avoid duplicates
                if not any(x["name"] == c_name for x in impact_plan["impacted_components"]):
                    impact_plan["impacted_components"].append({
                        "name": c_name,
                        "source_yaml": filename
                    })
                    
                    # Add source files from map
                    sources = SPEC_TO_SOURCE_MAP.get(spec_key, [])
                    for src in sources:
                        impact_plan["impacted_files"].add(src)
                        
    # Convert set to list for JSON serialization
    impact_plan["impacted_files"] = list(impact_plan["impacted_files"])
    return impact_plan

def main():
    parser = argparse.ArgumentParser(description="Component Impact Resolver")
    parser.add_argument("--intent", default="automation/tasks/current_intent.json", help="Input intent JSON")
    parser.add_argument("--human-intent", help="Input human intent JSON (optional, overrides intent)")
    parser.add_argument("--output", default="automation/tasks/current_impact.json", help="Output impact JSON")
    args = parser.parse_args()
    
    intents = []
    human_intent = {}

    # 1. Try Human Intent (Highest Priority if Modified)
    if args.human_intent:
        hi_path = Path(args.human_intent)
        if hi_path.exists():
            human_intent = json.loads(hi_path.read_text(encoding="utf-8"))
            if human_intent.get("manually_modified", False):
                intents = parse_human_intent(human_intent)
                logger.info(f"Loaded {len(intents)} intents from Human Intent file (Modified).")
        else:
            logger.warning(f"Human intent file {hi_path} not found.")

    # 2. Try Original Intents in Human Intent (Highest Fidelity / Versioned)
    if not intents and human_intent:
        original = human_intent.get("original_intents", [])
        if original:
            intents = original
            logger.info(f"Loaded {len(intents)} intents from Human Intent (Original Fidelity).")

    # 3. Try Granular Intent File (Standard Path - Fallback if original missing)
    if not intents:
        intent_path = Path(args.intent)
        if intent_path.exists():
            loaded_intents = json.loads(intent_path.read_text(encoding="utf-8"))
            if loaded_intents:
                intents = loaded_intents
                logger.info(f"Loaded {len(intents)} intents from granular intent file.")

    # 4. Fallback to Synthetic Human Intent (Low Fidelity)
    if not intents and human_intent:
        intents = parse_human_intent(human_intent)
        logger.info(f"Fallback: Loaded {len(intents)} intents from auto-generated Human Intent file (Low Fidelity).")

    if not intents:
         logger.warning("No intent source found.")
         return

    components = load_components()
    impact = resolve_impact(intents, components)
    
    output_path = Path(args.output)
    output_path.write_text(json.dumps(impact, indent=2), encoding="utf-8")
    
    logger.info(f"Resolved impact: {len(impact['impacted_components'])} components, {len(impact['impacted_files'])} files.")

if __name__ == "__main__":
    main()
