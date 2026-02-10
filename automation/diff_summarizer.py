"""
Diff Summarizer
================
Produces a short human-readable summary of current uncommitted changes.
"""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def summarize() -> str:
    """
    Generate a human-readable summary of uncommitted git changes.

    Returns:
        A formatted summary string of the current diff.
    """
    # Get the full diff
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        stat_output = result.stdout.strip() if result.returncode == 0 else ""
    except FileNotFoundError:
        stat_output = "(git not available)"

    # Get staged diff stat
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "--cached"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        staged_output = result.stdout.strip() if result.returncode == 0 else ""
    except FileNotFoundError:
        staged_output = ""

    # Get untracked files
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        untracked = result.stdout.strip().splitlines() if result.returncode == 0 else []
    except FileNotFoundError:
        untracked = []

    # Build summary
    parts = []
    parts.append("=" * 60)
    parts.append("  AUTONOMOUS LOOP — DIFF SUMMARY")
    parts.append("=" * 60)

    if stat_output:
        parts.append("\n  Unstaged Changes:")
        for line in stat_output.splitlines():
            parts.append(f"    {line}")

    if staged_output:
        parts.append("\n  Staged Changes:")
        for line in staged_output.splitlines():
            parts.append(f"    {line}")

    if untracked:
        parts.append(f"\n  Untracked Files ({len(untracked)}):")
        for f in untracked[:20]:
            parts.append(f"    + {f}")
        if len(untracked) > 20:
            parts.append(f"    ... and {len(untracked) - 20} more")

    if not stat_output and not staged_output and not untracked:
        parts.append("\n  No changes detected.")

    parts.append("\n" + "=" * 60)

    return "\n".join(parts)
