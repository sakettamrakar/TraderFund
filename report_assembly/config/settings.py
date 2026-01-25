from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AssemblyConfig:
    # Inclusion Thresholds
    MIN_NARRATIVE_CONFIDENCE: float = 30.0
    MIN_SIGNAL_SEVERITY: float = 0.5
    
    # Ordering Weights
    WEIGHT_CONFIDENCE: float = 0.6
    WEIGHT_RECENCY: float = 0.4
    
    # Limits
    MAX_NARRATIVES_DAILY: int = 5
    MAX_NARRATIVES_WEEKLY: int = 10
    
    # Partial Data
    ALLOW_PARTIAL_DATA: bool = True
    MIN_NARRATIVES_REQUIRED: int = 0  # Allow empty reports
    
    @classmethod
    def default(cls) -> 'AssemblyConfig':
        return cls()
