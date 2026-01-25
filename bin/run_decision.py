import sys
import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from narratives.repository.parquet_repo import ParquetNarrativeRepository
from signals.core.enums import Market
from src.decision.engine import DecisionEngine
from src.decision.models import Decision
from src.utils.logging import setup_logging

# Setup Logging
logger = setup_logging("RunDecisionCLI", log_dir="logs")

def main():
    parser = argparse.ArgumentParser(description="Run Decision Logic")
    parser.add_argument("--market", default="US", help="Market to process")
    parser.add_argument("--output", default="data/decisions", help="Output directory")
    
    args = parser.parse_args()
    
    market = Market(args.market)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Narratives
    repo = ParquetNarrativeRepository(Path("data/narratives"))
    active_narratives = repo.get_active_narratives(market)
    
    logger.info(f"Loaded {len(active_narratives)} active narratives for {market.value}")
    
    if not active_narratives:
        return

    # 2. Run Engine
    engine = DecisionEngine()
    decisions = engine.evaluate_narratives(active_narratives)
    
    logger.info(f"Generated {len(decisions)} decisions")
    
    # 3. Save Decisions
    for d in decisions:
        filename = f"{d.timestamp.replace(':','-')}_{d.decision_id}.json"
        
        # Determine subfolder by date
        date_folder = output_path / market.value / d.timestamp.split('T')[0]
        date_folder.mkdir(parents=True, exist_ok=True)
        
        filepath = date_folder / filename
        
        with open(filepath, 'w') as f:
            json.dump(d.to_dict(), f, indent=2)
            
        logger.info(f"Saved decision {d.decision_id} ({d.action.value}) to {filepath}")

if __name__ == "__main__":
    main()
