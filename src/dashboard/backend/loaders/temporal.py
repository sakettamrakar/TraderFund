from pathlib import Path
import json
import logging
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
TEMPORAL_DIR = PROJECT_ROOT / "docs" / "intelligence" / "temporal"
CONFIG_PATH = PROJECT_ROOT / "config" / "temporal_drift_policy.json"
DEFAULT_MAX_DRIFT_DAYS = 7

logger = logging.getLogger(__name__)

def _load_max_drift_days(market: str) -> int:
    if not CONFIG_PATH.exists():
        return DEFAULT_MAX_DRIFT_DAYS
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        markets = data.get("markets", {})
        return int(markets.get(market, data.get("max_drift_days_default", DEFAULT_MAX_DRIFT_DAYS)))
    except Exception:
        return DEFAULT_MAX_DRIFT_DAYS


def _normalize_temporal_payload(payload: Dict[str, Any], market: str) -> Dict[str, Any]:
    drift = payload.setdefault("drift_status", {})
    max_drift = _load_max_drift_days(market)
    drift_days = int(drift.get("evaluation_drift_days", 0))

    drift.setdefault("max_drift_days", max_drift)
    drift.setdefault("drift_limit_exceeded", drift_days > max_drift)
    drift.setdefault("required_operator_action", None)

    if drift_days > max_drift and drift.get("status_code") != "DRIFT_LIMIT_EXCEEDED":
        drift["status_code"] = "DRIFT_LIMIT_EXCEEDED"
        drift["message"] = (
            "EVAL REQUIRED - DRIFT WINDOW EXCEEDED. "
            f"Drift={drift_days}d exceeds max={max_drift}d."
        )

    drift.setdefault(
        "human_explanation",
        "Temporal drift is monitored against a bounded threshold; no automatic truth advancement is permitted.",
    )

    holds = payload.setdefault("holds", {})
    holds.setdefault("evaluation_hold", True)
    holds.setdefault("reason", "Evaluation hold active.")

    payload.setdefault("evaluation_window", None)
    payload.setdefault(
        "governance_pause",
        {
            "active": bool(holds.get("evaluation_hold", True)),
            "reason": holds.get("reason", "Evaluation hold active."),
            "required_operator_action": drift.get("required_operator_action"),
        },
    )
    return payload


def load_temporal_status(market: str):
    """
    Loads the temporal truth status (RDT, CTT, TE, Drift) for a given market.
    """
    file_path = TEMPORAL_DIR / f"temporal_state_{market}.json"
    
    if not file_path.exists():
        logger.warning(f"Temporal state file not found for {market}: {file_path}")
        return {
            "market": market,
            "error": "TEMPORAL_STATE_MISSING",
            "message": "Temporal state definition not found."
        }
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return _normalize_temporal_payload(payload, market)
    except Exception as e:
        logger.error(f"Failed to load temporal state for {market}: {e}")
        return {
            "market": market,
            "error": "READ_ERROR",
            "message": "Failed to read temporal state."
        }
