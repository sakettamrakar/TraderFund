"""
EV-TICK Start Script.
Invoked by CRON to advance system time passively.
"""
import sys
import time
from pathlib import Path

# Setup Path to import from src AND root 
# CRITICAL: PROJECT_ROOT must be at index 0 (first) because root-level 
# 'ingestion.api_ingestion' must not be shadowed by 'src/ingestion/'
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from evolution.orchestration.ev_tick import EvTickOrchestrator

def main():
    # Output to a rolling tick directory
    ts = int(time.time())
    out_dir = PROJECT_ROOT / "docs" / "evolution" / "ticks" / f"tick_{ts}"
    
    orchestrator = EvTickOrchestrator(out_dir)
    orchestrator.execute()

if __name__ == "__main__":
    main()
