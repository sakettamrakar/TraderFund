from pathlib import Path
import argparse
import datetime
import json
import logging
import sys
from typing import Any, Dict, Optional

import pandas as pd


# Configure logging
LOG_FILE = Path("logs/temporal_truth_orchestrator.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# Constants
PROJECT_ROOT = Path(__file__).parent.parent
TEMPORAL_DIR = PROJECT_ROOT / "docs" / "intelligence" / "temporal"
TEMPORAL_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = PROJECT_ROOT / "config" / "temporal_drift_policy.json"
AUDIT_DIR = PROJECT_ROOT / "docs" / "audit" / "f1_temporal_drift"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_DIR = TEMPORAL_DIR / "evaluation_windows"
WINDOW_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MAX_DRIFT_DAYS = 7


class TemporalOrchestrator:
    """
    Manages explicit temporal state transitions: RDT -> CTT while TE remains frozen.

    F1 remediation controls implemented:
    - Configurable max drift threshold (default 7 days)
    - DRIFT_LIMIT_EXCEEDED state when drift exceeds threshold
    - Operator-mediated bounded evaluation window requests
    - Audit logging for breaches and window requests

    Safety invariants:
    - Never auto-advances TE
    - Never auto-triggers evaluation
    - Never modifies execution/capital states
    """

    def __init__(self):
        self.state_file_us = TEMPORAL_DIR / "temporal_state_US.json"
        self.state_file_india = TEMPORAL_DIR / "temporal_state_INDIA.json"

        # Data sources
        self.data_us = PROJECT_ROOT / "data" / "us_market" / "SPY_daily.csv"
        self.data_india = PROJECT_ROOT / "data" / "india" / "NIFTY50.csv"

        self.policy = self._load_policy()
        self.max_drift_default = int(self.policy.get("max_drift_days_default", DEFAULT_MAX_DRIFT_DAYS))

    # ----------------------------
    # Policy & State Helpers
    # ----------------------------
    def _load_policy(self) -> Dict[str, Any]:
        default_policy = {
            "max_drift_days_default": DEFAULT_MAX_DRIFT_DAYS,
            "markets": {"US": DEFAULT_MAX_DRIFT_DAYS, "INDIA": DEFAULT_MAX_DRIFT_DAYS},
            "operator_action_name": "REQUEST_EVALUATION_WINDOW",
            "version": "1.0.0",
        }

        if not CONFIG_PATH.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(default_policy, f, indent=2)
            logger.info("Created default temporal drift policy at %s", CONFIG_PATH)
            return default_policy

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            policy = {**default_policy, **loaded}
            policy_markets = dict(default_policy.get("markets", {}))
            policy_markets.update(loaded.get("markets", {}))
            policy["markets"] = policy_markets
            return policy
        except Exception as exc:
            logger.error("Failed to load drift policy (%s). Using defaults.", exc)
            return default_policy

    def _max_drift_days_for_market(self, market: str) -> int:
        return int(self.policy.get("markets", {}).get(market, self.max_drift_default))

    def _state_path_for_market(self, market: str) -> Path:
        return self.state_file_us if market == "US" else self.state_file_india

    def _load_truth_epoch_date(self) -> str:
        """
        Loads the frozen TE date string (YYYY-MM-DD) from execution gate status.
        Falls back to TE-2026-01-30 if unavailable.
        """
        gate_path = PROJECT_ROOT / "docs" / "intelligence" / "execution_gate_status.json"
        fallback = "2026-01-30"

        if not gate_path.exists():
            return fallback

        try:
            with open(gate_path, "r", encoding="utf-8") as f:
                gate = json.load(f)
            raw = str(gate.get("truth_epoch", ""))
            if raw.startswith("TE-") and len(raw) >= 13:
                return raw.replace("TE-", "")
        except Exception:
            pass

        return fallback

    def _bootstrap_state(self, market: str) -> Dict[str, Any]:
        te_date = self._load_truth_epoch_date()
        return {
            "market": market,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "temporal_state": {
                "raw_data_time": {"timestamp": te_date, "source": "unknown", "status": "UNKNOWN"},
                "canonical_truth_time": {
                    "timestamp": te_date,
                    "source": "canonical_validation_layer",
                    "status": "UNKNOWN",
                    "last_validated": None,
                },
                "truth_epoch": {
                    "timestamp": te_date,
                    "source": "governance_manifest",
                    "status": "FROZEN",
                    "reason": "Truth Epoch freeze enforced",
                },
            },
            "drift_status": {
                "ingestion_drift_days": 0,
                "evaluation_drift_days": 0,
                "max_drift_days": self._max_drift_days_for_market(market),
                "drift_limit_exceeded": False,
                "critical_future_leakage": False,
                "status_code": "SYNC",
                "message": "System synchronized.",
                "required_operator_action": None,
                "human_explanation": "No drift detected.",
            },
            "holds": {"ingestion_hold": False, "evaluation_hold": True, "reason": "Truth epoch frozen"},
            "evaluation_window": None,
            "governance_pause": {
                "active": True,
                "reason": "Truth epoch frozen",
                "required_operator_action": self.policy.get("operator_action_name", "REQUEST_EVALUATION_WINDOW"),
            },
        }

    def _ensure_state_shape(self, market: str, state: Dict[str, Any]) -> Dict[str, Any]:
        if not state:
            state = self._bootstrap_state(market)

        state.setdefault("market", market)
        state.setdefault("timestamp", datetime.datetime.utcnow().isoformat() + "Z")
        temporal_state = state.setdefault("temporal_state", {})

        te_date = self._load_truth_epoch_date()

        temporal_state.setdefault("raw_data_time", {"timestamp": te_date, "source": "unknown", "status": "UNKNOWN"})
        temporal_state.setdefault(
            "canonical_truth_time",
            {"timestamp": te_date, "source": "canonical_validation_layer", "status": "UNKNOWN", "last_validated": None},
        )
        temporal_state.setdefault(
            "truth_epoch",
            {"timestamp": te_date, "source": "governance_manifest", "status": "FROZEN", "reason": "Truth epoch frozen"},
        )

        drift_status = state.setdefault("drift_status", {})
        drift_status.setdefault("ingestion_drift_days", 0)
        drift_status.setdefault("evaluation_drift_days", 0)
        drift_status.setdefault("max_drift_days", self._max_drift_days_for_market(market))
        drift_status.setdefault("drift_limit_exceeded", False)
        drift_status.setdefault("critical_future_leakage", False)
        drift_status.setdefault("status_code", "UNKNOWN")
        drift_status.setdefault("message", "Temporal status unknown.")
        drift_status.setdefault("required_operator_action", None)
        drift_status.setdefault("human_explanation", "Temporal status unavailable.")

        holds = state.setdefault("holds", {})
        holds.setdefault("ingestion_hold", False)
        holds.setdefault("evaluation_hold", True)
        holds.setdefault("reason", "Truth epoch frozen")

        state.setdefault("evaluation_window", None)
        state.setdefault(
            "governance_pause",
            {
                "active": True,
                "reason": "Truth epoch frozen",
                "required_operator_action": self.policy.get("operator_action_name", "REQUEST_EVALUATION_WINDOW"),
            },
        )

        return state

    def load_state(self, market: str) -> Dict[str, Any]:
        path = self._state_path_for_market(market)
        if not path.exists():
            logger.warning("State file %s not found. Bootstrapping.", path)
            return self._bootstrap_state(market)
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            return self._ensure_state_shape(market, state)
        except Exception as exc:
            logger.error("Failed to read %s (%s). Bootstrapping.", path, exc)
            return self._bootstrap_state(market)

    def save_state(self, market: str, state: Dict[str, Any]) -> None:
        path = self._state_path_for_market(market)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
        logger.info("Updated temporal state for %s", market)

    def _append_audit_event(self, file_name: str, event: Dict[str, Any]) -> None:
        out_path = AUDIT_DIR / file_name
        payload = {"logged_at": datetime.datetime.utcnow().isoformat() + "Z", **event}
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

    def _log_drift_breach(self, market: str, te: str, ctt: str, drift_days: int, max_drift_days: int) -> None:
        self._append_audit_event(
            "drift_breaches.jsonl",
            {
                "event": "DRIFT_LIMIT_EXCEEDED",
                "market": market,
                "truth_epoch": te,
                "canonical_truth_time": ctt,
                "drift_days": drift_days,
                "max_drift_days": max_drift_days,
                "required_operator_action": self.policy.get("operator_action_name", "REQUEST_EVALUATION_WINDOW"),
            },
        )

    def _window_file_for_market(self, market: str) -> Path:
        return WINDOW_DIR / f"evaluation_window_{market}.json"

    def _load_latest_window(self, market: str) -> Optional[Dict[str, Any]]:
        path = self._window_file_for_market(market)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    # ----------------------------
    # Temporal Computation
    # ----------------------------
    def _parse_date(self, date_value: str) -> datetime.datetime:
        return datetime.datetime.strptime(date_value, "%Y-%m-%d")

    def get_latest_data_date(self, file_path: Path) -> Optional[str]:
        """
        Reads CSV and returns latest date string YYYY-MM-DD.
        Supports both Date/date and timestamp columns.
        """
        if not file_path.exists():
            logger.error("Data file %s missing", file_path)
            return None

        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return None

            date_col = None
            for candidate in ("Date", "date", "timestamp", "Timestamp", "datetime", "Datetime"):
                if candidate in df.columns:
                    date_col = candidate
                    break

            if date_col is None:
                return None

            parsed = pd.to_datetime(df[date_col], errors="coerce").dropna()
            if parsed.empty:
                return None

            return parsed.iloc[-1].strftime("%Y-%m-%d")
        except Exception as exc:
            logger.error("Failed reading latest date from %s: %s", file_path, exc)
            return None

    def update_rdt_ctt(self, market: str) -> Dict[str, Any]:
        """
        Updates RDT/CTT, computes drift vs frozen TE, enforces drift thresholds.
        Does NOT advance TE.
        """
        logger.info("Checking temporal state for %s...", market)
        state = self.load_state(market)
        data_path = self.data_us if market == "US" else self.data_india
        latest_date = self.get_latest_data_date(data_path)

        if not latest_date:
            logger.error("Could not determine RDT for %s", market)
            return state

        # Update RDT and CTT
        state["temporal_state"]["raw_data_time"]["timestamp"] = latest_date
        state["temporal_state"]["raw_data_time"]["source"] = str(data_path.relative_to(PROJECT_ROOT))
        state["temporal_state"]["raw_data_time"]["status"] = "VALID"

        prev_ctt = state["temporal_state"]["canonical_truth_time"].get("timestamp", "1970-01-01")
        if latest_date >= prev_ctt:
            state["temporal_state"]["canonical_truth_time"]["timestamp"] = latest_date
            state["temporal_state"]["canonical_truth_time"]["last_validated"] = datetime.datetime.utcnow().isoformat() + "Z"
            state["temporal_state"]["canonical_truth_time"]["status"] = "VALID"

        te_str = state["temporal_state"]["truth_epoch"].get("timestamp", "1970-01-01")
        ctt_str = state["temporal_state"]["canonical_truth_time"].get("timestamp", latest_date)

        dt_ctt = self._parse_date(ctt_str)
        dt_te = self._parse_date(te_str)
        drift_days = (dt_ctt - dt_te).days
        max_drift_days = self._max_drift_days_for_market(market)
        limit_exceeded = drift_days > max_drift_days

        drift_status = state["drift_status"]
        drift_status["ingestion_drift_days"] = 0
        drift_status["evaluation_drift_days"] = drift_days
        drift_status["max_drift_days"] = max_drift_days
        drift_status["drift_limit_exceeded"] = limit_exceeded
        drift_status["required_operator_action"] = None
        drift_status["critical_future_leakage"] = False

        if drift_days < 0:
            drift_status["status_code"] = "CRITICAL_FUTURE_LEAKAGE"
            drift_status["critical_future_leakage"] = True
            drift_status["message"] = (
                f"SYSTEM HALT: Truth ({te_str}) is ahead of canonical data ({ctt_str})."
            )
            drift_status["human_explanation"] = (
                "Temporal integrity failure: TE cannot be ahead of CTT."
            )
            state["holds"]["evaluation_hold"] = True
            state["holds"]["reason"] = "Critical future leakage detected."
            state["governance_pause"] = {
                "active": True,
                "reason": "Critical future leakage",
                "required_operator_action": "HUMAN_RECONCILIATION_REQUIRED",
            }
            logger.critical("Future leakage detected for %s", market)
        elif limit_exceeded:
            drift_status["status_code"] = "DRIFT_LIMIT_EXCEEDED"
            drift_status["message"] = (
                "EVAL REQUIRED - DRIFT WINDOW EXCEEDED. "
                f"Drift={drift_days}d exceeds max={max_drift_days}d."
            )
            drift_status["required_operator_action"] = (
                f"{self.policy.get('operator_action_name', 'REQUEST_EVALUATION_WINDOW')}"
                f"({market}, window_start, window_end)"
            )
            drift_status["human_explanation"] = (
                "Evaluation remains blocked because canonical data has moved too far ahead of frozen truth. "
                "Operator must submit bounded catch-up windows; TE will not auto-advance."
            )
            state["holds"]["evaluation_hold"] = True
            state["holds"]["reason"] = "Drift window exceeded. Operator-mediated catch-up required."
            state["governance_pause"] = {
                "active": True,
                "reason": "Drift threshold exceeded",
                "required_operator_action": drift_status["required_operator_action"],
            }
            self._log_drift_breach(market, te_str, ctt_str, drift_days, max_drift_days)
        elif drift_days > 0:
            drift_status["status_code"] = "EVALUATION_PENDING"
            drift_status["message"] = (
                f"Canonical data ({ctt_str}) is ahead of Truth Epoch ({te_str}). Drift={drift_days}d."
            )
            drift_status["human_explanation"] = (
                "Evaluation is pending under freeze. Operator may request bounded catch-up windows if needed."
            )
            state["holds"]["evaluation_hold"] = True
            state["holds"]["reason"] = "Evaluation pending under frozen truth epoch."
            state["governance_pause"] = {
                "active": True,
                "reason": "Evaluation pending under freeze",
                "required_operator_action": (
                    f"{self.policy.get('operator_action_name', 'REQUEST_EVALUATION_WINDOW')}"
                    f"({market}, window_start, window_end)"
                ),
            }
        else:
            drift_status["status_code"] = "SYNC"
            drift_status["message"] = "System synchronized at frozen truth epoch boundary."
            drift_status["human_explanation"] = "No evaluation drift is present."
            state["holds"]["evaluation_hold"] = False
            state["holds"]["reason"] = "No drift."
            state["governance_pause"] = {
                "active": False,
                "reason": "No drift",
                "required_operator_action": None,
            }

        latest_window = self._load_latest_window(market)
        state["evaluation_window"] = latest_window

        state["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        self.save_state(market, state)
        return state

    # ----------------------------
    # Operator Action Interface
    # ----------------------------
    def request_evaluation_window(self, market: str, window_start: str, window_end: str) -> Dict[str, Any]:
        """
        REQUEST_EVALUATION_WINDOW(market, window_start, window_end)
        Validates and persists a bounded catch-up request.

        Validation rule:
        [window_start, window_end] must be a subset of [TE, CTT].
        """
        state = self.load_state(market)
        te_str = state["temporal_state"]["truth_epoch"]["timestamp"]
        ctt_str = state["temporal_state"]["canonical_truth_time"]["timestamp"]

        event: Dict[str, Any] = {
            "event": "REQUEST_EVALUATION_WINDOW",
            "market": market,
            "window_start": window_start,
            "window_end": window_end,
            "truth_epoch": te_str,
            "canonical_truth_time": ctt_str,
            "status": "REJECTED",
            "reason": "",
        }

        try:
            dt_start = self._parse_date(window_start)
            dt_end = self._parse_date(window_end)
            dt_te = self._parse_date(te_str)
            dt_ctt = self._parse_date(ctt_str)
        except Exception:
            event["reason"] = "Invalid date format. Expected YYYY-MM-DD."
            self._append_audit_event("evaluation_window_requests.jsonl", event)
            return event

        if dt_start > dt_end:
            event["reason"] = "window_start must be <= window_end."
            self._append_audit_event("evaluation_window_requests.jsonl", event)
            return event

        if dt_start < dt_te or dt_end > dt_ctt:
            event["reason"] = "Requested window must be within [TE, CTT]."
            self._append_audit_event("evaluation_window_requests.jsonl", event)
            return event

        request_id = f"WIN-{market}-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        metadata = {
            "request_id": request_id,
            "market": market,
            "window_start": window_start,
            "window_end": window_end,
            "requested_at": datetime.datetime.utcnow().isoformat() + "Z",
            "status": "REQUESTED",
            "bounded_by": {"truth_epoch": te_str, "canonical_truth_time": ctt_str},
            "notes": "Bounded catch-up requested. No TE advancement performed.",
        }

        with open(self._window_file_for_market(market), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        state["evaluation_window"] = metadata
        state["holds"]["evaluation_hold"] = True
        state["holds"]["reason"] = "Operator evaluation window requested. Awaiting manual catch-up execution."
        state["governance_pause"] = {
            "active": True,
            "reason": "Awaiting operator-mediated bounded evaluation",
            "required_operator_action": "APPROVE_AND_RUN_BOUNDED_WINDOW",
        }
        state["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        self.save_state(market, state)

        event.update(
            {
                "status": "ACCEPTED",
                "reason": "Window validated and persisted. No automatic evaluation triggered.",
                "request_id": request_id,
            }
        )
        self._append_audit_event("evaluation_window_requests.jsonl", event)
        return {"event": event, "metadata": metadata}


def REQUEST_EVALUATION_WINDOW(market: str, window_start: str, window_end: str) -> Dict[str, Any]:
    """
    Explicit operator action interface requested by governance design.
    """
    orchestrator = TemporalOrchestrator()
    return orchestrator.request_evaluation_window(market=market, window_start=window_start, window_end=window_end)


def main() -> None:
    parser = argparse.ArgumentParser(description="Temporal Truth Orchestrator")
    subparsers = parser.add_subparsers(dest="command")

    request = subparsers.add_parser(
        "request-window",
        help="REQUEST_EVALUATION_WINDOW(market, window_start, window_end)",
    )
    request.add_argument("--market", required=True, choices=["US", "INDIA"])
    request.add_argument("--window-start", required=True, help="YYYY-MM-DD")
    request.add_argument("--window-end", required=True, help="YYYY-MM-DD")

    args = parser.parse_args()

    orchestrator = TemporalOrchestrator()

    if args.command == "request-window":
        result = orchestrator.request_evaluation_window(args.market, args.window_start, args.window_end)
        print(json.dumps(result, indent=2))
        return

    # Default behavior (backward compatible): update both markets
    orchestrator.update_rdt_ctt("US")
    orchestrator.update_rdt_ctt("INDIA")


if __name__ == "__main__":
    main()
