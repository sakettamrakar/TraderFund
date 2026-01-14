"""
LLM Kill Switches.
Allows instant disabling of LLM features without code changes.
"""

class LLMSwitches:
    # Global LLM Switch
    LLM_ENABLED: bool = True
    
    # Per-Feature Switches
    NARRATIVE_EXPLANATION_ENABLED: bool = True
    REPORT_EXPLANATION_ENABLED: bool = True
    QUERY_EXPLANATION_ENABLED: bool = True
    
    # Fallback Message
    FALLBACK_MESSAGE: str = "No explanation available. LLM feature is disabled."
    
    @classmethod
    def disable_all(cls):
        cls.LLM_ENABLED = False
        print("ALERT: All LLM features disabled.")
        
    @classmethod
    def enable_all(cls):
        cls.LLM_ENABLED = True
        print("INFO: LLM features re-enabled.")
        
    @classmethod
    def is_enabled(cls, feature: str = "global") -> bool:
        if not cls.LLM_ENABLED:
            return False
            
        if feature == "narrative":
            return cls.NARRATIVE_EXPLANATION_ENABLED
        elif feature == "report":
            return cls.REPORT_EXPLANATION_ENABLED
        elif feature == "query":
            return cls.QUERY_EXPLANATION_ENABLED
            
        return cls.LLM_ENABLED
        
    @classmethod
    def status(cls) -> dict:
        return {
            "global": cls.LLM_ENABLED,
            "narrative": cls.NARRATIVE_EXPLANATION_ENABLED,
            "report": cls.REPORT_EXPLANATION_ENABLED,
            "query": cls.QUERY_EXPLANATION_ENABLED
        }
