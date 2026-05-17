"""
Manifest-aware artifact loader for dashboard backend (RR-C.2 / RR-C.3).

Provides helpers that dashboard loaders can use to:
  1. Resolve artifact paths from the pipeline manifest
  2. Attach freshness and provenance metadata to responses
  3. Explain why data is missing with actionable details

Usage:
    from dashboard.backend.loaders.manifest_loader import (
        get_manifest,
        resolve_artifact_path,
        freshness_metadata,
    )
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
MANIFEST_PATH = PROJECT_ROOT / "logs" / "validation" / "pipeline_manifest.json"

_cached_manifest: Optional[Dict[str, Any]] = None
_cached_manifest_mtime: float = 0.0


def get_manifest(force_reload: bool = False) -> Optional[Dict[str, Any]]:
    """
    Load the pipeline manifest, caching it and only reloading when the
    file modification time changes.
    """
    global _cached_manifest, _cached_manifest_mtime

    if not MANIFEST_PATH.exists():
        return None

    try:
        current_mtime = MANIFEST_PATH.stat().st_mtime
        if not force_reload and _cached_manifest is not None and current_mtime == _cached_manifest_mtime:
            return _cached_manifest

        with MANIFEST_PATH.open("r", encoding="utf-8") as f:
            _cached_manifest = json.load(f)
        _cached_manifest_mtime = current_mtime
        return _cached_manifest
    except Exception as exc:
        logger.warning("Failed to load pipeline manifest: %s", exc)
        return None


def resolve_artifact_path(artifact_id: str) -> Optional[Path]:
    """
    Resolve an artifact path from the manifest.
    Returns None if the manifest is unavailable or the artifact is missing/not present.
    """
    manifest = get_manifest()
    if manifest is None:
        return None

    for entry in manifest.get("entries", []):
        if entry.get("artifact_id") == artifact_id and entry.get("status") == "present":
            resolved = PROJECT_ROOT / entry["path"]
            return resolved if resolved.exists() else None

    return None


def get_manifest_entry(artifact_id: str) -> Optional[Dict[str, Any]]:
    """Return the raw manifest entry dict for an artifact, or None."""
    manifest = get_manifest()
    if manifest is None:
        return None
    for entry in manifest.get("entries", []):
        if entry.get("artifact_id") == artifact_id:
            return entry
    return None


def freshness_metadata(
    source_artifact: str,
    *,
    produced_at: Optional[str] = None,
    market_mode: Optional[str] = None,
    manifest_entry: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build freshness and provenance metadata for a dashboard response (RR-C.3).

    Returns a dict suitable for merging into a dashboard API response:
        {
            "_freshness": {
                "source_artifact": "...",
                "produced_at": "ISO-8601 or null",
                "market_mode": "fixture",
                "age_seconds": 123 or null,
                "manifest_status": "present | missing | unavailable",
                "stale": true/false,
                "stale_reason": "..."
            }
        }
    """
    now = datetime.now(timezone.utc)

    entry = manifest_entry or get_manifest_entry(source_artifact)
    manifest_status = "unavailable"
    entry_produced_at = produced_at

    if entry is not None:
        manifest_status = entry.get("status", "unknown")
        if not entry_produced_at:
            entry_produced_at = entry.get("produced_at")

    age_seconds = None
    stale = False
    stale_reason = ""

    if entry_produced_at:
        try:
            produced_dt = datetime.fromisoformat(entry_produced_at)
            age_seconds = (now - produced_dt).total_seconds()
            # Consider data stale if older than 24 hours
            if age_seconds > 86400:
                stale = True
                stale_reason = f"Data is {age_seconds / 3600:.1f} hours old (threshold: 24h)"
        except (ValueError, TypeError):
            pass

    if manifest_status == "missing":
        stale = True
        stale_reason = entry.get("missing_reason", "Artifact not found on disk") if entry else "Artifact not found"

    return {
        "_freshness": {
            "source_artifact": source_artifact,
            "produced_at": entry_produced_at,
            "market_mode": market_mode or (entry.get("market_mode") if entry else None),
            "age_seconds": round(age_seconds, 1) if age_seconds is not None else None,
            "manifest_status": manifest_status,
            "stale": stale,
            "stale_reason": stale_reason,
        }
    }


def attach_freshness(
    payload: Dict[str, Any],
    source_artifact: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Convenience: attach freshness metadata to an existing payload dict.
    """
    payload.update(freshness_metadata(source_artifact, **kwargs))
    return payload
