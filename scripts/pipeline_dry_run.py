"""TraderFund Pipeline Dry Run.

Orchestrates the end-to-end data pipeline:
1. API Ingestion (Mocked/Single Cycle)
2. Data Processing (Raw -> Parquet)
3. Momentum Engine Execution

Validates system continuity and data lineage.
"""

import subprocess
import os
import sys
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DryRun")

def run_command(command: list, description: str):
    logger.info(f"--- STARTING: {description} ---")
    logger.info(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            logger.info(f"SUCCESS: {description}")
            if result.stdout:
                logger.info(f"Output:\n{result.stdout.strip()}")
        else:
            logger.error(f"FAILURE: {description} (Exit code: {result.returncode})")
            if result.stderr:
                logger.error(f"Error Output:\n{result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        logger.exception(f"Exception during {description}: {e}")
        return False

def check_file_flow():
    """Verify that files are actually being created/updated."""
    raw_path = Path("data/raw/api_based/angel/intraday_ohlc")
    proc_path = Path("data/processed/candles/intraday")
    
    raw_files = list(raw_path.glob("*.jsonl"))
    proc_files = list(proc_path.glob("*.parquet"))
    
    logger.info(f"File Check: {len(raw_files)} raw files found.")
    logger.info(f"File Check: {len(proc_files)} processed files found.")
    
    return len(raw_files) > 0 and len(proc_files) > 0

def main():
    logger.info("Starting Offline Dry Run for TraderFund Pipeline...")
    
    # 1. API Ingestion (External Module)
    # We use single-cycle to avoid hanging. Outside market hours is allowed by flag.
    ingest_cmd = [sys.executable, "-m", "ingestion.api_ingestion.angel_smartapi.scheduler", "--outside-market-hours", "--single-cycle"]
    ingest_success = run_command(ingest_cmd, "Phase 1: API Ingestion")
    
    # 2. Processing (Candle Generation)
    process_cmd = [sys.executable, "processing/intraday_candles_processor.py"]
    process_success = run_command(process_cmd, "Phase 2: Intraday Candle Processing")
    
    # 3. Momentum Engine (Signal Generation)
    momentum_cmd = [sys.executable, "-m", "src.core_modules.momentum_engine.momentum_engine"]
    momentum_success = run_command(momentum_cmd, "Phase 3: Momentum Engine Execution")
    
    # 4. Final Validation
    logger.info("--- FINAL VALIDATION ---")
    files_ok = check_file_flow()
    
    if ingest_success and process_success and momentum_success and files_ok:
        logger.info("PIPELINE DRY RUN COMPLETED SUCCESSFULLY.")
    else:
        logger.error("PIPELINE DRY RUN FAILED IN ONE OR MORE STEPS.")
        sys.exit(1)

if __name__ == "__main__":
    main()
