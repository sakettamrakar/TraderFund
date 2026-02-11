"""
Canonical Partiality Detector (F2 remediation support).

Detects per-market canonical completeness and freshness alignment and emits
explicit partiality state artifacts for downstream regime/policy/dashboard use.

Safety invariants:
- Read-only with respect to ingestion/factor/regime algorithms.
- No TE advancement and no execution/capital enablement.
- Market-scoped; no cross-market contamination.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
PROXY_CONFIG_PATH = PROJECT_ROOT / "src" / "structural" / "market_proxy_instance.json"
INTEL_DIR = PROJECT_ROOT / "docs" / "intelligence"
TEMPORAL_DIR = INTEL_DIR / "temporal"
AUDIT_DIR = PROJECT_ROOT / "docs" / "audit" / "f2_regime_partiality"

CANONICAL_COMPLETE = "CANONICAL_COMPLETE"
CANONICAL_PARTIAL = "CANONICAL_PARTIAL"
CANONICAL_MIXED = "CANONICAL_MIXED"

# Strict F2 defaults for DEGRADE-ON-PARTIAL:
# - Any required role behind CTT is stale.
# - Any freshness skew is mixed freshness.
MAX_ROLE_LAG_DAYS = 0
MAX_FRESHNESS_SKEW_DAYS = 0

REQUIRED_ROLES: Dict[str, List[str]] = {
    "US": ["equity_core", "growth_proxy", "volatility_gauge", "rates_anchor"],
    "INDIA": ["benchmark_equity", "growth_proxy", "volatility_gauge", "rates_anchor"],
}

ROLE_ALIASES: Dict[str, Dict[str, List[str]]] = {
    "US": {
        "equity_core": ["equity_core", "benchmark_equity"],
        "growth_proxy": ["growth_proxy"],
        "volatility_gauge": ["volatility_gauge"],
        "rates_anchor": ["rates_anchor"],
    },
    "INDIA": {
        "benchmark_equity": ["benchmark_equity", "equity_core"],
        "growth_proxy": ["growth_proxy", "sector_proxy"],
        "volatility_gauge": ["volatility_gauge"],
        "rates_anchor": ["rates_anchor"],
    },
}

DATE_KEYS = ["date", "Date", "timestamp", "Timestamp", "time", "Time"]
NON_ACTIVE_STATUSES = {"MISSING", "NOT_INGESTED", "INSUFFICIENT_HISTORY", "ERROR", "PARSE_ERROR"}


def _utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def _parse_iso_date(raw: Optional[str]) -> Optional[dt.date]:
    if not raw:
        return None
    value = str(raw).strip()
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except Exception:
        try:
            return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except Exception:
            return None


def _last_timestamp_from_csv(path: Path) -> Optional[dt.date]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            last_row: Optional[Dict[str, Any]] = None
            for row in reader:
                last_row = row
            if not last_row:
                return None
            for key in DATE_KEYS:
                parsed = _parse_iso_date(last_row.get(key))
                if parsed:
                    return parsed
    except Exception:
        return None
    return None


def _last_timestamp_from_jsonl(path: Path) -> Optional[dt.date]:
    last_record: Optional[Dict[str, Any]] = None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                raw = line.strip()
                if not raw:
                    continue
                try:
                    last_record = json.loads(raw)
                except Exception:
                    continue
    except Exception:
        return None

    if not last_record:
        return None
    for key in DATE_KEYS:
        parsed = _parse_iso_date(last_record.get(key))
        if parsed:
            return parsed
    return None


def _read_last_canonical_date(path: Path) -> Optional[dt.date]:
    if not path.exists():
        return None
    if path.suffix.lower() == ".csv":
        return _last_timestamp_from_csv(path)
    if path.suffix.lower() == ".jsonl":
        return _last_timestamp_from_jsonl(path)
    return None


def _resolve_alias_payload(
    market: str,
    logical_role: str,
    diagnostics: Dict[str, Any],
    proxy_roles: Dict[str, List[str]],
) -> Tuple[Optional[str], Dict[str, Any]]:
    aliases = ROLE_ALIASES.get(market, {}).get(logical_role, [logical_role])
    for alias in aliases:
        if alias in diagnostics:
            return alias, diagnostics.get(alias) or {}
    for alias in aliases:
        if alias in proxy_roles:
            return alias, {}
    return None, {}


def _load_proxy_config(market: str) -> Dict[str, Any]:
    cfg = _read_json(PROXY_CONFIG_PATH)
    return cfg.get(market, {})


def _load_ctt(market: str) -> Optional[dt.date]:
    state = _read_json(TEMPORAL_DIR / f"temporal_state_{market}.json")
    ctt = (
        state.get("temporal_state", {})
        .get("canonical_truth_time", {})
        .get("timestamp")
    )
    return _parse_iso_date(ctt)


def _build_role_state(
    market: str,
    logical_role: str,
    parity_payload: Dict[str, Any],
    proxy_payload: Dict[str, Any],
    ctt_date: Optional[dt.date],
) -> Dict[str, Any]:
    diagnostics = parity_payload.get("proxy_diagnostics", {}) or {}
    proxy_roles = proxy_payload.get("roles", {}) or {}
    bindings = proxy_payload.get("ingestion_binding", {}) or {}

    alias, diag = _resolve_alias_payload(market, logical_role, diagnostics, proxy_roles)
    role_symbols = proxy_roles.get(alias or logical_role, []) if (alias or logical_role) in proxy_roles else []
    symbol = (diag.get("symbol") if isinstance(diag, dict) else None) or (role_symbols[0] if role_symbols else None)
    rel_path = bindings.get(symbol) if symbol else None

    explicit_path = diag.get("path") if isinstance(diag, dict) else None
    if explicit_path:
        path = Path(explicit_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / explicit_path
    elif rel_path:
        path = PROJECT_ROOT / rel_path
    else:
        path = None

    status = str((diag or {}).get("status", "MISSING")).upper()
    if status == "STALE":
        status = "ERROR"

    exists = bool(path and path.exists())
    missing = (not exists) or (status in NON_ACTIVE_STATUSES) or (alias is None)

    last_date = _read_last_canonical_date(path) if exists and path else None
    lag_days: Optional[int] = None
    stale_vs_ctt = False
    if ctt_date and last_date:
        lag_days = (ctt_date - last_date).days
        stale_vs_ctt = lag_days > MAX_ROLE_LAG_DAYS

    return {
        "logical_role": logical_role,
        "resolved_role": alias or logical_role,
        "status": "MISSING" if missing else status,
        "symbol": symbol,
        "path": str(path) if path else None,
        "last_canonical_timestamp": last_date.isoformat() if last_date else None,
        "lag_days_vs_ctt": lag_days,
        "stale_relative_to_ctt": stale_vs_ctt,
        "missing": missing,
    }


def detect_canonical_partiality(market: str, truth_epoch: str = "TE-2026-01-30") -> Dict[str, Any]:
    market = market.upper()
    required = REQUIRED_ROLES.get(market, [])
    parity_path = INTEL_DIR / f"market_parity_status_{market}.json"
    parity_payload = _read_json(parity_path)
    proxy_payload = _load_proxy_config(market)
    ctt_date = _load_ctt(market)

    role_states: Dict[str, Dict[str, Any]] = {}
    missing_roles: List[str] = []
    stale_roles: List[str] = []
    lag_values: List[int] = []

    for role in required:
        state = _build_role_state(market, role, parity_payload, proxy_payload, ctt_date)
        role_states[role] = state
        if state["missing"]:
            missing_roles.append(role)
        if state["stale_relative_to_ctt"]:
            stale_roles.append(role)
        if state["lag_days_vs_ctt"] is not None:
            lag_values.append(int(state["lag_days_vs_ctt"]))

    freshness_skew_days = 0
    if lag_values:
        freshness_skew_days = max(lag_values) - min(lag_values)

    if missing_roles:
        canonical_state = CANONICAL_PARTIAL
        reason = "Required canonical roles missing or non-active."
    elif stale_roles or freshness_skew_days > MAX_FRESHNESS_SKEW_DAYS:
        canonical_state = CANONICAL_MIXED
        reason = "Canonical roles present but freshness is not aligned to CTT."
    else:
        canonical_state = CANONICAL_COMPLETE
        reason = "All required canonical roles are present and freshness-aligned."

    payload = {
        "market": market,
        "computed_at": _utc_now_iso(),
        "truth_epoch": truth_epoch,
        "canonical_truth_time": ctt_date.isoformat() if ctt_date else None,
        "canonical_state": canonical_state,
        "required_roles": required,
        "role_states": role_states,
        "missing_roles": missing_roles,
        "stale_roles": stale_roles,
        "freshness_skew_days": freshness_skew_days,
        "declaration_reason": reason,
        "policy": {
            "max_role_lag_days": MAX_ROLE_LAG_DAYS,
            "max_freshness_skew_days": MAX_FRESHNESS_SKEW_DAYS,
            "mode": "DEGRADE_ON_PARTIAL",
        },
        "version": "1.0.0-F2-PARTIALITY",
    }
    return payload


def detect_and_persist_canonical_partiality(
    market: str,
    truth_epoch: str = "TE-2026-01-30",
    write_audit_log: bool = True,
) -> Dict[str, Any]:
    payload = detect_canonical_partiality(market=market, truth_epoch=truth_epoch)
    market = payload["market"]
    artifact_path = INTEL_DIR / f"canonical_partiality_state_{market}.json"
    _write_json(artifact_path, payload)

    if write_audit_log:
        _append_jsonl(
            AUDIT_DIR / "partiality_detections.jsonl",
            {
                "event": "CANONICAL_PARTIALITY_DETECTED",
                "market": market,
                "computed_at": payload["computed_at"],
                "canonical_state": payload["canonical_state"],
                "missing_roles": payload["missing_roles"],
                "stale_roles": payload["stale_roles"],
                "freshness_skew_days": payload["freshness_skew_days"],
                "declaration_reason": payload["declaration_reason"],
                "artifact": str(artifact_path.relative_to(PROJECT_ROOT)),
            },
        )
    return payload


def load_or_detect_canonical_partiality(
    market: str,
    truth_epoch: str = "TE-2026-01-30",
) -> Dict[str, Any]:
    return detect_and_persist_canonical_partiality(
        market=market.upper(),
        truth_epoch=truth_epoch,
        write_audit_log=True,
    )


def log_regime_degradation(
    market: str,
    canonical_state: str,
    missing_roles: List[str],
    stale_roles: List[str],
    reason: str,
    source: str,
) -> None:
    _append_jsonl(
        AUDIT_DIR / "regime_degradations.jsonl",
        {
            "event": "REGIME_DEGRADED_ON_PARTIAL",
            "computed_at": _utc_now_iso(),
            "market": market.upper(),
            "canonical_state": canonical_state,
            "missing_roles": missing_roles,
            "stale_roles": stale_roles,
            "reason": reason,
            "source": source,
        },
    )
