"""
Git utilities for deterministic commit-aware memory triggering.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAST_PROCESSED_COMMIT_PATH = PROJECT_ROOT / "automation" / "history" / "last_processed_commit.txt"
MEMORY_PATHSPEC = "docs/memory/"


def _run_git_command(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git executable was not found on PATH.") from exc

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        message = stderr or stdout or f"git {' '.join(args)} failed with exit code {result.returncode}"
        raise RuntimeError(message)

    return result.stdout.strip()


def get_current_head() -> str:
    """
    Returns the current HEAD commit hash.
    Raises a clear error if not executed inside a git repository.
    """
    try:
        return _run_git_command(["rev-parse", "HEAD"])
    except RuntimeError as exc:
        message = str(exc)
        if "not a git repository" in message.lower():
            raise RuntimeError("Current directory is not a git repository.") from exc
        raise RuntimeError(f"Failed to resolve current HEAD: {message}") from exc


def get_last_processed_commit() -> Optional[str]:
    """
    Returns the last processed commit hash from disk.
    Returns None if commit state file is missing or empty.
    """
    if not LAST_PROCESSED_COMMIT_PATH.exists():
        return None

    try:
        value = LAST_PROCESSED_COMMIT_PATH.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError(f"Failed to read {LAST_PROCESSED_COMMIT_PATH}: {exc}") from exc

    return value or None


def save_last_processed_commit(commit_hash: str) -> None:
    """
    Atomically persists the last processed commit hash.
    """
    normalized = (commit_hash or "").strip()
    if not normalized:
        raise ValueError("commit_hash must be a non-empty string.")

    LAST_PROCESSED_COMMIT_PATH.parent.mkdir(parents=True, exist_ok=True)

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=str(LAST_PROCESSED_COMMIT_PATH.parent),
            prefix="last_processed_commit.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(f"{normalized}\n")
            handle.flush()
            os.fsync(handle.fileno())
            tmp_path = Path(handle.name)

        os.replace(str(tmp_path), str(LAST_PROCESSED_COMMIT_PATH))
    except Exception:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def get_memory_diff_commits(from_commit: str, to_commit: str) -> list[str]:
    """
    Returns changed files under docs/memory/ between two commits.
    """
    if not from_commit or not to_commit:
        return []

    output = _run_git_command(
        ["diff", "--name-only", from_commit, to_commit, "--", MEMORY_PATHSPEC]
    )

    if not output:
        return []

    return sorted({line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()})
