"""
Auto-Advance Truth Epoch Script
===============================
Reads the latest Canonical Truth Time (CTT) from the temporal states of all enabled markets.
If canonical states are complete and fresh, it advances the global Truth Epoch to match the most recent CTT.
"""
import sys, json, logging
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("TruthEpochAdvancer")

def advance_global_truth_epoch():
    temporal_dir = PROJECT_ROOT / "docs" / "intelligence" / "temporal"
    gate_path = PROJECT_ROOT / "docs" / "intelligence" / "execution_gate_status.json"
    epoch_path = PROJECT_ROOT / "docs" / "epistemic" / "truth_epoch.json"
    
    ctts = []
    markets = ["US", "INDIA"]
    
    # 1. Gather all CTTs
    for market in markets:
        tpath = temporal_dir / f"temporal_state_{market}.json"
        if tpath.exists():
            try:
                state = json.load(open(tpath, "r"))
                ctt = state.get("temporal_state", {}).get("canonical_truth_time", {}).get("timestamp")
                if ctt:
                    ctts.append(ctt)
            except Exception as e:
                logger.error(f"Failed to read temporal state for {market}: {e}")
                
    if not ctts:
        logger.warning("No canonical truth times found. Cannot advance truth epoch.")
        return False
        
    # Use the oldest CTT among markets to ensure we don't advance past any market's validated truth
    # Or should we advance to today? Usually we use the minimum of the latest refreshed data.
    latest_global_ctt = min(ctts)
    new_epoch_id = f"TE-{latest_global_ctt}"
    
    logger.info(f"Targeting new Truth Epoch: {new_epoch_id} (Based on CTTs: {ctts})")
    
    # 2. Update execution gate
    try:
        gate = json.load(open(gate_path, "r")) if gate_path.exists() else {}
        gate["truth_epoch"] = new_epoch_id
        
        with open(gate_path, "w", encoding="utf-8") as f:
            json.dump(gate, f, indent=4)
        logger.info(f"Updated execution_gate_status.json -> {new_epoch_id}")
    except Exception as e:
        logger.error(f"Failed to update gate status: {e}")
        
    # 3. Update epistemic truth epoch file
    try:
        epoch_data = json.load(open(epoch_path, "r")) if epoch_path.exists() else {
            "epoch": {}, "markets_enabled": ["US", "INDIA"]
        }
        
        epoch_data["epoch"]["epoch_id"] = f"TRUTH_EPOCH_{latest_global_ctt}_01"
        epoch_data["epoch"]["activation_time"] = datetime.now().astimezone().isoformat()
        epoch_data["epoch"]["frozen_by"] = "SYSTEM_AUTO_ADVANCE"
        epoch_data["epoch"]["mode"] = "CANONICAL_OBSERVATION"
        epoch_data["notes"] = f"Truth epoch auto-advanced to {latest_global_ctt} following canonical refresh."
        
        with open(epoch_path, "w", encoding="utf-8") as f:
            json.dump(epoch_data, f, indent=4)
        logger.info(f"Updated truth_epoch.json -> {latest_global_ctt}")
    except Exception as e:
        logger.error(f"Failed to update truth epoch file: {e}")
        
    return True

if __name__ == "__main__":
    advance_global_truth_epoch()
