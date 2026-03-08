from typing import Dict, Any
from dashboard.backend.loaders.intelligence import load_execution_gate, load_last_evaluation
from dashboard.backend.loaders.provenance import attach_provenance, load_truth_epoch_id

def load_system_status(market: str = "US") -> Dict[str, Any]:
    """
    Composite status for the dashboard header.
    Binds A1.2 (Gate) and A1.3 (Evaluation) to canonical artifacts.
    """
    gate_data = load_execution_gate()
    eval_data = load_last_evaluation()
    
    truth_epoch = load_truth_epoch_id()
    gate_payload = dict(gate_data.get("gate", {}))
    gate_payload["truth_epoch"] = truth_epoch
    return attach_provenance({
        "gate": gate_payload,
        "last_evaluation": eval_data,
        "trace": {
            "gate_source": gate_data.get("trace", {}).get("source", "UNKNOWN"),
            "ev_source": "docs/intelligence/last_successful_evaluation.json"
        },
        "governance_status": f"{truth_epoch} [FROZEN]",
        "truth_epoch": truth_epoch,
    }, "docs/intelligence/execution_gate_status.json", truth_epoch)
