import argparse
import os
import sys
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("RegimeWrapper")

def main():
    parser = argparse.ArgumentParser(description="Market Regime Engine - Production Wrapper")
    parser.add_argument("--mode", required=True, choices=["OFF", "SHADOW", "ENFORCED", "ANALYTICS"],
                       help="Operating mode for the Regime Engine")
    parser.add_argument("--target", default="observations/india_momentum_runner.py",
                       help="Target strategy runner script to launch (for SHADOW/ENFORCED)")
    
    args = parser.parse_args()
    
    mode = args.mode.upper()
    logger.info(f" initializing Regime Engine Wrapper in {mode} mode")
    
    # 1. ANALYTICS MODE
    if mode == "ANALYTICS":
        logger.info("Starting Offline Regret Analysis...")
        try:
            from traderfund.regime.regret_analysis import RegimeRegretAnalyzer
            analyzer = RegimeRegretAnalyzer()
            # Paths hardcoded to match default ShadowRunner output for MVP
            regime_log = "regime_shadow.jsonl"
            signal_log = "logs/momentum_signals.csv" # Hypothetical
            
            if not os.path.exists(regime_log):
                logger.error(f"Regime log not found at {regime_log}")
                sys.exit(1)
                
            logger.info("Loading data...")
            # For this runbook implementation, we assume logs exist.
            # In production, specific paths would be config driven.
            logger.info("Analysis Complete. (This is a placeholder wrapper implementation for the Analyzer class)")
            # analyzer.run_full_report() # Logic to be added if specific entry point exists
        except ImportError:
            logger.error("Could not import RegimeRegretAnalyzer")
        sys.exit(0)

    # 2. RUNTIME MODES (OFF, SHADOW, ENFORCED)
    
    # Set Environment Variable
    os.environ["REGIME_MODE"] = mode
    logger.info(f"Environment set: REGIME_MODE={mode}")
    
    target_script = Path(args.target)
    if not target_script.exists():
        logger.error(f"Target script not found: {target_script}")
        sys.exit(1)
        
    cmd = [sys.executable, str(target_script)]
    
    logger.info(f"Launching target: {' '.join(cmd)}")
    logger.info("------------------------------------------------")
    
    try:
        # Launch subprocess
        # checks=False allows usage in scripts even if target fails
        process = subprocess.Popen(cmd, env=os.environ.copy())
        
        # Monitor
        process.wait()
        
        logger.info(f"Target process exited with code {process.returncode}")
        sys.exit(process.returncode)
        
    except KeyboardInterrupt:
        logger.info("Wrapper received SIGINT. Stopping target...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Wrapper Execution Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
