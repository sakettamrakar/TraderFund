"""
Update Global System Postures
=============================
Generates system_stress_posture.json and system_posture.json 
by aggregating market-specific fragility contexts and decision policies.
"""
import sys, json, logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("SystemPostureUpdater")

def _read_json(path):
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def update_postures():
    intel_dir = PROJECT_ROOT / "docs" / "intelligence"
    te_path = PROJECT_ROOT / "docs" / "epistemic" / "truth_epoch.json"
    
    epoch_data = _read_json(te_path).get("epoch", {})
    truth_epoch = epoch_data.get("epoch_id", "TE-UNKNOWN")

    # 1. Stress Posture (from fragility context)
    frag_us = _read_json(intel_dir / "fragility_context_US.json").get("fragility_context", {})
    frag_in = _read_json(intel_dir / "fragility_context_INDIA.json").get("fragility_context", {})
    
    stress_us = frag_us.get("stress_state", "UNKNOWN").upper()
    stress_in = frag_in.get("stress_state", "UNKNOWN").upper()
    
    overall_stress = "NORMAL"
    if "SYSTEMIC" in stress_us or "SYSTEMIC" in stress_in:
        overall_stress = "CRITICAL"
    elif "ELEVATED" in stress_us or "ELEVATED" in stress_in or "STRESS" in stress_us or "STRESS" in stress_in:
        overall_stress = "ELEVATED"

    stress_posture = {
        "system_stress_posture": overall_stress,
        "derived_from": {
            "US": stress_us,
            "INDIA": stress_in
        },
        "truth_epoch": truth_epoch
    }
    
    with open(intel_dir / "system_stress_posture.json", "w", encoding="utf-8") as f:
        json.dump(stress_posture, f, indent=4)
        
    # 2. Constraint Posture (from decision policy / policy state)
    pol_us = _read_json(intel_dir / "decision_policy_US.json").get("policy_decision", {})
    pol_in = _read_json(intel_dir / "decision_policy_INDIA.json").get("policy_decision", {})
    
    pstate_us = pol_us.get("policy_state", "UNKNOWN").upper()
    pstate_in = pol_in.get("policy_state", "UNKNOWN").upper()
    
    # Also fetch final constraints from fragility
    const_us = frag_us.get("constraints_applied", [])
    const_in = frag_in.get("constraints_applied", [])
    
    overall_constraint = "NORMAL"
    if pstate_us in ["HALTED", "OFFLINE"] or pstate_in in ["HALTED", "OFFLINE"]:
        overall_constraint = "HALTED"
    elif pstate_us == "RESTRICTED" or pstate_in == "RESTRICTED" or const_us or const_in:
        overall_constraint = "RESTRICTED"
        
    constraint_posture = {
        "system_constraint_posture": overall_constraint,
        "derived_from": {
            "US": {"permissions": pol_us.get("permissions", []), "state": pstate_us},
            "INDIA": {"permissions": pol_in.get("permissions", []), "state": pstate_in}
        },
        "truth_epoch": truth_epoch
    }
    
    with open(intel_dir / "system_posture.json", "w", encoding="utf-8") as f:
        json.dump(constraint_posture, f, indent=4)
        
    logger.info("Updated global system postures.")

if __name__ == "__main__":
    update_postures()
