import os
import glob
from pathlib import Path
from src.utils.logging import setup_logging

# Setup Logging
logger = setup_logging("MonitorTrigger", log_dir="logs")

def check_inbox(inbox_path: str = "data/events/inbox") -> int:
    """Check for pending events in inbox."""
    files = glob.glob(os.path.join(inbox_path, "*.json"))
    count = len(files)
    if count > 0:
        logger.info(f"[SUGGESTION] Found {count} pending events in {inbox_path}", extra={"suggestion": "Run bin/run_narrative.py"})
    else:
        logger.debug(f"Inbox {inbox_path} is empty.")
    return count

def check_decision_gap(narrative_path: str = "data/narratives", decision_path: str = "data/decisions") -> int:
    """Check if there are narratives without decisions."""
    # This is a naive check (file counts). A robust one would match IDs.
    # For prototype, we just count.
    
    n_files = len(glob.glob(os.path.join(narrative_path, "**/*.json"), recursive=True))
    d_files = len(glob.glob(os.path.join(decision_path, "**/*.json"), recursive=True))
    
    gap = n_files - d_files
    
    if gap > 0:
        logger.info(f"[SUGGESTION] Found {gap} potential unconnected narratives ({n_files} vs {d_files})", extra={"suggestion": "Run bin/run_decision.py"})
    elif gap < 0:
         logger.warning(f"Orphaned Decisions detected? Narratives: {n_files}, Decisions: {d_files}")
    else:
        logger.debug("Narrative-Decision parity OK.")
        
    return gap

def main():
    logger.info("Starting Passive Monitor Scan...")
    
    # 1. Inbox Check
    check_inbox()
    
    # 2. Decision Gap Check
    try:
        check_decision_gap()
    except Exception as e:
        logger.error(f"Error checking decision gap: {e}")
        
    logger.info("Monitor Scan Complete.")

if __name__ == "__main__":
    main()
