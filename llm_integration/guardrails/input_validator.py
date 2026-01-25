"""
Input Validation Guardrails.
Ensures only properly structured data reaches the LLM.
"""
from typing import Dict, Any, Tuple

class InputValidator:
    """
    Validates input data before sending to LLM.
    """
    
    REQUIRED_NARRATIVE_FIELDS = [
        'narrative_id', 'market', 'lifecycle_state', 
        'confidence_score', 'explainability_payload'
    ]
    
    REQUIRED_REPORT_FIELDS = [
        'report_id', 'report_type', 'market_scope',
        'period_start', 'period_end'
    ]
    
    def validate_narrative_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        # Check required fields
        for field in self.REQUIRED_NARRATIVE_FIELDS:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        # Check explainability payload exists and is dict
        if not isinstance(data.get('explainability_payload'), dict):
            return False, "explainability_payload must be a dictionary"
            
        # Check confidence is numeric
        conf = data.get('confidence_score')
        if not isinstance(conf, (int, float)):
            return False, "confidence_score must be numeric"
            
        return True, "Valid"
        
    def validate_report_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        for field in self.REQUIRED_REPORT_FIELDS:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        return True, "Valid"
