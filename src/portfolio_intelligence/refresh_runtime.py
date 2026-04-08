from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict


class PortfolioRefreshRuntime:
    _locks: Dict[str, Lock] = {}
    _states: Dict[str, Dict[str, Any]] = {}
    _guard = Lock()

    @classmethod
    def _key(cls, market: str, portfolio_id: str) -> str:
        return f"{market.upper()}::{portfolio_id}"

    @classmethod
    def acquire(cls, market: str, portfolio_id: str) -> bool:
        key = cls._key(market, portfolio_id)
        with cls._guard:
            lock = cls._locks.setdefault(key, Lock())
        return lock.acquire(blocking=False)

    @classmethod
    def release(cls, market: str, portfolio_id: str) -> None:
        key = cls._key(market, portfolio_id)
        with cls._guard:
            lock = cls._locks.get(key)
        if lock and lock.locked():
            lock.release()

    @classmethod
    def mark_started(cls, market: str, portfolio_id: str, *, trigger: str, headless_auth: bool) -> None:
        key = cls._key(market, portfolio_id)
        cls._states[key] = {
            "status": "IN_PROGRESS",
            "last_started_at": datetime.now(timezone.utc).isoformat(),
            "last_finished_at": cls._states.get(key, {}).get("last_finished_at"),
            "last_error": None,
            "last_duration_seconds": None,
            "trigger": trigger,
            "headless_auth": headless_auth,
            "auth_mode": cls._states.get(key, {}).get("auth_mode"),
            "last_data_source": cls._states.get(key, {}).get("last_data_source"),
        }

    @classmethod
    def mark_success(
        cls,
        market: str,
        portfolio_id: str,
        *,
        duration_seconds: float,
        data_source: str,
        auth_mode: str,
    ) -> None:
        key = cls._key(market, portfolio_id)
        existing = cls._states.get(key, {})
        cls._states[key] = {
            **existing,
            "status": "IDLE",
            "last_finished_at": datetime.now(timezone.utc).isoformat(),
            "last_error": None,
            "last_duration_seconds": round(duration_seconds, 4),
            "last_data_source": data_source,
            "auth_mode": auth_mode,
        }

    @classmethod
    def mark_failure(cls, market: str, portfolio_id: str, *, error: str, auth_mode: str | None = None) -> None:
        key = cls._key(market, portfolio_id)
        existing = cls._states.get(key, {})
        cls._states[key] = {
            **existing,
            "status": "FAILED",
            "last_finished_at": datetime.now(timezone.utc).isoformat(),
            "last_error": error,
            "auth_mode": auth_mode or existing.get("auth_mode"),
        }

    @classmethod
    def snapshot(cls, market: str, portfolio_id: str) -> Dict[str, Any]:
        key = cls._key(market, portfolio_id)
        return {
            "status": "IDLE",
            "last_started_at": None,
            "last_finished_at": None,
            "last_error": None,
            "last_duration_seconds": None,
            "trigger": None,
            "headless_auth": False,
            "auth_mode": None,
            "last_data_source": None,
            **cls._states.get(key, {}),
        }