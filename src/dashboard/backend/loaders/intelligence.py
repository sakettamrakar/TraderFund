import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from dashboard.backend.loaders.provenance import attach_provenance, load_truth_epoch_id

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

def _read_json_safe(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def load_intelligence_snapshot(market: str = "US") -> Dict[str, Any]:
    """
    Loads the latest intelligence snapshot for the requested market.
    """
    # Assuming daily filenames: intelligence_{market}_{YYYY-MM-DD}.json
    # We want the *latest* one.
    snapshot_dir = PROJECT_ROOT / "docs" / "intelligence" / "snapshots"
    if not snapshot_dir.exists():
        return {"error": "No snapshots found", "market": market}
        
    # Find files matching pattern
    pattern = f"intelligence_{market}_*.json"
    files = list(snapshot_dir.glob(pattern))
    
    if not files:
        return attach_provenance({"error": f"No data for {market}", "signals": [], "market": market}, f"docs/intelligence/snapshots/intelligence_{market}_*.json")
        
    # Sort by name (which includes date) desc
    latest_file = sorted(files, key=lambda x: x.name, reverse=True)[0]
    
    payload = _read_json_safe(latest_file)
    return attach_provenance(payload, f"docs/intelligence/snapshots/{latest_file.name}")

def load_decision_policy(market: str) -> Dict[str, Any]:
    """
    Loads proper Decision Policy Artifact.
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / f"decision_policy_{market}.json"
    if not path.exists():
        return attach_provenance({
            "policy_decision": {
                "market": market,
                "policy_state": "OFFLINE",
                "permissions": [],
                "blocked_actions": [],
                "reason": "Policy artifact not found on disk.",
                "epistemic_health": {"grade": "UNKNOWN", "proxy_status": "UNKNOWN"}
            }
        }, f"docs/intelligence/decision_policy_{market}.json")
    return attach_provenance(_read_json_safe(path), f"docs/intelligence/decision_policy_{market}.json")

def load_fragility_context(market: str) -> Dict[str, Any]:
    """
    Loads proper Fragility Context Artifact.
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / f"fragility_context_{market}.json"
    if not path.exists():
        return attach_provenance({
            "fragility_context": {
                "market": market,
                "stress_state": "UNKNOWN",
                "constraints_applied": [],
                "final_authorized_intents": [],
                "reason": "Fragility artifact not found on disk."
            }
        }, f"docs/intelligence/fragility_context_{market}.json")
    return attach_provenance(_read_json_safe(path), f"docs/intelligence/fragility_context_{market}.json")

def load_execution_gate() -> Dict[str, Any]:
    """
    Loads the canonical Execution Gate Status artifact (A1.2).
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / "execution_gate_status.json"
    if not path.exists():
        return attach_provenance({
            "execution_gate": "UNKNOWN",
            "reasons": ["ARTIFACT_MISSING", "EXECUTION_BLOCKED"],
            "truth_epoch": "UNKNOWN"
        }, "docs/intelligence/execution_gate_status.json")
    
    data = _read_json_safe(path)
    # Add a trace field for auditing as per OBL-DATA-PROVENANCE-VISIBLE
    return attach_provenance({
        "gate": data,
        "trace": {
            "source": "docs/intelligence/execution_gate_status.json",
            "layer": "GOVERNANCE",
            "role": "SYSTEM_LOCK"
        }
    }, "docs/intelligence/execution_gate_status.json", data.get("truth_epoch") or load_truth_epoch_id())

def load_last_evaluation() -> Dict[str, Any]:
    """
    Loads the last successful evaluation timestamp (A1.3).
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / "last_successful_evaluation.json"
    if not path.exists():
        return attach_provenance({
            "last_successful_evaluation": "NONE",
            "truth_epoch": "UNKNOWN"
        }, "docs/intelligence/last_successful_evaluation.json")
    return attach_provenance(_read_json_safe(path), "docs/intelligence/last_successful_evaluation.json")

def load_stress_posture() -> Dict[str, Any]:
    """
    Loads systemic stress posture (A2.1).
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / "system_stress_posture.json"
    data = _read_json_safe(path) if path.exists() else {"system_stress_posture": "UNKNOWN"}
    return attach_provenance({
        "posture": data,
        "trace": {"source": "docs/intelligence/system_stress_posture.json"}
    }, "docs/intelligence/system_stress_posture.json")

def load_constraint_posture() -> Dict[str, Any]:
    """
    Loads systemic constraint posture (A2.2).
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / "system_posture.json"
    data = _read_json_safe(path) if path.exists() else {"system_constraint_posture": "UNKNOWN"}
    return attach_provenance({
        "posture": data,
        "trace": {"source": "docs/intelligence/system_posture.json"}
    }, "docs/intelligence/system_posture.json")

def load_evaluation_scope() -> Dict[str, Any]:
    """
    Loads market evaluation scope (A3.1).
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / "market_evaluation_scope.json"
    data = _read_json_safe(path) if path.exists() else {"evaluated_markets": []}
    return attach_provenance({
        "scope": data,
        "trace": {"source": "docs/intelligence/market_evaluation_scope.json"}
    }, "docs/intelligence/market_evaluation_scope.json")

def load_market_parity(market: str) -> Dict[str, Any]:
    """
    Loads market parity status (A1.1 / A3.2).
    """
    path = PROJECT_ROOT / "docs" / "intelligence" / f"market_parity_status_{market}.json"
    data = _read_json_safe(path) if path.exists() else {"market": market, "parity_status": "UNKNOWN"}
    return attach_provenance({
        "parity": data,
        "trace": {"source": f"docs/intelligence/market_parity_status_{market}.json"}
    }, f"docs/intelligence/market_parity_status_{market}.json")
