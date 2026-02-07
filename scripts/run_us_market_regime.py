
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
        
        # 6. Parity Status Generation
        print("\n>>> STEP 4: PARITY STATUS GENERATION")
        
        # Inline proxy check to avoid import hell between src/ingestion and root/ingestion
        proxy_config_path = Path("src/structural/market_proxy_instance.json")
        if not proxy_config_path.exists():
            logger.error(f"Missing Proxy Config: {proxy_config_path}")
            return

        with open(proxy_config_path, "r") as f:
            proxy_config = json.load(f)
            
        us_config = proxy_config.get("US", {})
        bindings = us_config.get("ingestion_binding", {})
        
        parity_result = {
            "market": "US",
            "computed_at": datetime.now().isoformat(),
            "truth_epoch": "TE-UNKNOWN",
            "parity_status": "CANONICAL",
            "proxy_diagnostics": {},
            "gaps": [],
            "canonical_ready": True
        }
        
        # Load Truth Epoch
        try:
            with open("docs/epistemic/truth_epoch.json", "r") as f:
                te = json.load(f)
                parity_result["truth_epoch"] = te.get("epoch", {}).get("epoch_id", "TE-UNKNOWN")
        except:
            pass

        # Inspect binding
        roles = ["equity_core", "growth_proxy", "volatility_gauge", "rates_anchor"]
        # Map roles to keys in ingestion_binding
        # Based on market_proxy_instance.json: SPY, QQQ, VIXY, TNX
        # We need to map role -> binding_key. 
        # The structure is: roles -> list of keys.
        
        role_def = us_config.get("roles", {})
        
        for role in roles:
            keys = role_def.get(role, [])
            if not keys:
               parity_result["gaps"].append(role)
               continue
            
            # Take primary
            primary_key = keys[0]
            rel_path = bindings.get(primary_key)
            
            if not rel_path:
                parity_result["gaps"].append(role)
                continue
                
            p = Path(rel_path)
            status = "ACTIVE"
            rows = 0
            
            if p.exists():
                try:
                    import pandas as pd
                    df = pd.read_csv(p)
                    rows = len(df)
                    # Simple Freshness Check (Last 3 days)
                    last_date = pd.to_datetime(df['timestamp'].iloc[-1])
                    if (datetime.now() - last_date).days > 3:
                        status = "STALE"
                except:
                    status = "ERROR"
            else:
                status = "MISSING"
                parity_result["canonical_ready"] = False
                
            parity_result["proxy_diagnostics"][role] = {
                "status": status,
                "role": role,
                "symbol": primary_key,
                "source": "Yahoo Finance (AlphaVantage)",
                "provenance": "REAL",
                "path": str(p),
                "rows": rows,
                "staleness": "NONE" if status == "ACTIVE" else "HIGH"
            }
            
        # Write
        out_path = Path("docs/intelligence/market_parity_status_US.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(parity_result, f, indent=4)
            
        print(f"Parity Status Updated: {out_path}")

    except Exception as e:
        logger.error(f"Aggregation Failed: {e}")

if __name__ == "__main__":
    main()
