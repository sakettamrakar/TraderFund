"""Momentum Engine Live Runner.

This script orchestrates the momentum engine execution at fixed intervals
during market hours for observation and logging.
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.core_modules.momentum_engine.momentum_engine import MomentumEngine
from observations.signal_logger import ObservationLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MomentumRunner")

def is_market_hours():
    """Simple check for IST market hours (9:15 AM - 3:30 PM)."""
    now = datetime.now()
    # Market open: 09:15, Close: 15:30
    # Dayofweek: 0=Mon, 4=Fri
    if now.weekday() > 4:
        return False
    
    start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return start_time <= now <= end_time

def run_pipeline_step(command, description):
    """Run a subprocess command and log success/failure."""
    import subprocess
    logger.info(f"Stepping: {description}")
    try:
        result = subprocess.run(
            [sys.executable] + command,
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout:
            logger.info(f"OUTPUT ({description}):\n{result.stdout}")
        
        if result.returncode == 0:
            return True
        else:
            logger.error(f"Step '{description}' failed (code {result.returncode})")
            if result.stderr:
                logger.error(f"STDERR:\n{result.stderr}")
            return False
    except Exception as e:
        logger.exception(f"Exception in '{description}': {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="TraderFund Momentum Live Runner")
    parser.add_argument("--interval", type=int, default=5, help="Interval in minutes")
    parser.add_argument("--force", action="store_true", help="Force run outside market hours")
    parser.add_argument("--hod-dist", type=float, default=0.5, help="HOD proximity percentage")
    parser.add_argument("--vol-mult", type=float, default=2.0, help="Volume multiplier")
    parser.add_argument("--symbols", type=str, help="Comma-separated symbols")
    args = parser.parse_args()

    from ingestion.api_ingestion.angel_smartapi.config import AngelConfig
    config = AngelConfig()
    
    if args.symbols:
        watchlist = args.symbols.split(",")
    else:
        watchlist = config.symbol_watchlist
    
    # Initialize engine with provided parameters
    engine = MomentumEngine(
        hod_proximity_pct=args.hod_dist,
        vol_multiplier=args.vol_mult
    )
    obs_logger = ObservationLogger()

    logger.info(f"Starting Momentum Live Runner (Interval: {args.interval}m)")
    logger.info(f"Parameters: HOD Dist {args.hod_dist}%, Vol Mult {args.vol_mult}x")
    logger.info(f"Watchlist: {watchlist}")

    while True:
        if not args.force and not is_market_hours():
            logger.info("Outside market hours. Sleeping...")
            time.sleep(60)
            continue

        loop_start = time.time()
        logger.info("--- Execution Cycle Triggered ---")

        # 1. Trigger Ingestion (Single Cycle)
        ingest_cmd = ["-m", "ingestion.api_ingestion.angel_smartapi.scheduler", "--outside-market-hours", "--single-cycle"]
        if run_pipeline_step(ingest_cmd, "Data Ingestion"):
            
            # 2. Trigger Processing
            process_cmd = ["processing/intraday_candles_processor.py"]
            if run_pipeline_step(process_cmd, "Data Processing"):
                
                # 3. Run Momentum Engine
                logger.info("Running Momentum Engine...")
                signals = engine.run_on_all(watchlist)
                
                if signals:
                    logger.info(f"Generated {len(signals)} signals!")
                    for sig in signals:
                        obs_logger.log_signal(sig.to_dict())
                else:
                    logger.info("No signals generated in this cycle.")
                
                # 4. Generate Executive Dashboard Data
                exec_cmd = ["observations/executive_data_generator.py"]
                run_pipeline_step(exec_cmd, "Executive Dashboard Data Generation")

        # 5. Update API Health Monitor (Always run, even if ingestion fails)
        health_cmd = ["observations/api_health_monitor.py"]
        run_pipeline_step(health_cmd, "API Health Monitoring")

        # Wait for the next interval
        elapsed = time.time() - loop_start
        wait_time = max(0, (args.interval * 60) - elapsed)
        logger.info(f"Cycle completed. Waiting {wait_time:.1f}s for next run.")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()
