"""
Stability Adapter — Component Stability Score Reader
=====================================================
Reads automation/history/stability_state.json and returns the stability score
for a named component.

Contract:
  • Returns 1.0 (fully stable) if the file is missing, malformed, or the
    component key is absent — never raises, never crashes.
  • Scores are clamped to [0.0, 1.0] regardless of file content.
  • Allows path override for testability without patching or mocking.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

# ── Constants ─────────────────────────────────────────────────────────────────

_DEFAULT_STABILITY: float = 1.0
_STATE_RELATIVE_PATH: str = os.path.join("automation", "history", "stability_state.json")


# ── Workspace root resolution ─────────────────────────────────────────────────

def _locate_workspace_root() -> Path:
    """
    Walk upward from this file until we find a directory that contains a
    'src' sub-directory — that is the workspace root.  Caps at 6 levels to
    prevent infinite traversal on misconfigured environments.
    """
    current = Path(__file__).resolve().parent
    for _ in range(8):
        if (current / "src").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    # Fallback: three levels up from src/feedback/
    return Path(__file__).resolve().parents[2]


# ── Adapter ───────────────────────────────────────────────────────────────────

class StabilityAdapter:
    """
    Reads component stability scores from the persistent stability state file.

    Expected JSON structure::

        {
            "MetaAnalysis": 0.85,
            "ConvergenceEngine": 0.90,
            "StrategyRegistry": 0.95
        }

    Any read or parse error silently returns the safe default (1.0).

    Parameters
    ----------
    state_path : str | None
        Override path for testing.  Pass the full path to a temporary JSON
        file.  ``None`` resolves the standard workspace-relative location.
    """

    def __init__(self, state_path: Optional[str] = None) -> None:
        if state_path is not None:
            self._path = Path(state_path)
        else:
            root = _locate_workspace_root()
            self._path = root / _STATE_RELATIVE_PATH

    def get_stability(self, component: str) -> float:
        """
        Return stability score ∈ [0.0, 1.0] for the named component.

        Returns ``1.0`` on any failure condition:
          - file not found
          - malformed JSON
          - component key absent
          - value not numeric
        """
        try:
            if not self._path.exists():
                return _DEFAULT_STABILITY
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, dict):
                return _DEFAULT_STABILITY
            raw_value = data.get(component)
            if raw_value is None:
                return _DEFAULT_STABILITY
            return max(0.0, min(1.0, float(raw_value)))
        except Exception:  # noqa: BLE001 — any I/O or parse failure is safe
            return _DEFAULT_STABILITY

    @property
    def state_path(self) -> Path:
        """Expose resolved path for observability / logging."""
        return self._path
