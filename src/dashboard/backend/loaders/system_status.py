from typing import Dict, Any
from dashboard.backend.loaders.intelligence import load_execution_gate, load_last_evaluation

def load_system_status(market: str = "US") -> Dict[str, Any]:
    """
    Composite status for the dashboard header.
    Binds A1.2 (Gate) and A1.3 (Evaluation) to canonical artifacts.
    """
    gate_data = load_execution_gate()
    eval_data = load_last_evaluation()
    
    return {
        "gate": gate_data.get("gate", {}),
        "last_evaluation": eval_data,
        "trace": {
            "gate_source": gate_data.get("trace", {}).get("source", "UNKNOWN"),
            "ev_source": "docs/intelligence/last_successful_evaluation.json" # Trace for A1.3
        },
        "governance_status": "TE-2026-01-30 [FROZEN]"
    }
