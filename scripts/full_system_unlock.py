"""
Full System Unlock Script
=========================
Refreshes ALL stale data, re-runs ev_tick, updates temporal state,
re-computes governance, and verifies dashboard readiness.

This script is the SINGLE ENTRY POINT for bringing the system up to date.

Pipeline Steps:
1. Refresh regime detection anchors (yfinance: SPY, QQQ, VIX, HYG, LQD, ^TYX)
2. Refresh US market dailies (ingest_daily.py: SPY, QQQ, IWM, VIXY, TNX)
3. Refresh India IN10Y rates (FRED monthly)
4. Update temporal state (temporal_orchestrator)
5. Run evolution tick (ev_tick)
6. Re-compute governance (suppression, narrative)
7. Verify system state
"""
import sys
import os
import json
import time
import traceback
import importlib.util
from pathlib import Path
from datetime import datetime
import logging

PROJECT_ROOT = Path(__file__).parent.parent
for entry in (str(PROJECT_ROOT), str(PROJECT_ROOT / "src")):
    if entry in sys.path:
        sys.path.remove(entry)
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(1, str(PROJECT_ROOT / "src"))

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "logs" / "full_system_unlock.log", mode="a"),
    ],
)
logger = logging.getLogger("SystemUnlock")

RESULTS = {"timestamp": datetime.now().isoformat(), "steps": {}, "summary": {}}


def _load_us_market_ingestor_class():
    for entry in (str(PROJECT_ROOT), str(PROJECT_ROOT / "src")):
        if entry in sys.path:
            sys.path.remove(entry)
    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(1, str(PROJECT_ROOT / "src"))
    try:
        from ingestion.us_market.ingest_daily import USMarketIngestor

        return USMarketIngestor
    except Exception:
        module_path = PROJECT_ROOT / "ingestion" / "us_market" / "ingest_daily.py"
        spec = importlib.util.spec_from_file_location("traderfund_us_ingest_daily", module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load US market ingestor from {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.USMarketIngestor


def step(name):
    """Decorator for step tracking."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info("=" * 60)
            logger.info(f"STEP: {name}")
            logger.info("=" * 60)
            try:
                result = func(*args, **kwargs)
                RESULTS["steps"][name] = {"status": "PASS", "result": result}
                logger.info(f"  ✅ {name}: PASS")
                return result
            except Exception as e:
                RESULTS["steps"][name] = {"status": "FAIL", "error": str(e)}
                logger.error(f"  ❌ {name}: FAIL - {e}")
                logger.error(traceback.format_exc())
                return None
        return wrapper
    return decorator


# ============================================================
# STEP 1: Refresh regime detection anchors via yfinance
# ============================================================
@step("1_regime_anchor_refresh")
def refresh_regime_anchors():
    """Refresh the 6 stale regime detection files from yfinance."""
    import yfinance as yf

    REGIME_DIR = PROJECT_ROOT / "data" / "regime" / "raw"
    REGIME_DIR.mkdir(parents=True, exist_ok=True)

    symbols = {
        "SPY": "SPY", "QQQ": "QQQ", "VIX": "^VIX",
        "HYG": "HYG", "LQD": "LQD", "^TYX": "^TYX",
    }

    results = {}
    for file_sym, yf_sym in symbols.items():
        out_path = REGIME_DIR / f"{file_sym}.csv"

        # Load existing data to determine start date
        start_date = "2021-01-01"
        if out_path.exists():
            try:
                existing = pd.read_csv(out_path)
                if "date" in existing.columns:
                    last = pd.to_datetime(existing["date"]).max()
                    # Overlap by 3 days to catch corrections
                    start_date = (last - pd.Timedelta(days=3)).strftime("%Y-%m-%d")
            except Exception:
                pass

        logger.info(f"  Fetching {yf_sym} from {start_date}...")
        try:
            df = yf.download(yf_sym, start=start_date, progress=False, auto_adjust=False)
            if df.empty:
                logger.warning(f"  ⚠️ {yf_sym}: No data returned")
                results[file_sym] = {"status": "EMPTY", "rows": 0}
                continue

            # Handle MultiIndex columns from yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.reset_index().rename(columns={
                "Date": "date", "Open": "open", "High": "high",
                "Low": "low", "Close": "close", "Volume": "volume",
            })
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
            df["symbol"] = file_sym if not file_sym.startswith("^") else file_sym
            df = df[["date", "symbol", "open", "high", "low", "close", "volume"]].dropna(subset=["date"])

            # Merge with existing if present
            if out_path.exists():
                try:
                    existing = pd.read_csv(out_path)
                    existing["date"] = pd.to_datetime(existing["date"])
                    df = pd.concat([existing, df])
                except Exception:
                    pass

            # Deduplicate and sort
            df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
            df.to_csv(out_path, index=False)

            last_date = df["date"].max()
            results[file_sym] = {
                "status": "OK",
                "rows": len(df),
                "last_date": str(last_date.date()) if pd.notna(last_date) else None,
            }
            logger.info(f"  ✅ {file_sym}: {len(df)} rows → {last_date.date()}")

        except Exception as e:
            logger.error(f"  ❌ {file_sym}: {e}")
            results[file_sym] = {"status": "ERROR", "error": str(e)}

        time.sleep(0.5)  # Gentle pacing

    return results


# ============================================================
# STEP 2: Refresh US market dailies
# ============================================================
@step("2_us_daily_refresh")
def refresh_us_dailies():
    """Run existing US daily ingestor."""
    USMarketIngestor = _load_us_market_ingestor_class()
    ingestor = USMarketIngestor()
    ingestor.run_all()

    # Check results
    results = {}
    files = {
        "SPY": PROJECT_ROOT / "data/us_market/SPY_daily.csv",
        "QQQ": PROJECT_ROOT / "data/us_market/QQQ_daily.csv",
        "IWM": PROJECT_ROOT / "data/us_market/IWM_daily.csv",
        "VIXY": PROJECT_ROOT / "data/us_market/VIXY_daily.csv",
        "TNX": PROJECT_ROOT / "data/regime/raw/^TNX.csv",
    }
    for sym, path in files.items():
        if path.exists():
            df = pd.read_csv(path)
            date_col = "date" if sym == "TNX" else "timestamp"
            if date_col in df.columns:
                last = pd.to_datetime(df[date_col]).max()
                results[sym] = {"rows": len(df), "last_date": str(last.date())}
    return results


# ============================================================
# STEP 3: Refresh India IN10Y from FRED
# ============================================================
@step("3_india_in10y_refresh")
def refresh_india_in10y():
    """Refresh India 10Y rate from FRED."""
    from scripts.india_in10y_fred_ingestion import ingest_india_10y
    output_path = ingest_india_10y()
    df = pd.read_csv(output_path, parse_dates=["Date"])
    return {"rows": len(df), "last_date": str(df["Date"].max().date()), "path": str(output_path)}


# ============================================================
# STEP 4: Update temporal state
# ============================================================
@step("4_temporal_state_update")
def update_temporal_state():
    """Run temporal orchestrator to update RDT/CTT."""
    from scripts.temporal_orchestrator import TemporalOrchestrator

    orch = TemporalOrchestrator()
    results = {}
    for market in ["US", "INDIA"]:
        state = orch.update_rdt_ctt(market)
        ts = state.get("temporal_state", {})
        ds = state.get("drift_status", {})
        results[market] = {
            "rdt": ts.get("raw_data_time", {}).get("timestamp"),
            "ctt": ts.get("canonical_truth_time", {}).get("timestamp"),
            "te": ts.get("truth_epoch", {}).get("timestamp"),
            "drift_days": ds.get("evaluation_drift_days"),
            "drift_status": ds.get("status_code"),
        }
        logger.info(f"  [{market}] RDT={results[market]['rdt']} CTT={results[market]['ctt']} "
                     f"TE={results[market]['te']} drift={results[market]['drift_days']}d "
                     f"status={results[market]['drift_status']}")
    return results


# ============================================================
# STEP 5: Run evolution tick
# ============================================================
@step("5_evolution_tick")
def run_evolution_tick():
    """Run ev_tick to regenerate all intelligence artifacts."""
    from evolution.orchestration.ev_tick import EvTickOrchestrator

    ts = int(time.time())
    out_dir = PROJECT_ROOT / "docs" / "evolution" / "ticks" / f"tick_{ts}"
    orchestrator = EvTickOrchestrator(out_dir)
    orchestrator.execute()

    # Verify outputs
    results = {"tick_id": f"tick_{ts}", "markets": {}}
    for market in ["US", "INDIA"]:
        market_dir = out_dir / market
        if market_dir.exists():
            files = [f.name for f in market_dir.iterdir() if f.is_file()]
            results["markets"][market] = {"files": len(files), "file_list": files}

            # Read regime context
            rc_path = market_dir / "regime_context.json"
            if rc_path.exists():
                with open(rc_path) as f:
                    rc = json.load(f)
                ctx = rc.get("regime_context", {})
                results["markets"][market]["regime"] = ctx.get("regime")
                results["markets"][market]["canonical_state"] = ctx.get("canonical_state")

    return results


# ============================================================
# STEP 6: Re-compute governance artifacts
# ============================================================
@step("6_governance_recompute")
def recompute_governance():
    """Re-compute suppression state and narrative."""
    from governance.suppression_state import compute_suppression_for_market
    from governance.narrative_guard import compute_narrative_for_market

    results = {}
    for market in ["US", "INDIA"]:
        logger.info(f"  Computing suppression for {market}...")
        sup = compute_suppression_for_market(market)
        sup_summary = sup.get("summary", {})
        
        logger.info(f"  Computing narrative for {market}...")
        nar = compute_narrative_for_market(market)
        nar_state = nar.get("narrative", {})

        results[market] = {
            "suppression_state": sup_summary.get("suppression_state"),
            "suppression_reasons": len(sup.get("registry", {}).get("reasons", [])),
            "narrative_mode": nar_state.get("narrative_mode"),
        }
        logger.info(f"  [{market}] suppression={results[market]['suppression_state']} "
                     f"narrative={results[market]['narrative_mode']}")
    return results


# ============================================================
# STEP 7: Final verification
# ============================================================
@step("7_final_verification")
def verify_system_state():
    """Final system state check."""
    today = datetime(2026, 3, 8).date()
    results = {"data_freshness": {}, "proxy_status": {}}

    # Data freshness
    crit_files = {
        "SPY_daily": ("data/us_market/SPY_daily.csv", "timestamp"),
        "SPY_regime": ("data/regime/raw/SPY.csv", "date"),
        "QQQ_regime": ("data/regime/raw/QQQ.csv", "date"),
        "VIX_regime": ("data/regime/raw/VIX.csv", "date"),
        "HYG_regime": ("data/regime/raw/HYG.csv", "date"),
        "LQD_regime": ("data/regime/raw/LQD.csv", "date"),
        "TNX": ("data/regime/raw/^TNX.csv", "date"),
        "NIFTY50": ("data/india/NIFTY50.csv", "Date"),
        "IN10Y": ("data/india/IN10Y.csv", "Date"),
    }

    for name, (rel, date_col) in crit_files.items():
        path = PROJECT_ROOT / rel
        if not path.exists():
            results["data_freshness"][name] = "MISSING"
            continue
        df = pd.read_csv(path)
        if date_col in df.columns:
            last = pd.to_datetime(df[date_col], errors="coerce").max()
            if pd.notna(last):
                stale = (today - last.date()).days
                status = "FRESH" if stale <= 5 else "STALE"
                results["data_freshness"][name] = {
                    "last_date": str(last.date()),
                    "stale_days": stale,
                    "status": status,
                }
                icon = "✅" if status == "FRESH" else "❌"
                logger.info(f"  {icon} {name:15s} | {last.date()} | stale={stale}d")

    # Proxy adapter check
    from structural.proxy_adapter import ProxyAdapter
    adapter = ProxyAdapter()
    for market in ["US", "INDIA"]:
        for role in ["equity_core", "rates_anchor"]:
            try:
                paths = adapter.get_ingestion_binding(market, role)
                exists = all(p.exists() for p in paths)
                results["proxy_status"][f"{market}_{role}"] = "OK" if exists else "MISSING"
            except Exception:
                results["proxy_status"][f"{market}_{role}"] = "NOT_BOUND"

    return results


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    logger.info("🚀 FULL SYSTEM UNLOCK - STARTING")
    logger.info(f"   Timestamp: {datetime.now().isoformat()}")
    logger.info(f"   Project: {PROJECT_ROOT}")
    logger.info("")

    refresh_regime_anchors()
    refresh_us_dailies()
    refresh_india_in10y()
    update_temporal_state()
    
    # Auto-advance truth epoch if canonical data is fresh
    import subprocess
    subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "auto_advance_truth_epoch.py")], check=True)
    update_temporal_state()  # Re-run so drift flags clear based on the new TE
    
    run_evolution_tick()
    
    # Generate final policies and fragilities before computing suppression
    try:
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "run_us_market_regime.py")], check=True)
        logger.info("US Decision Policy and Fragility regenerated.")
    except Exception as e:
        logger.error(f"Failed to regenerate US policies: {e}")
        
    try:
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "india_policy_evaluation.py")], check=True)
        logger.info("INDIA Decision Policy regenerated.")
    except Exception as e:
        logger.error(f"Failed to regenerate INDIA policies: {e}")

    recompute_governance()
    
    # Update global postures
    try:
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "update_system_postures.py")], check=True)
        logger.info("Global postures updated.")
    except Exception as e:
        logger.error(f"Failed to update global postures: {e}")
        
    verify_system_state()

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("FULL SYSTEM UNLOCK - SUMMARY")
    logger.info("=" * 60)

    all_pass = True
    for step_name, step_result in RESULTS["steps"].items():
        status = step_result["status"]
        icon = "✅" if status == "PASS" else "❌"
        logger.info(f"  {icon} {step_name}: {status}")
        if status != "PASS":
            all_pass = False

    RESULTS["summary"]["all_pass"] = all_pass
    RESULTS["summary"]["completed_at"] = datetime.now().isoformat()

    # Save report
    report_path = PROJECT_ROOT / "docs" / "verification_runs" / "SYSTEM_UNLOCK_REPORT.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2, default=str)

    logger.info(f"\n📋 Report: {report_path}")
    logger.info(f"END SYSTEM UNLOCK {'[SUCCESS]' if all_pass else 'PARTIAL [WARNING]'}")
