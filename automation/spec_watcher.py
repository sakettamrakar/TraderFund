"""
Spec Watcher
=============
Detects changed specification files under docs/memory/ using git diff.
"""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def changed_specs() -> list[str]:
    """
    Return a list of changed files under docs/memory/ relative to the last commit.

    Uses `git diff --name-only HEAD` to detect unstaged and staged changes,
    and `git diff --name-only --cached` for staged-only changes.
    Merges both lists and filters to docs/memory/ paths only.

    Returns:
        List of relative file paths that changed under docs/memory/.
    """
    changed = set()

    # Unstaged changes
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode == 0:
            changed.update(result.stdout.strip().splitlines())
    except FileNotFoundError:
        pass

    # Staged changes
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode == 0:
            changed.update(result.stdout.strip().splitlines())
    except FileNotFoundError:
        pass

    # Untracked files under docs/memory/
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "docs/memory/"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode == 0:
            changed.update(result.stdout.strip().splitlines())
    except FileNotFoundError:
        pass

    # Filter to docs/memory/ only, exclude empty strings
    spec_files = sorted(
        f for f in changed
        if f.startswith("docs/memory/") and f.strip()
    )

    return spec_files
