
import os
import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Add project root
sys.path.append(os.getcwd())

# Modules
from ingestion.us_market.ingest_daily import USMarketIngestor
from traderfund.regime.us_market.run_symbol_regime import SymbolRegimeRunner
from traderfund.regime.us_market.market_aggregator import MarketAggregator

# Setup Logging
# Console Handler only for immediate feedback
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("USOrchestrator")

def main():
    print("\n" + "="*60)
    print(" US MARKET REGIME DETECTION PIPELINE (LIVE)")
    print("="*60)
    
    # 1. Ingestion
    print("\n>>> STEP 1: INGESTION")
    ingestor = USMarketIngestor()
    try:
        ingestor.run_all()
    except Exception as e:
        logger.error(f"Ingestion Failed: {e}")
        # Continue? If ingestion fails, we might still have old data.
        
    # 2. Calculation
    print("\n>>> STEP 2: SYMBOL REGIME CALCULATION")
    runner = SymbolRegimeRunner()
    try:
        runner.run_for_symbol("SPY")
        runner.run_for_symbol("QQQ")
        runner.run_for_symbol("IWM")
        runner.run_for_symbol("VIXY")
    except Exception as e:
         logger.error(f"Calculation Failed: {e}")
         return

    # 3. Aggregation
    print("\n>>> STEP 3: MARKET AGGREGATION")
    agg = MarketAggregator()
    try:
        result = agg.aggregate()
        if not result:
            print("Aggregation returned empty result.")
            return

        # 4. Output
        print("\n" + "="*60)
        print(" [US MARKET REGIME] SUMMARY")
        print("="*60)
        print(f" Timestamp:  {result.get('timestamp')}")
        print(f" State:      {result.get('regime')}")
        print(f" Bias:       {result.get('bias')}")
        print(f" Drivers:    {result.get('drivers')}")
        print(f" Coherency:  {result.get('scores')}")
        print("="*60)
        
        # 5. Persistent Log
        log_path = Path("data/us_market/us_market_regime.jsonl")
        with open(log_path, 'a') as f:
            f.write(json.dumps(result) + "\n")
            
        print(f"\nLocked & Logged to: {log_path}")

    except Exception as e:
        logger.error(f"Aggregation Failed: {e}")

if __name__ == "__main__":
    main()
