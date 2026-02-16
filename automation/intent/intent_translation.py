"""
Intent Translation Saver
=========================
Saves a structured intent translation file per run into automation/intent/.
This file captures the translated human intent BEFORE execution begins,
enabling review and optional correction via override files.

Schema:
{
    "run_id": "...",
    "memory_changes_detected": [...],
    "extracted_intent": "...",
    "target_components": [...],
    "expected_behavioral_change": "...",
    "confidence": 0.82
}
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

INTENT_DIR = Path(__file__).resolve().parent


def save_intent_translation(
    run_id: str,
    memory_changes: List[Dict[str, Any]],
    intents: List[Dict[str, Any]],
    target_components: List[str],
    human_intent: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Save the intent translation file for a run.

    This must be called BEFORE execution begins so the intent can be
    reviewed and optionally overridden.

    Returns the path to the saved file.
    """
    # Synthesize extracted intent summary
    intent_parts = []
    for intent in intents:
        concept = intent.get("concept", "")
        level = intent.get("domain_level", "")
        desc = intent.get("intent", "")
        if desc:
            intent_parts.append(desc)
        elif concept:
            intent_parts.append(f"Update {concept} ({level})")

    extracted_intent = "; ".join(intent_parts) if intent_parts else "No explicit intent extracted."

    # Determine expected behavioral change
    expected_change = "No specific behavior change extracted."
    if human_intent:
        user_intent = human_intent.get("user_intent", {})
        change = user_intent.get("expected_behavior_change", "")
        if change:
            expected_change = change

    # Compute confidence heuristic based on intent specificity
    confidence = _compute_confidence(intents, memory_changes)

    translation = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "memory_changes_detected": [
            {
                "file": c.get("file", ""),
                "change_type": c.get("change_type", ""),
                "section": c.get("section", ""),
            }
            for c in memory_changes
        ],
        "extracted_intent": extracted_intent,
        "target_components": target_components,
        "expected_behavioral_change": expected_change,
        "confidence": round(confidence, 4),
    }

    INTENT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = INTENT_DIR / f"{run_id}_intent_translation.json"
    output_path.write_text(json.dumps(translation, indent=2), encoding="utf-8")

    logger.info(f"Intent translation saved: {output_path} (confidence={confidence:.2f})")
    return output_path


def _compute_confidence(
    intents: List[Dict[str, Any]],
    memory_changes: List[Dict[str, Any]],
) -> float:
    """
    Heuristic confidence score for the intent translation.

    Factors:
    - Has intents at all (base)
    - Domain level specificity (known vs Unknown)
    - Ratio of intents to memory changes
    """
    if not intents:
        return 0.1

    base = 0.5

    # Bonus for specific domain levels
    known_levels = sum(
        1 for i in intents if i.get("domain_level", "Unknown") != "Unknown"
    )
    level_ratio = known_levels / len(intents) if intents else 0
    base += level_ratio * 0.3

    # Bonus for concept specificity
    has_concept = sum(
        1 for i in intents if i.get("concept", "Unknown") != "Unknown"
    )
    concept_ratio = has_concept / len(intents) if intents else 0
    base += concept_ratio * 0.15

    # Slight bonus if changes are proportional to intents
    if memory_changes and intents:
        ratio = min(len(intents) / len(memory_changes), 1.0)
        base += ratio * 0.05

    return min(base, 1.0)


def load_intent_override(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Check for and load an intent override file for the given run.

    Override schema:
    {
        "corrected_intent": "...",
        "clarifications": "...",
        "scope_limits": "...",
        "approved_by": "human",
        "timestamp": "..."
    }

    Returns None if no override exists.
    """
    override_path = INTENT_DIR / f"{run_id}_intent_override.json"
    if not override_path.exists():
        return None

    try:
        override = json.loads(override_path.read_text(encoding="utf-8"))
        logger.info(f"Intent override found for run {run_id}: {override_path}")
        return override
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load intent override: {e}")
        return None
