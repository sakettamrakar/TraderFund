"""Pipeline Controller - Models"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class ActivationDecision:
    symbol: str
    evaluation_date: str
    stages_to_run: List[int]
    stages_skipped: Dict[int, str]
    triggering_conditions: List[str]
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "evaluation_date": self.evaluation_date,
            "stages_to_run": self.stages_to_run,
            "stages_skipped": self.stages_skipped,
            "triggering_conditions": self.triggering_conditions,
            "version": self.version,
        }

@dataclass
class SymbolState:
    symbol: str
    last_run: Dict[str, str] = field(default_factory=dict) # stage_id: iso_date
    last_score: Dict[str, float] = field(default_factory=dict) # stage_id: score
    last_state: Dict[str, str] = field(default_factory=dict) # stage_id: state
