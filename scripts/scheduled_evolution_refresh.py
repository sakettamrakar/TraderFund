"""
Scheduled Evolution Refresh
===========================
Refreshes ONLY dynamic (evolution) datasets that change daily.
ANCHOR datasets (like regime/raw full histories or IN10Y) are EXCLUDED to protect them from unnecessary refresh.

Pipeline Steps:
1. Refresh US market dailies (ingest_daily.py: SPY, QQQ, IWM, VIXY, TNX)
2. Refresh India proxies (yfinance: ^NSEI, ^NSEBANK, ^INDIAVIX -> saved as NIFTY50.csv, BANKNIFTY.csv, INDIAVIX.csv)
3. Regenerate Parity Status (update_parity_status.py)
4. Update temporal state (temporal_orchestrator)
5. Run evolution tick (ev_tick)
6. Re-compute governance (suppression, narrative)
"""
import sys, os, time, logging, json
import importlib.util
from pathlib import Path
from datetime import datetime
import pandas as pd
import yfinance as yf

PROJECT_ROOT = Path(__file__).parent.parent
for entry in (str(PROJECT_ROOT), str(PROJECT_ROOT / "src")):
    if entry in sys.path:
        sys.path.remove(entry)
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(1, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("EvolutionRefresh")


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

def refresh_us_dailies():
    try:
        USMarketIngestor = _load_us_market_ingestor_class()
        ingestor = USMarketIngestor()
        ingestor.run_all()
        logger.info("US Dailies refreshed.")
    except Exception as e:
        logger.error(f"Failed to refresh US Dailies: {e}")

def refresh_india_dailies():
    # Use yfinance for India proxies to ensure reliable daily refresh without Angel API
    symbols = {
        "NIFTY50": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "INDIAVIX": "^INDIAVIX"
    }
    out_dir = PROJECT_ROOT / "data" / "india"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for file_sym, yf_sym in symbols.items():
        out_path = out_dir / f"{file_sym}.csv"
        try:
            df = yf.download(yf_sym, period="1y", progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.reset_index().rename(columns={"Date": "Date", "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
                df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Date"])
                
                # Merge with existing file if it exists to preserve extra history
                if out_path.exists():
                    existing = pd.read_csv(out_path)
                    existing["Date"] = pd.to_datetime(existing["Date"], errors="coerce").dt.normalize()
                    df = pd.concat([existing, df])
                
                df = df.sort_values("Date").drop_duplicates(subset=["Date"], keep="last")
                df.to_csv(out_path, index=False)
                logger.info(f"India proxy {file_sym} refreshed via {yf_sym}.")
            else:
                logger.warning(f"No data returned for {yf_sym}")
        except Exception as e:
            logger.error(f"Failed to refresh {file_sym}: {e}")
        time.sleep(1)

def update_parity():
    import subprocess
    try:
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "update_parity_status.py")], check=True)
        logger.info("Parity status updated.")
    except Exception as e:
        logger.error(f"Failed to update parity: {e}")

def update_temporal():
    from scripts.temporal_orchestrator import TemporalOrchestrator
    try:
        orch = TemporalOrchestrator()
        for market in ["US", "INDIA"]:
            orch.update_rdt_ctt(market)
        logger.info("Temporal state updated.")
    except Exception as e:
        logger.error(f"Failed to update temporal state: {e}")

def run_ev_tick():
    from evolution.orchestration.ev_tick import EvTickOrchestrator
    try:
        ts = int(time.time())
        out_dir = PROJECT_ROOT / "docs" / "evolution" / "ticks" / f"tick_{ts}"
        orchestrator = EvTickOrchestrator(out_dir)
        orchestrator.execute()
        logger.info(f"EV-Tick executed -> {out_dir.name}")
    except Exception as e:
        logger.error(f"Failed to run ev_tick: {e}")

def recompute_gov():
    from governance.suppression_state import compute_suppression_for_market
    from governance.narrative_guard import compute_narrative_for_market
    import subprocess
    try:
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "run_us_market_regime.py")], check=True)
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "india_policy_evaluation.py")], check=True)
        for market in ["US", "INDIA"]:
            compute_suppression_for_market(market)
            compute_narrative_for_market(market)
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "update_system_postures.py")], check=True)
        logger.info("Governance recomputed.")
    except Exception as e:
        logger.error(f"Failed to recompute governance: {e}")

def main(*args, **kwargs):
    logger.info("Starting Daily Evolution Data Refresh...")
    refresh_us_dailies()
    refresh_india_dailies()
    update_parity()
    update_temporal()
    import subprocess
    subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "auto_advance_truth_epoch.py")], check=True)
    update_temporal()  # Run again to clear drift warnings using new TE
    run_ev_tick()
    recompute_gov()
    logger.info("Daily Evolution Data Refresh Complete.")
    return True

if __name__ == "__main__":
    main()
