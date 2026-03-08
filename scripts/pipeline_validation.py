"""
Pipeline Validation Script
Validates Anchor Data + Daily Refresh + Delta/Incremental Load
Produces structured audit report.
"""
import sys
import os
import json
import hashlib
import time
import traceback
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

REPORT = {
    "timestamp": datetime.now().isoformat(),
    "phases": {},
    "summary": {}
}

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")

def hash_df(df):
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

# ============================================================
# PHASE 1: ANCHOR DATA VALIDATION (Pre-Refresh)
# ============================================================
def phase1_anchor_validation():
    log("=" * 60)
    log("PHASE 1: ANCHOR DATA VALIDATION (Pre-Refresh State)")
    log("=" * 60)
    
    results = {"status": "PASS", "tables": {}, "errors": []}
    
    # --- US Market Anchors ---
    us_anchors = {
        "SPY": {"path": PROJECT_ROOT / "data/us_market/SPY_daily.csv", "role": "equity_core", "date_col": "timestamp"},
        "QQQ": {"path": PROJECT_ROOT / "data/us_market/QQQ_daily.csv", "role": "growth_proxy", "date_col": "timestamp"},
        "IWM": {"path": PROJECT_ROOT / "data/us_market/IWM_daily.csv", "role": "small_cap_proxy", "date_col": "timestamp"},
        "VIXY": {"path": PROJECT_ROOT / "data/us_market/VIXY_daily.csv", "role": "volatility_gauge", "date_col": "timestamp"},
        "TNX": {"path": PROJECT_ROOT / "data/regime/raw/^TNX.csv", "role": "rates_anchor", "date_col": "date"},
    }
    
    # Regime detection anchors
    regime_anchors = {
        "SPY_regime": {"path": PROJECT_ROOT / "data/regime/raw/SPY.csv", "role": "regime_equity", "date_col": "date"},
        "QQQ_regime": {"path": PROJECT_ROOT / "data/regime/raw/QQQ.csv", "role": "regime_growth", "date_col": "date"},
        "VIX_regime": {"path": PROJECT_ROOT / "data/regime/raw/VIX.csv", "role": "regime_vol", "date_col": "date"},
        "HYG_regime": {"path": PROJECT_ROOT / "data/regime/raw/HYG.csv", "role": "credit_spread", "date_col": "date"},
        "LQD_regime": {"path": PROJECT_ROOT / "data/regime/raw/LQD.csv", "role": "inv_grade", "date_col": "date"},
        "TYX_regime": {"path": PROJECT_ROOT / "data/regime/raw/^TYX.csv", "role": "long_rates", "date_col": "date"},
    }
    
    # India anchors
    india_anchors = {
        "NIFTY50": {"path": PROJECT_ROOT / "data/india/NIFTY50.csv", "role": "india_equity_core", "date_col": "Date"},
        "BANKNIFTY": {"path": PROJECT_ROOT / "data/india/BANKNIFTY.csv", "role": "india_sector_proxy", "date_col": "Date"},
        "INDIAVIX": {"path": PROJECT_ROOT / "data/india/INDIAVIX.csv", "role": "india_volatility", "date_col": "Date"},
        "IN10Y": {"path": PROJECT_ROOT / "data/india/IN10Y.csv", "role": "india_rates_anchor", "date_col": "Date"},
    }
    
    all_anchors = {}
    all_anchors.update(us_anchors)
    all_anchors.update(regime_anchors)
    all_anchors.update(india_anchors)
    
    for name, cfg in all_anchors.items():
        path = cfg["path"]
        date_col = cfg["date_col"]
        entry = {
            "file": str(path.relative_to(PROJECT_ROOT)),
            "role": cfg["role"],
            "exists": path.exists(),
        }
        
        if not path.exists():
            entry["status"] = "MISSING"
            entry["rows"] = 0
            entry["error"] = f"File not found: {path}"
            results["errors"].append(f"{name}: File missing at {path}")
            results["status"] = "PARTIAL"
        else:
            try:
                df = pd.read_csv(path)
                entry["rows"] = len(df)
                entry["columns"] = list(df.columns)
                
                # Date range
                if date_col.lower() in [c.lower() for c in df.columns]:
                    actual_col = [c for c in df.columns if c.lower() == date_col.lower()][0]
                    dates = pd.to_datetime(df[actual_col], errors="coerce")
                    valid_dates = dates.dropna()
                    if len(valid_dates) > 0:
                        entry["date_min"] = str(valid_dates.min().date())
                        entry["date_max"] = str(valid_dates.max().date())
                        # Staleness
                        last_date = valid_dates.max().date()
                        today = datetime(2026, 3, 8).date()
                        stale_days = (today - last_date).days
                        entry["staleness_days"] = stale_days
                        entry["is_stale"] = stale_days > 3  # Weekend buffer
                    else:
                        entry["date_min"] = None
                        entry["date_max"] = None
                        entry["staleness_days"] = -1
                else:
                    entry["date_col_found"] = False
                    
                # Schema check
                expected_cols = {"open", "high", "low", "close", "volume"}
                actual_lower = {c.lower() for c in df.columns}
                missing_schema = expected_cols - actual_lower
                entry["schema_valid"] = len(missing_schema) == 0
                if missing_schema:
                    entry["missing_columns"] = list(missing_schema)
                    
                # Hash for idempotency
                entry["data_hash"] = hash_df(df)
                entry["status"] = "ACTIVE"
                
            except Exception as e:
                entry["status"] = "ERROR"
                entry["error"] = str(e)
                results["errors"].append(f"{name}: {e}")
                results["status"] = "PARTIAL"
        
        results["tables"][name] = entry
        status_icon = "✅" if entry.get("status") == "ACTIVE" else "❌"
        stale_str = f" (stale: {entry.get('staleness_days', '?')}d)" if entry.get("is_stale") else ""
        log(f"  {status_icon} {name:15s} | rows={entry.get('rows', 0):>5} | {entry.get('date_min','?')} → {entry.get('date_max','?')}{stale_str}")
    
    REPORT["phases"]["anchor_validation"] = results
    return results

# ============================================================
# PHASE 2: DAILY REFRESH - FULL LOAD
# ============================================================
def phase2_daily_refresh():
    log("=" * 60)
    log("PHASE 2: DAILY REFRESH (Full Load via Alpha Vantage + yfinance)")
    log("=" * 60)
    
    results = {"status": "PASS", "symbols": {}, "errors": []}
    
    # Snapshot pre-refresh state
    pre_state = {}
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
                dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
                pre_state[sym] = {
                    "rows": len(df),
                    "max_date": str(dates.max().date()) if len(dates) > 0 else None,
                    "hash": hash_df(df)
                }
            else:
                pre_state[sym] = {"rows": len(df), "max_date": None, "hash": hash_df(df)}
        else:
            pre_state[sym] = {"rows": 0, "max_date": None, "hash": None}
    
    log("Pre-refresh snapshot captured.")
    for sym, s in pre_state.items():
        log(f"  {sym:6s} | rows={s['rows']:>5} | last={s['max_date']}")
    
    # Execute refresh
    log("")
    log("Executing US Market Ingestor...")
    try:
        from ingestion.us_market.ingest_daily import USMarketIngestor
        ingestor = USMarketIngestor()
        ingestor.run_all()
        results["execution"] = "SUCCESS"
        log("Ingestion execution completed.")
    except Exception as e:
        results["execution"] = "FAILED"
        results["errors"].append(f"Ingestion execution failed: {e}")
        results["status"] = "FAIL"
        log(f"Ingestion FAILED: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        REPORT["phases"]["daily_refresh"] = results
        return results
    
    # Post-refresh validation
    log("")
    log("Post-refresh validation...")
    
    for sym, path in files.items():
        sym_result = {"pre": pre_state[sym]}
        if path.exists():
            df = pd.read_csv(path)
            date_col = "date" if sym == "TNX" else "timestamp"
            if date_col in df.columns:
                dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
                post = {
                    "rows": len(df),
                    "max_date": str(dates.max().date()) if len(dates) > 0 else None,
                    "hash": hash_df(df)
                }
            else:
                post = {"rows": len(df), "max_date": None, "hash": hash_df(df)}
            
            sym_result["post"] = post
            
            # Delta analysis
            delta_rows = post["rows"] - pre_state[sym]["rows"]
            date_advanced = post["max_date"] != pre_state[sym]["max_date"]
            data_changed = post["hash"] != pre_state[sym]["hash"]
            
            sym_result["delta"] = {
                "new_rows": delta_rows,
                "date_advanced": date_advanced,
                "data_changed": data_changed,
                "status": "UPDATED" if data_changed else "UNCHANGED"
            }
            
            status_icon = "✅" if data_changed or delta_rows > 0 else "⬜"
            log(f"  {status_icon} {sym:6s} | {pre_state[sym]['rows']:>5} → {post['rows']:>5} (+{delta_rows}) | {pre_state[sym]['max_date']} → {post['max_date']} | {'UPDATED' if data_changed else 'UNCHANGED'}")
        else:
            sym_result["post"] = {"rows": 0, "max_date": None}
            sym_result["delta"] = {"status": "MISSING"}
            results["errors"].append(f"{sym}: File missing after refresh")
        
        results["symbols"][sym] = sym_result
    
    REPORT["phases"]["daily_refresh"] = results
    return results

# ============================================================
# PHASE 3: DELTA/INCREMENTAL LOAD VALIDATION
# ============================================================
def phase3_delta_validation():
    log("=" * 60)
    log("PHASE 3: DELTA / INCREMENTAL LOAD VALIDATION")
    log("=" * 60)
    
    results = {"status": "PASS", "tests": {}, "errors": []}
    
    # Test 1: Idempotency - Run the same refresh twice, ensure no duplicate rows
    log("Test 3.1: Idempotency Check (double-write produces no duplicates)...")
    files = {
        "SPY": ("data/us_market/SPY_daily.csv", "timestamp"),
        "TNX": ("data/regime/raw/^TNX.csv", "date"),
    }
    
    for sym, (rel_path, date_col) in files.items():
        path = PROJECT_ROOT / rel_path
        if not path.exists():
            results["tests"][f"idempotency_{sym}"] = {"status": "SKIP", "reason": "File missing"}
            continue
            
        df = pd.read_csv(path)
        if date_col in df.columns:
            total = len(df)
            unique = df[date_col].nunique()
            has_dupes = total != unique
            results["tests"][f"idempotency_{sym}"] = {
                "status": "FAIL" if has_dupes else "PASS",
                "total_rows": total,
                "unique_dates": unique,
                "duplicates": total - unique
            }
            icon = "❌" if has_dupes else "✅"
            log(f"  {icon} {sym}: total={total}, unique_dates={unique}, dupes={total - unique}")
        else:
            results["tests"][f"idempotency_{sym}"] = {"status": "SKIP", "reason": f"No {date_col} column"}
    
    # Test 2: Schema Stability
    log("")
    log("Test 3.2: Schema Stability (columns unchanged after refresh)...")
    expected_schemas = {
        "SPY": {"timestamp", "open", "high", "low", "close", "volume"},
        "TNX": {"date", "symbol", "open", "high", "low", "close", "volume"},
    }
    
    for sym, expected_cols in expected_schemas.items():
        rel, dc = files[sym]
        path = PROJECT_ROOT / rel
        if not path.exists():
            continue
        df = pd.read_csv(path)
        actual = set(df.columns)
        missing = expected_cols - actual
        extra = actual - expected_cols
        
        test_pass = len(missing) == 0
        results["tests"][f"schema_{sym}"] = {
            "status": "PASS" if test_pass else "FAIL",
            "expected": sorted(expected_cols),
            "actual": sorted(actual),
            "missing": sorted(missing),
            "extra": sorted(extra)
        }
        icon = "✅" if test_pass else "❌"
        log(f"  {icon} {sym}: expected={sorted(expected_cols)}, missing={sorted(missing)}")
    
    # Test 3: Sort Order Validation (chronological)
    log("")
    log("Test 3.3: Sort Order Validation (chronological ascending)...")
    for sym, (rel, dc) in files.items():
        path = PROJECT_ROOT / rel
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if dc in df.columns:
            dates = pd.to_datetime(df[dc], errors="coerce").dropna()
            is_sorted = dates.is_monotonic_increasing
            results["tests"][f"sort_{sym}"] = {
                "status": "PASS" if is_sorted else "FAIL",
                "is_sorted": is_sorted
            }
            icon = "✅" if is_sorted else "❌"
            log(f"  {icon} {sym}: sorted={is_sorted}")
    
    # Test 4: Data continuity (no large gaps)
    log("")
    log("Test 3.4: Continuity Check (no gaps > 5 business days)...")
    for sym, (rel, dc) in files.items():
        path = PROJECT_ROOT / rel
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if dc in df.columns:
            dates = pd.to_datetime(df[dc], errors="coerce").dropna().sort_values()
            gaps = dates.diff().dropna()
            max_gap = gaps.max()
            max_gap_days = max_gap.days if hasattr(max_gap, 'days') else 0
            has_large_gap = max_gap_days > 7  # 5 biz days = ~7 calendar days
            results["tests"][f"continuity_{sym}"] = {
                "status": "WARN" if has_large_gap else "PASS",
                "max_gap_days": max_gap_days
            }
            icon = "⚠️" if has_large_gap else "✅"
            log(f"  {icon} {sym}: max_gap={max_gap_days}d")
    
    REPORT["phases"]["delta_validation"] = results
    return results

# ============================================================
# PHASE 4: INDIA DATA VALIDATION
# ============================================================
def phase4_india_validation():
    log("=" * 60)
    log("PHASE 4: INDIA MARKET DATA VALIDATION")
    log("=" * 60)
    
    results = {"status": "PASS", "roles": {}, "errors": []}
    
    try:
        from ingestion.india_market_loader import IndiaMarketLoader
        loader = IndiaMarketLoader()
        parity = loader.check_parity()
        
        results["parity_status"] = parity["parity_status"]
        results["canonical_ready"] = parity["canonical_ready"]
        
        for role, diag in parity["proxy_diagnostics"].items():
            status = diag.get("status", "UNKNOWN")
            rows = diag.get("rows", 0)
            results["roles"][role] = {
                "status": status,
                "rows": rows,
                "path": diag.get("path", "N/A")
            }
            icon = "✅" if status == "ACTIVE" else "❌"
            log(f"  {icon} {role:20s} | status={status:15s} | rows={rows}")
        
        if not parity["canonical_ready"]:
            results["status"] = "PARTIAL"
            for gap in parity.get("gaps", []):
                results["errors"].append(f"{gap['role']}: {gap['status']}")
    
    except Exception as e:
        results["status"] = "FAIL"
        results["errors"].append(str(e))
        log(f"India validation failed: {e}", "ERROR")
    
    REPORT["phases"]["india_validation"] = results
    return results

# ============================================================
# PHASE 5: PROXY ADAPTER + CANONICAL STATE VALIDATION
# ============================================================
def phase5_canonical_validation():
    log("=" * 60)
    log("PHASE 5: CANONICAL STATE + PROXY ADAPTER VALIDATION")
    log("=" * 60)
    
    results = {"status": "PASS", "markets": {}, "errors": []}
    
    try:
        from structural.proxy_adapter import ProxyAdapter
        adapter = ProxyAdapter()
        
        for market in ["US", "INDIA"]:
            market_result = {"roles": {}}
            roles = ["equity_core", "growth_proxy", "volatility_gauge", "rates_anchor"]
            
            for role in roles:
                try:
                    paths = adapter.get_ingestion_binding(market, role)
                    all_exist = all(p.exists() for p in paths)
                    has_data = False
                    row_count = 0
                    last_date = None
                    
                    for p in paths:
                        if p.exists():
                            df = pd.read_csv(p)
                            row_count += len(df)
                            has_data = True
                            # Try to find last date
                            for col in ["date", "timestamp", "Date", "Timestamp"]:
                                if col in df.columns:
                                    d = pd.to_datetime(df[col], errors="coerce").max()
                                    if pd.notna(d):
                                        last_date = str(d.date())
                                    break
                    
                    market_result["roles"][role] = {
                        "paths": [str(p) for p in paths],
                        "all_exist": all_exist,
                        "has_data": has_data,
                        "rows": row_count,
                        "last_date": last_date,
                        "status": "ACTIVE" if all_exist and has_data else "MISSING"
                    }
                    icon = "✅" if all_exist else "❌"
                    log(f"  [{market}] {icon} {role:20s} | exists={all_exist} | rows={row_count} | last={last_date}")
                    
                except ValueError as e:
                    market_result["roles"][role] = {"status": "NOT_BOUND", "error": str(e)}
                    log(f"  [{market}] ⚠️ {role:20s} | NOT BOUND: {e}")
            
            results["markets"][market] = market_result
    
    except Exception as e:
        results["status"] = "FAIL"
        results["errors"].append(str(e))
        log(f"Canonical validation failed: {e}", "ERROR")
    
    REPORT["phases"]["canonical_validation"] = results
    return results

# ============================================================
# PHASE 6: POST-EXECUTION FRESHNESS CHECK
# ============================================================
def phase6_freshness_check():
    log("=" * 60)
    log("PHASE 6: POST-EXECUTION FRESHNESS + TIMESTAMP VERIFICATION")
    log("=" * 60)
    
    results = {"status": "PASS", "files": {}}
    today = datetime(2026, 3, 8).date()
    
    critical_files = {
        "SPY_daily": ("data/us_market/SPY_daily.csv", "timestamp"),
        "QQQ_daily": ("data/us_market/QQQ_daily.csv", "timestamp"),
        "TNX": ("data/regime/raw/^TNX.csv", "date"),
        "NIFTY50": ("data/india/NIFTY50.csv", "Date"),
    }
    
    for name, (rel, date_col) in critical_files.items():
        path = PROJECT_ROOT / rel
        if not path.exists():
            results["files"][name] = {"status": "MISSING"}
            continue
            
        df = pd.read_csv(path)
        file_mod = datetime.fromtimestamp(path.stat().st_mtime)
        
        last_date = None
        if date_col in df.columns:
            dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
            if len(dates) > 0:
                last_date = dates.max().date()
        
        stale_days = (today - last_date).days if last_date else -1
        is_fresh = stale_days <= 3
        
        results["files"][name] = {
            "last_data_date": str(last_date) if last_date else None,
            "file_modified": file_mod.isoformat(),
            "staleness_days": stale_days,
            "is_fresh": is_fresh,
            "rows": len(df)
        }
        
        icon = "✅" if is_fresh else "⚠️"
        log(f"  {icon} {name:12s} | last_data={last_date} | stale={stale_days}d | modified={file_mod.strftime('%Y-%m-%d %H:%M')}")
        
        if not is_fresh:
            results["status"] = "STALE"
    
    REPORT["phases"]["freshness_check"] = results
    return results

# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    log("🚀 PIPELINE VALIDATION STARTED")
    log(f"   Timestamp: {datetime.now().isoformat()}")
    log(f"   Project Root: {PROJECT_ROOT}")
    log("")
    
    # Phase 1: Validate anchor state BEFORE refresh
    phase1_anchor_validation()
    log("")
    
    # Phase 2: Execute daily refresh
    phase2_daily_refresh()
    log("")
    
    # Phase 3: Validate delta/incremental logic
    phase3_delta_validation()
    log("")
    
    # Phase 4: India market validation
    phase4_india_validation()
    log("")
    
    # Phase 5: Canonical proxy validation
    phase5_canonical_validation()
    log("")
    
    # Phase 6: Final freshness check
    phase6_freshness_check()
    log("")
    
    # ============================================================
    # SUMMARY
    # ============================================================
    log("=" * 60)
    log("PIPELINE VALIDATION SUMMARY")
    log("=" * 60)
    
    summary = {}
    for phase_name, phase_data in REPORT["phases"].items():
        status = phase_data.get("status", "UNKNOWN")
        errors = phase_data.get("errors", [])
        summary[phase_name] = {
            "status": status,
            "error_count": len(errors)
        }
        icon = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌", "STALE": "⏰"}.get(status, "❓")
        log(f"  {icon} {phase_name:25s} | {status}")
        for err in errors[:3]:
            log(f"      └─ {err}")
    
    REPORT["summary"] = summary
    
    # Save report
    report_path = PROJECT_ROOT / "docs" / "verification_runs" / "PIPELINE_VALIDATION_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(REPORT, f, indent=2, default=str)
    
    log("")
    log(f"📋 Full report saved to: {report_path}")
    log("🏁 PIPELINE VALIDATION COMPLETE")
