import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic, sleep
from typing import Any, Dict

from automation.jules_supervisor.cli_api import (
    jules_api_available,
    jules_api_get,
    jules_cli_available,
    parse_cli_output,
    run_cli_command,
)

logger = logging.getLogger(__name__)

TERMINAL = {"COMPLETED", "FAILED", "TIMED_OUT"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_status(raw_status: str | None, payload: Dict[str, Any] | None = None) -> str:
    """
    Normalize vendor-specific statuses into pipeline statuses.
    """
    if payload:
        outputs = payload.get("outputs")
        if isinstance(outputs, list) and outputs:
            return "COMPLETED"

    token = (raw_status or "").upper().replace("-", "_").replace(" ", "_")
    mapping = {
        "DONE": "COMPLETED",
        "SUCCESS": "COMPLETED",
        "SUCCEEDED": "COMPLETED",
        "COMPLETE": "COMPLETED",
        "COMPLETED": "COMPLETED",
        "ERROR": "FAILED",
        "FAILED": "FAILED",
        "CANCELLED": "FAILED",
        "TIMED_OUT": "TIMED_OUT",
        "TIMEOUT": "TIMED_OUT",
        "RUNNING": "RUNNING",
        "QUEUED": "QUEUED",
        "PENDING": "PENDING",
        "IN_PROGRESS": "RUNNING",
    }
    return mapping.get(token, "UNKNOWN")


def _status_from_api(task_id: str) -> Dict[str, Any]:
    task_token = task_id.split("/")[-1]
    candidate_paths = [task_id, f"tasks/{task_token}", f"sessions/{task_token}"]

    for path in candidate_paths:
        response = jules_api_get(path)
        if not response.get("ok"):
            continue

        payload = response.get("data")
        if not isinstance(payload, dict):
            payload = {}

        raw_status = (
            payload.get("status")
            or payload.get("state")
            or payload.get("phase")
            or payload.get("result")
        )

        status = _normalize_status(raw_status, payload=payload)
        return {
            "task_id": task_id,
            "status": status,
            "raw_status": raw_status or "UNKNOWN",
            "last_update": _utc_now(),
            "source": "API",
            "payload": payload,
            "error": None,
        }

    return {
        "task_id": task_id,
        "status": "UNKNOWN",
        "raw_status": "UNKNOWN",
        "last_update": _utc_now(),
        "source": "API",
        "payload": {},
        "error": "API request failed for all candidate endpoints.",
    }


def _status_from_cli(task_id: str) -> Dict[str, Any]:
    attempts = [
        ["jules", "status", task_id, "--json"],
        ["jules", "status", task_id],
    ]

    for command in attempts:
        result = run_cli_command(command, timeout=30)
        if not result.get("ok"):
            continue

        parsed = parse_cli_output(result.get("stdout", ""))
        raw_status = (
            parsed.get("status")
            or parsed.get("state")
            or parsed.get("phase")
            or parsed.get("result")
            or "UNKNOWN"
        )

        status = _normalize_status(str(raw_status), payload=parsed if isinstance(parsed, dict) else None)
        return {
            "task_id": task_id,
            "status": status,
            "raw_status": str(raw_status),
            "last_update": _utc_now(),
            "source": "CLI",
            "payload": parsed if isinstance(parsed, dict) else {"raw_text": result.get("stdout", "")},
            "error": None,
        }

    return {
        "task_id": task_id,
        "status": "UNKNOWN",
        "raw_status": "UNKNOWN",
        "last_update": _utc_now(),
        "source": "CLI",
        "payload": {},
        "error": "CLI status command failed.",
    }


def jules_status_details(task_id: str) -> Dict[str, Any]:
    """
    Returns structured status details using API first, CLI fallback.
    """
    if jules_api_available():
        api_record = _status_from_api(task_id)
        if api_record.get("status") != "UNKNOWN":
            return api_record
        if jules_cli_available():
            cli_record = _status_from_cli(task_id)
            if cli_record.get("status") != "UNKNOWN":
                return cli_record
        return api_record

    if jules_cli_available():
        return _status_from_cli(task_id)

    return {
        "task_id": task_id,
        "status": "UNKNOWN",
        "raw_status": "UNKNOWN",
        "last_update": _utc_now(),
        "source": "NONE",
        "payload": {},
        "error": "Neither Jules API credentials nor Jules CLI are available.",
    }


def jules_status(task_id: str) -> str:
    """
    Returns the normalized Jules task status.
    API first; CLI fallback.
    """
    return jules_status_details(task_id).get("status", "UNKNOWN")


def wait_for_jules_task(task_id: str, timeout: int = 1800, poll_interval: int = 10) -> Dict[str, Any]:
    """
    Polls the Jules executor for task status.
    Stops when status = COMPLETED | FAILED | TIMED_OUT.
    """
    started = monotonic()
    polls = 0
    last_record: Dict[str, Any] = {
        "task_id": task_id,
        "status": "UNKNOWN",
        "last_update": _utc_now(),
        "source": "NONE",
        "payload": {},
        "error": None,
    }

    while monotonic() - started < timeout:
        polls += 1
        record = jules_status_details(task_id)
        record["poll_count"] = polls
        record["duration_seconds"] = round(monotonic() - started, 2)
        last_record = record

        status = record.get("status", "UNKNOWN")
        if status in TERMINAL:
            return record

        sleep(max(1, poll_interval))

    timeout_record = dict(last_record)
    timeout_record["status"] = "TIMED_OUT"
    timeout_record["last_update"] = _utc_now()
    timeout_record["duration_seconds"] = round(monotonic() - started, 2)
    timeout_record["poll_count"] = polls
    timeout_record["error"] = timeout_record.get("error") or "Monitor timeout exceeded."
    return timeout_record


class TaskMonitor:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.run_dir = Path("automation/runs") / run_id

    def wait(self, task_id: str, timeout: int = 1800) -> Dict[str, Any]:
        """
        Waits for a Jules task and writes status details to jules_status.json.
        """
        logger.info("Monitor: waiting for task %s (timeout=%ss)", task_id, timeout)
        status_record = wait_for_jules_task(task_id, timeout=timeout)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        (self.run_dir / "jules_status.json").write_text(
            json.dumps(status_record, indent=2),
            encoding="utf-8",
        )
        logger.info(
            "Monitor: task %s finished with status %s (source=%s)",
            task_id,
            status_record.get("status"),
            status_record.get("source"),
        )
        return status_record
