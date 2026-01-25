"""Pipeline Controller - Runner & Orchestrator"""
import argparse
import logging
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from . import config
from .controller import PipelineController
from .models import ActivationDecision

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def update_execution_history(decisions: List[ActivationDecision]):
    """Update the parquet file tracking last runs."""
    history_file = config.EXECUTION_HISTORY_PATH
    history_file.parent.mkdir(parents=True, exist_ok=True)
    
    new_rows = []
    for d in decisions:
        for stage in d.stages_to_run:
            new_rows.append({
                "symbol": d.symbol,
                "stage_id": stage,
                "last_run": d.evaluation_date,
                "version": d.version
            })
    
    if not new_rows:
        return

    new_df = pd.DataFrame(new_rows)
    
    if history_file.exists():
        old_df = pd.read_parquet(history_file)
        # Keep only the latest run per (symbol, stage_id)
        combined = pd.concat([old_df, new_df]).sort_values("last_run", ascending=False)
        final_df = combined.drop_duplicates(subset=["symbol", "stage_id"], keep="first")
    else:
        final_df = new_df
        
    final_df.to_parquet(history_file, index=False)

def execute_stage(stage_id: int, symbols: List[str]):
    """Call the runner of the specific stage."""
    logger.info(f"--- EXECUTING STAGE {stage_id} for {len(symbols)} symbols ---")
    
    sym_str = ",".join(symbols)
    
    try:
        if stage_id == 0:
            from research_modules.universe_hygiene.eligibility_runner import run_eligibility_evaluation
            run_eligibility_evaluation() # S0 usually runs on all or based on its own config
        elif stage_id == 1:
            from research_modules.structural_capability.runner import run_structural_evaluation
            run_structural_evaluation(symbols=symbols)
        elif stage_id == 2:
            from research_modules.energy_setup.runner import run_energy_evaluation
            run_energy_evaluation(symbols=symbols)
        elif stage_id == 3:
            from research_modules.participation_trigger.runner import run_participation_evaluation
            run_participation_evaluation(symbols=symbols)
        elif stage_id == 4:
            from research_modules.momentum_confirmation.runner import run_momentum_evaluation
            run_momentum_evaluation(symbols=symbols)
        elif stage_id == 5:
            from research_modules.sustainability_risk.runner import run_sustainability_evaluation
            run_sustainability_evaluation(symbols=symbols)
    except Exception as e:
        logger.error(f"Failed to execute Stage {stage_id}: {e}")

def run_pipeline_orchestration(symbols: Optional[List[str]] = None, dry_run: bool = False):
    logger.info("=" * 60)
    logger.info("PIPELINE ACTIVATION CONTROLLER - Starting")
    logger.info("=" * 60)
    
    if not symbols:
        # Load from symbol master (Expansion Layer)
        from ingestion.universe_expansion import config as ue_config
        if ue_config.SYMBOL_MASTER_PATH.exists():
             master = pd.read_parquet(ue_config.SYMBOL_MASTER_PATH)
             symbols = master['symbol'].tolist()
        else:
             logger.error("No symbols provided and expansion master missing.")
             return

    controller = PipelineController()
    decisions = []
    
    stage_queue = {i: [] for i in range(6)}

    for sym in symbols:
        decision = controller.decide(sym)
        decisions.append(decision)
        
        if decision.stages_to_run:
            logger.info(f"{sym}: Activate Stages {decision.stages_to_run}")
            for s in decision.stages_to_run:
                stage_queue[s].append(sym)
        else:
            logger.info(f"{sym}: No stages eligible today")

    if dry_run:
        logger.info("DRY RUN COMPLETE. No execution triggered.")
        return

    # Execute in order
    executed = False
    for stage_id in range(6):
        if stage_queue[stage_id]:
            execute_stage(stage_id, stage_queue[stage_id])
            executed = True

    # Update history
    update_execution_history(decisions)
    
    logger.info("=" * 60)
    logger.info("PIPELINE ACTIVATION CONTROLLER - Complete")
    logger.info("=" * 60)
    
    if not executed:
        return {"status": "NO_OP", "reason": "no stages triggered"}
    return {"status": "SUCCESS"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Run the controller")
    parser.add_argument("--symbols", type=str, help="Comma separated symbols")
    parser.add_argument("--dry-run", action="store_true", help="Determine plan without execution")
    args = parser.parse_args()

    if not args.run:
        parser.print_help()
        sys.exit(0)

    symbols = args.symbols.split(",") if args.symbols else None
    run_pipeline_orchestration(symbols, args.dry_run)

if __name__ == "__main__":
    main()
