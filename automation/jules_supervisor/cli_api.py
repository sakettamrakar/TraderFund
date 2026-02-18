"""
Jules API/CLI abstraction layer.

API is preferred when credentials exist; CLI is used as fallback.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
from typing import Any, Dict, List

try:
    import requests
except Exception:  # pragma: no cover - optional dependency guard
    requests = None

from automation.jules.config import JULES_API_KEY, JULES_API_URL

logger = logging.getLogger(__name__)


def jules_api_available() -> bool:
    """Returns True when Jules API credentials are configured."""
    api_key = (JULES_API_KEY or os.environ.get("JULES_API_KEY", "")).strip()
    return bool(api_key)


def jules_cli_available() -> bool:
    """Returns True when Jules CLI binary is available."""
    return shutil.which("jules") is not None


def run_cli_command(args: List[str], timeout: int = 60) -> Dict[str, Any]:
    """
    Executes a Jules CLI command and captures stdout/stderr.
    """
    command = [str(a) for a in args]
    logger.info("[Executor][Jules][CLI] %s", " ".join(command))

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "command": command,
        }
    except FileNotFoundError as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"CLI not found: {exc}",
            "command": command,
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
            "command": command,
        }


def parse_cli_output(output: str) -> Dict[str, Any]:
    """
    Parses Jules CLI output into a normalized dictionary.
    """
    text = (output or "").strip()
    if not text:
        return {}

    # JSON output (preferred)
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            return {"items": parsed}
    except json.JSONDecodeError:
        pass

    # Key: value style output
    key_values: Dict[str, Any] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        key_values[key] = value.strip()

    if key_values:
        key_values["raw_text"] = text
        return key_values

    status_match = re.search(
        r"\b(COMPLETED|FAILED|TIMED_OUT|TIMEOUT|RUNNING|QUEUED|PENDING|IN_PROGRESS)\b",
        text,
        flags=re.IGNORECASE,
    )
    if status_match:
        return {"status": status_match.group(1).upper(), "raw_text": text}

    return {"raw_text": text}


def jules_api_post(path: str, body: Dict[str, Any] | None = None, timeout: int = 20) -> Dict[str, Any]:
    """
    Performs a POST request against Jules API.
    Returns a normalized dictionary: {ok, data, status_code, error, url}.
    """
    if not jules_api_available():
        return {"ok": False, "error": "API credentials missing."}
    if requests is None:
        return {"ok": False, "error": "requests module unavailable."}

    api_key = (JULES_API_KEY or os.environ.get("JULES_API_KEY", "")).strip()
    url = f"{JULES_API_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = {"X-Goog-Api-Key": api_key, "Content-Type": "application/json"}

    logger.info("[Executor][Jules][API] POST %s", url)

    try:
        response = requests.post(url, headers=headers, json=body or {}, timeout=timeout)
        payload: Any = None
        try:
            payload = response.json()
        except Exception:
            payload = {"raw_text": response.text or ""}

        if response.status_code >= 400:
            return {
                "ok": False,
                "status_code": response.status_code,
                "data": payload,
                "error": f"HTTP {response.status_code}",
                "url": url,
            }

        return {
            "ok": True,
            "status_code": response.status_code,
            "data": payload,
            "url": url,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "url": url}


def jules_api_get(path: str, timeout: int = 20) -> Dict[str, Any]:
    """
    Performs a GET request against Jules API.
    Returns a normalized dictionary: {ok, data, status_code, error, url}.
    """
    if not jules_api_available():
        return {"ok": False, "error": "API credentials missing."}
    if requests is None:
        return {"ok": False, "error": "requests module unavailable."}

    api_key = (JULES_API_KEY or os.environ.get("JULES_API_KEY", "")).strip()
    url = f"{JULES_API_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = {"X-Goog-Api-Key": api_key}

    logger.info("[Executor][Jules][API] GET %s", url)

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        payload: Any = None
        try:
            payload = response.json()
        except Exception:
            payload = {"raw_text": response.text or ""}

        if response.status_code >= 400:
            return {
                "ok": False,
                "status_code": response.status_code,
                "data": payload,
                "error": f"HTTP {response.status_code}",
                "url": url,
            }

        return {
            "ok": True,
            "status_code": response.status_code,
            "data": payload,
            "url": url,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "url": url}
