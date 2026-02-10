"""
Approval Gate
==============
Shows diff summary, changed file count, pauses for explicit "yes" approval, and commits.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def approve() -> bool:
    """
    Show the current git status and diff summary, wait for explicit 'yes' before committing.

    Returns:
        True if changes were committed, False if user aborted.
    """
    # Get git status
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        status = result.stdout.strip() if result.returncode == 0 else "(unable to read git status)"
    except FileNotFoundError:
        print("  ERROR: git not found.")
        return False

    if not status:
        print("  No changes to commit.")
        return False

    # Get diff stat
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        diff_stat = result.stdout.strip() if result.returncode == 0 else ""
    except FileNotFoundError:
        diff_stat = ""

    # Count changed files
    changed_files = [line for line in status.splitlines() if line.strip()]
    file_count = len(changed_files)

    print("\n" + "=" * 60)
    print("  APPROVAL GATE — HUMAN REVIEW REQUIRED")
    print("=" * 60)

    print(f"\n  Changed files: {file_count}")
    print()
    for line in changed_files:
        print(f"    {line}")

    if diff_stat:
        print("\n  Diff summary:")
        for line in diff_stat.splitlines():
            print(f"    {line}")

    print()
    print("  To inspect full diffs, run: git diff")
    print()

    try:
        response = input("  Type 'yes' to approve and commit, anything else to cancel: ")
    except (EOFError, KeyboardInterrupt):
        print("\n  Aborted by user.")
        return False

    if response.strip().lower() != "yes":
        print("  Commit aborted by user.")
        return False

    # Stage all changes
    subprocess.run(
        ["git", "add", "--all"],
        cwd=str(PROJECT_ROOT),
    )

    # Commit
    result = subprocess.run(
        ["git", "commit", "-m", "autonomous update"],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
    )

    if result.returncode == 0:
        print(f"\n  Committed: {result.stdout.strip().splitlines()[0]}")
        return True
    else:
        print(f"\n  Commit failed: {result.stderr.strip()}")
        return False
