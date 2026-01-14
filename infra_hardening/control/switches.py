"""
Global Kill Switches for TraderFund System.
These switches allow instant disabling of specific layers without code changes.
"""

class SystemSwitches:
    # Layer Switches
    INGESTION_ENABLED: bool = True
    SIGNAL_GENERATION_ENABLED: bool = True
    NARRATIVE_GENESIS_ENABLED: bool = True
    REPORT_GENERATION_ENABLED: bool = True
    SANDBOX_ENABLED: bool = True
    
    # Mode Switches
    READ_ONLY_MODE: bool = False  # If True, no writes to any persistence layer
    GRACEFUL_DEGRADATION: bool = True # If True, failures are logged but don't crash
    
    @classmethod
    def disable_all_writes(cls):
        cls.READ_ONLY_MODE = True
        print("ALERT: System is now in READ-ONLY mode.")
        
    @classmethod
    def enable_all_writes(cls):
        cls.READ_ONLY_MODE = False
        print("INFO: System writes re-enabled.")
        
    @classmethod
    def kill_sandbox(cls):
        cls.SANDBOX_ENABLED = False
        print("ALERT: Sandbox layer disabled.")
        
    @classmethod
    def status(cls) -> dict:
        return {
            "ingestion": cls.INGESTION_ENABLED,
            "signals": cls.SIGNAL_GENERATION_ENABLED,
            "narratives": cls.NARRATIVE_GENESIS_ENABLED,
            "reports": cls.REPORT_GENERATION_ENABLED,
            "sandbox": cls.SANDBOX_ENABLED,
            "read_only": cls.READ_ONLY_MODE,
            "graceful_degradation": cls.GRACEFUL_DEGRADATION
        }
