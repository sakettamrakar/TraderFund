"""
Quick parity status regenerator.
Reads actual data files and writes correct market_parity_status_{market}.json.
"""
import sys, json
from pathlib import Path
from datetime import datetime
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from structural.proxy_adapter import ProxyAdapter


def _load_truth_epoch_id() -> str:
    epoch_path = PROJECT_ROOT / "docs" / "epistemic" / "truth_epoch.json"
    gate_path = PROJECT_ROOT / "docs" / "intelligence" / "execution_gate_status.json"

    try:
        if epoch_path.exists():
            with open(epoch_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            epoch_id = payload.get("epoch", {}).get("epoch_id")
            if epoch_id:
                return str(epoch_id)
    except Exception:
        pass

    try:
        if gate_path.exists():
            with open(gate_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            truth_epoch = payload.get("truth_epoch")
            if truth_epoch:
                return str(truth_epoch)
    except Exception:
        pass

    return "TE-2026-01-30"


def _resolve_date_column(frame: pd.DataFrame) -> str | None:
    for column in ("Date", "date", "timestamp", "Timestamp"):
        if column in frame.columns:
            return column
    return None


def _build_diagnostic(market: str, role: str, symbol: str, rel_path: str) -> dict:
    full_path = PROJECT_ROOT / rel_path
    diagnostic = {
        "status": "MISSING",
        "role": role,
        "symbol": symbol,
        "source": "Yahoo Finance (AlphaVantage)",
        "provenance": "REAL",
        "path": rel_path,
        "rows": 0,
        "staleness": "HIGH",
    }

    if not full_path.exists():
        return diagnostic

    try:
        frame = pd.read_csv(full_path)
        diagnostic["rows"] = len(frame)
        date_column = _resolve_date_column(frame)
        if not date_column:
            diagnostic["status"] = "ACTIVE"
            diagnostic["staleness"] = "UNKNOWN"
            return diagnostic

        timestamps = pd.to_datetime(frame[date_column], errors="coerce").dropna()
        if timestamps.empty:
            diagnostic["status"] = "ERROR"
            diagnostic["error"] = f"No valid timestamps in {date_column}"
            return diagnostic

        last_timestamp = timestamps.max()
        stale_days = (datetime.utcnow().date() - last_timestamp.date()).days
        max_stale_days = 70 if market == "INDIA" and role == "rates_anchor" else 5

        diagnostic["status"] = "ACTIVE" if stale_days <= max_stale_days else "STALE"
        diagnostic["staleness"] = "NONE" if stale_days <= max_stale_days else f"{stale_days}d"
        diagnostic["last_date"] = str(last_timestamp.date())
        return diagnostic
    except Exception as exc:
        diagnostic["status"] = "ERROR"
        diagnostic["error"] = str(exc)
        return diagnostic


def main() -> None:
    adapter = ProxyAdapter()
    truth_epoch = _load_truth_epoch_id()
    optional_roles = {"liquidity_proxy", "sector_proxies"}

    for market in ["US", "INDIA"]:
        proxy_config = adapter._config.get(market, {})
        roles_def = proxy_config.get("roles", {})
        bindings = proxy_config.get("ingestion_binding", {})

        parity = {
            "market": market,
            "computed_at": datetime.now().isoformat(),
            "truth_epoch": truth_epoch,
            "parity_status": "CANONICAL",
            "proxy_diagnostics": {},
            "gaps": [],
            "canonical_ready": True,
        }

        for role, keys in roles_def.items():
            if not keys:
                if role not in optional_roles:
                    parity["gaps"].append(role)
                    parity["canonical_ready"] = False
                continue

            primary = keys[0]
            rel_path = bindings.get(primary, "")
            diagnostic = _build_diagnostic(market, role, primary, rel_path)
            if diagnostic["status"] != "ACTIVE":
                parity["canonical_ready"] = False
            parity["proxy_diagnostics"][role] = diagnostic

        parity["parity_status"] = "CANONICAL" if parity["canonical_ready"] else "DEGRADED"

        out = PROJECT_ROOT / "docs" / "intelligence" / f"market_parity_status_{market}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(parity, f, indent=4)

        print(f"\n[{market}] Parity Status Updated:")
        for role, diagnostic in parity["proxy_diagnostics"].items():
            print(f"  {role}: {diagnostic['status']} ({diagnostic['rows']} rows, stale={diagnostic['staleness']})")
        print(f"  Gaps: {parity['gaps']}")
        print(f"  Canonical Ready: {parity['canonical_ready']}")


if __name__ == "__main__":
    main()
