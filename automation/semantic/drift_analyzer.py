import logging
import json
from typing import Dict, Any, Optional

# We import ask from gemini_fallback which we fixed earlier
from automation.executors.gemini_fallback import ask

logger = logging.getLogger(__name__)

class DriftAnalyzer:
    """
    Analyzes drift between intent, plan, and code changes.
    """

    def detect_drift(self, intent: str, plan: Dict[str, Any], diff: str, success_criteria: str = "") -> Dict[str, Any]:
        """
        Uses LLM to detect semantic drift.
        """
        # Safety check for empty inputs
        if not intent:
            intent = "No explicit intent provided."
        if not plan:
            plan = {"status": "NO_PLAN", "objective": "Unknown"}
        if not diff:
            return {
                "drift_detected": False,
                "reasoning": "No code changes to analyze.",
                "alignment_score": 1.0,
                "missing_elements": []
            }

        prompt = (
            f"You are a semantic code analyst. Your task is to verify if the code changes match the intent, plan, and success criteria.\n\n"
            f"Intent:\n{intent}\n\n"
            f"Success Criteria:\n{success_criteria}\n\n"
            f"Plan:\n{json.dumps(plan, indent=2)}\n\n"
            f"Code Changes (Diff):\n{diff[:10000]}\n\n"  # Truncate diff to avoid token limit if very large
            f"Question: Do the code changes semantically align with the intent, plan, and success criteria? Or is there drift (partial implementation, wrong logic, skipping steps)?\n\n"
            f"Output JSON format ONLY:\n"
            f"{{\n"
            f"  \"drift_detected\": boolean,\n"
            f"  \"reasoning\": \"string explaining the analysis\",\n"
            f"  \"alignment_score\": float (0.0 to 1.0),\n"
            f"  \"missing_elements\": [\"list of missing requirements\"]\n"
            f"}}"
        )

        response = ""
        try:
            response = ask(prompt)
            # Try to parse JSON from response (handling potential markdown blocks)
            clean_response = response.strip()

            # Simple markdown cleanup
            if "```json" in clean_response:
                clean_response = clean_response.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_response:
                clean_response = clean_response.split("```")[1].split("```")[0].strip()

            # Sometimes LLMs add text before/after JSON, try to find the brace
            if "{" in clean_response:
                start = clean_response.find("{")
                end = clean_response.rfind("}") + 1
                clean_response = clean_response[start:end]

            result = json.loads(clean_response)
            return result
        except Exception as e:
            logger.error(f"Drift analysis failed: {e}")
            # If we mocked the response, it might not be JSON.
            # If MOCK_GEMINI is on, ask returns "MOCK_RESPONSE: ..." which is not JSON.
            # We should handle that case gracefully for testing.
            if "MOCK_RESPONSE" in str(response):
                return {
                    "drift_detected": False, # Assume pass for mock
                    "reasoning": "Mock execution (analysis skipped).",
                    "alignment_score": 1.0,
                    "missing_elements": []
                }

            return {
                "drift_detected": True,
                "reasoning": f"Analysis failed: {e}",
                "alignment_score": 0.0,
                "missing_elements": []
            }
