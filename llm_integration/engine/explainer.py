"""
LLM Explainer Engine.
Orchestrates safe LLM calls with full guardrails.
"""
from typing import Optional, Dict, Any
from llm_integration.control.switches import LLMSwitches
from llm_integration.guardrails.input_validator import InputValidator
from llm_integration.guardrails.output_validator import OutputValidator
from llm_integration.prompts.narrative_prompt import build_narrative_prompt, SYSTEM_PROMPT
from llm_integration.schemas.models import NarrativeExplanation
from llm_integration.client import get_llm_client

class ExplainerEngine:
    """
    Main orchestrator for LLM explanations.
    Enforces all safety guardrails.
    """
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.input_validator = InputValidator()
        self.output_validator = OutputValidator()
        
    def explain_narrative(self, narrative_dict: Dict[str, Any]) -> Optional[NarrativeExplanation]:
        # 1. Check Kill Switch
        if not LLMSwitches.is_enabled("narrative"):
            print(LLMSwitches.FALLBACK_MESSAGE)
            return None
            
        # 2. Validate Input
        valid, reason = self.input_validator.validate_narrative_input(narrative_dict)
        if not valid:
            print(f"Input validation failed: {reason}")
            return None
            
        # 3. Build Prompt
        prompt = build_narrative_prompt(narrative_dict)
        
        # 4. Call LLM (Mock if no client)
        if self.llm_client is None:
            # Mock response for testing
            raw_output = self._mock_llm_response(narrative_dict)
        else:
            raw_output = self.llm_client.generate(SYSTEM_PROMPT, prompt)
            
        # 5. Validate Output
        signal_ids = set(narrative_dict.get('supporting_signals', []))
        valid, violations = self.output_validator.validate_output(raw_output, signal_ids)
        
        if not valid:
            print(f"Output validation failed: {violations}")
            return None
            
        # 6. Build Explanation Object
        conf = narrative_dict.get('confidence_score', 0)
        conf_level = "HIGH" if conf > 70 else ("MODERATE" if conf > 40 else "LOW")
        
        model_meta = {"model": "LocalLLM", "version": "1.0"} if self.llm_client else {"model": "Mock", "version": "1.0"}
        
        explanation = NarrativeExplanation.create(
            source_id=narrative_dict['narrative_id'],
            text=raw_output,
            signal_ids=list(signal_ids),
            event_ids=narrative_dict.get('supporting_events', []),
            conf=conf_level,
            uncertainty="Confidence is below threshold, treat with caution." if conf < 70 else "",
            model_meta=model_meta
        )
        
        return explanation
        
    def _mock_llm_response(self, narrative_dict: Dict) -> str:
        """Safe mock response for testing."""
        title = narrative_dict.get('title', 'Unknown')
        conf = narrative_dict.get('confidence_score', 0)
        state = narrative_dict.get('lifecycle_state', 'UNKNOWN')
        
        return f"""This narrative titled "{title}" represents an observed market pattern.
        
Current State: The narrative is currently {state} with a confidence level of {conf}%.

Evidence: The narrative was generated based on the supporting signals provided in the input.

Uncertainty Note: {"This is a moderate-to-low confidence observation. Further evidence is needed." if conf < 70 else "This observation has high supporting evidence."}

This explanation is based solely on the provided structured data."""
