"""
Output Validation Guardrails.
Ensures LLM outputs do not contain forbidden language or hallucinations.
"""
import re
from typing import Tuple, List, Set

class OutputValidator:
    """
    Validates LLM output for safety compliance.
    """
    
    FORBIDDEN_WORDS = {
        # Trading advice
        'buy', 'sell', 'hold', 'recommend', 'target price', 'stop loss',
        # Certainty language
        'guaranteed', 'certain', 'definitely', 'always', 'never',
        # Future predictions
        'will rise', 'will fall', 'will increase', 'will decrease',
        'going to', 'expected to', 'predicted to'
    }
    
    FUTURE_TENSE_PATTERNS = [
        r'\bwill\b(?!\s+have\s+been)',  # "will" except "will have been" (past)
        r'\bshall\b',
        r'\bgoing to\b',
    ]
    
    def validate_output(self, text: str, input_signal_ids: Set[str]) -> Tuple[bool, List[str]]:
        violations = []
        text_lower = text.lower()
        
        # 1. Check forbidden words (with word boundaries to avoid partial matches)
        for word in self.FORBIDDEN_WORDS:
            # Use word boundary regex to avoid "uncertainty" matching "certain"
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text_lower):
                violations.append(f"Forbidden language: '{word}'")
                
        # 2. Check future tense patterns
        for pattern in self.FUTURE_TENSE_PATTERNS:
            if re.search(pattern, text_lower):
                violations.append(f"Future tense pattern detected: {pattern}")
                
        # 3. Check for references to IDs not in input
        # Simple heuristic: look for signal_id mentions
        mentioned_ids = re.findall(r'sig_[a-z0-9]+', text_lower)
        for mid in mentioned_ids:
            if mid not in input_signal_ids:
                violations.append(f"Referenced unknown ID: {mid}")
                
        is_valid = len(violations) == 0
        return is_valid, violations
        
    def get_rejection_reason(self, violations: List[str]) -> str:
        return "Output rejected: " + "; ".join(violations)
