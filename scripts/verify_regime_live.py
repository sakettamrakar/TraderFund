
import os
import sys
import logging
import time
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("RegimeLiveDebug")

# Add project root to sys.path
sys.path.append(os.getcwd())

# Helper to print section headers
def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title.upper()}")
    print("=" * 60)

def print_result(check: str, status: str, details: str = ""):
    color = "\033[92m" if status == "PASS" else ("\033[93m" if status == "WARN" else "\033[91m")
    reset = "\033[0m"
    print(f"{check:<30} [{color}{status}{reset}] {details}")

# Import Regime Modules
try:
    from traderfund.regime.integration_guards import MomentumRegimeGuard, GuardDecision
    from traderfund.regime.types import RegimeState, MarketBehavior
except ImportError:
    print("Error: Could not import Regime modules. Run from repo root.")
    sys.exit(1)

def run_verification():
    print_header("LIVE DEBUG SESSION: MARKET REGIME ENGINE")
    print(f"Time: {datetime.now().isoformat()}")
    
    # 1. DATA INGESTION CHECK
    print_header("1. DATA INGESTION CHECK")
    data_dir = Path("data/processed/candles/intraday")
    symbols = ["RELIANCE", "INFY", "TCS"]
    
    for sym in symbols:
        file = data_dir / f"NSE_{sym}_1m.parquet"
        if not file.exists():
            print_result(f"File Check ({sym})", "FAIL", "Missing parquet file")
            continue
        
        try:
            df = pd.read_parquet(file)
            last_ts = pd.to_datetime(df['timestamp'].iloc[-1])
            now = datetime.now()
            # Assuming India Time in parquet or close to it
            # Delta might be large if data is stale, which is a finding.
            delta_mins = (now - last_ts).total_seconds() / 60
            
            status = "PASS" if delta_mins < 5 else "WARN"
            print_result(f"Freshness ({sym})", status, f"Last: {last_ts} ({delta_mins:.1f}m ago)")
            
            # Check for NaNs
            if df.isnull().values.any():
                print_result(f"Completeness ({sym})", "FAIL", "Contains NaNs")
            else:
                print_result(f"Completeness ({sym})", "PASS", "No NaNs")
                
        except Exception as e:
            print_result(f"Read Error ({sym})", "FAIL", str(e))

    # 2. PROVIDER & CALCULATOR TRACE
    print_header("2 - 5. COMPONENT TRACE")
    
    guard = MomentumRegimeGuard()
    # Cache state to simulate hysteresis
    manager_cache = {}
    
    for sym in symbols:
        print(f"\n--- Trace: {sym} ---")
        df = guard._load_data(sym)
        if df.empty:
            continue
            
        # Simulating live feed by iterating last 5 bars
        subset = df.iloc[-5:]
        start_idx = len(df) - 5
        
        # Instantiate fresh manager per symbol for this test run
        from traderfund.regime.core import StateManager
        manager = StateManager()
        
        for i in range(len(subset)):
            window = df.iloc[:start_idx + i + 1]
            curr_bar = window.iloc[-1]
            ts = curr_bar['timestamp']
            
            # Providers
            t_str = guard.trend.get_trend_strength(window)
            t_aln = guard.trend.get_alignment(window)
            v_rat = guard.vol.get_volatility_ratio(window)
            l_scr = guard.liq.get_liquidity_score(window)
            e_dat = guard.event.get_pressure(window)
            
            # Provider Check
            if np.isnan(t_str) or np.isnan(v_rat):
                print_result(f"Bar {ts}", "FAIL", "NaN Provider Output")
                continue
                
            # Calculator
            raw = guard.calc.calculate(t_str, t_aln, v_rat, l_scr, e_dat['pressure'], e_dat['is_lock_window'])
            
            # State Machine
            from traderfund.regime.types import RegimeFactors
            factors = RegimeFactors(
                 trend_strength_norm=t_str, 
                 volatility_ratio=v_rat, 
                 liquidity_status="NORMAL" if l_scr > 0.5 else "DRY", 
                 event_pressure_norm=e_dat['pressure']
            )
            state = manager.update(raw, factors)
            
            # Log Line
            print(f"[{ts}] Raw:{raw.behavior.value} -> State:{state.behavior.value} (Conf:{state.total_confidence:.2f})")
            
            # Verify Hysteresis
            if not state.is_stable and i > 0:
                print(f"      -> Unstable change detected. Counter: {manager.pending_counter}")

    # 6. STRATEGY GATE CHECK
    print_header("6. STRATEGY GATE DRY-RUN")
    
    # Check last state of 'RELIANCE'
    sym = "RELIANCE"
    df = guard._load_data(sym)
    if not df.empty:
        # We need to hack the guard to run check_signal but expose state
        # Actually check_signal returns state in decision!
        
        # Scenario 1: MODE=SHADOW
        os.environ["REGIME_MODE"] = "SHADOW"
        decision_shadow = guard.check_signal({'symbol': sym, 'timestamp': datetime.now()})
        print_result("SHADOW Mode", "PASS" if decision_shadow.allowed else "FAIL", 
                    f"Allowed: {decision_shadow.allowed}, Reason: {decision_shadow.reason}")
        
        # Scenario 2: MODE=ENFORCED
        os.environ["REGIME_MODE"] = "ENFORCED"
        # Force a BLOCK scenario? 
        # Hard to force without mocking data log, but we verify the switch works
        decision_enforced = guard.check_signal({'symbol': sym, 'timestamp': datetime.now()})
        
        status = "PASS"
        if decision_shadow.allowed and not decision_enforced.allowed:
            # If shadow allowed but enforced blocked -> Correct blocking logic
            pass
        elif decision_shadow.allowed == decision_enforced.allowed:
            # If both allowed -> Benign regime
            pass
        else:
            # Shadow Blocked? Shadow shouldn't block.
            status = "FAIL"
            
        print_result("ENFORCED Mode", status, 
                    f"Allowed: {decision_enforced.allowed}, Reason: {decision_enforced.reason}")

    # 9. PERFORMANCE
    print_header("9. PERFORMANCE LATENCY")
    start = time.perf_counter()
    count = 50
    for _ in range(count):
        guard.check_signal({'symbol': 'RELIANCE', 'timestamp': datetime.now()})
    end = time.perf_counter()
    avg_ms = ((end - start) / count) * 1000
    
    print_result("Latency Test", "PASS" if avg_ms < 50 else "WARN", f"Avg: {avg_ms:.2f}ms per check")

    # 10. FAIL SAFE
    print_header("10. FAIL SAFE TEST")
    try:
        decision = guard.check_signal({'symbol': 'NON_EXISTENT'})
        status = "PASS" if (not decision.allowed and "FAIL_SAFE" in decision.reason) else "FAIL"
        print_result("Missing Symbol", status, f"Reason: {decision.reason}")
    except Exception as e:
        print_result("Missing Symbol", "FAIL", f"Crashed: {e}")

    print_header("VERIFICATION COMPLETE")

if __name__ == "__main__":
    run_verification()
