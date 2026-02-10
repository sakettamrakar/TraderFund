"""
Diff Applier
=============
Applies unified diff text to the git working tree.
Rejects diffs that touch protected paths.
"""

import subprocess
import tempfile
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROTECTED_PREFIXES = ["docs/memory/", "docs/epistemic/"]


def _extract_diff_blocks(raw: str) -> str:
    """Extract only unified diff content, stripping markdown fences and prose."""
    lines = raw.splitlines()
    result = []
    in_diff = False

    for line in lines:
        # Skip markdown fences
        if line.strip().startswith("```"):
            in_diff = not in_diff
            continue
        # Detect diff header
        if line.startswith("diff --git") or line.startswith("--- ") or line.startswith("+++ "):
            in_diff = True
        if line.startswith("diff --git"):
            in_diff = True
        if in_diff:
            result.append(line)

    # If no diff headers found, try treating entire input as a diff
    if not result:
        has_diff_markers = any(
            l.startswith(("diff --git", "--- ", "+++ ", "@@"))
            for l in lines
        )
        if has_diff_markers:
            return raw

    return "\n".join(result) + "\n" if result else ""


def _check_protected_paths(diff_text: str) -> str | None:
    """Return error message if diff touches protected paths."""
    for line in diff_text.splitlines():
        if line.startswith("+++ b/") or line.startswith("--- a/"):
            path = line.split("/", 1)[1] if "/" in line else ""
            for prefix in PROTECTED_PREFIXES:
                if path.startswith(prefix):
                    return f"BLOCKED: Diff touches protected path: {path}"
    return None


def apply(raw_diff: str) -> tuple[bool, str]:
    """
    Apply a unified diff to the working tree.

    Args:
        raw_diff: Raw text from LLM, potentially containing unified diff.

    Returns:
        (success, message) tuple.
    """
    if not raw_diff or not raw_diff.strip():
        return False, "Empty diff — no-op."

    # Sentinel for no-change responses
    if "NO_CHANGES_REQUIRED" in raw_diff:
        return True, "No changes required."

    # Extract actual diff content
    diff_text = _extract_diff_blocks(raw_diff)
    if not diff_text.strip():
        return False, "No valid unified diff found in output."

    # Guard: reject diffs touching protected paths
    blocked = _check_protected_paths(diff_text)
    if blocked:
        return False, blocked

    # Write diff to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".patch", delete=False, encoding="utf-8"
    ) as f:
        f.write(diff_text)
        patch_path = f.name

    try:
        # Dry run first
        check = subprocess.run(
            ["git", "apply", "--check", "--verbose", patch_path],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if check.returncode != 0:
            return False, f"Patch dry-run failed:\n{check.stderr.strip()}"

        # Apply for real
        result = subprocess.run(
            ["git", "apply", "--verbose", patch_path],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            return False, f"Patch apply failed:\n{result.stderr.strip()}"

        return True, f"Patch applied successfully.\n{result.stderr.strip()}"

    finally:
        Path(patch_path).unlink(missing_ok=True)
