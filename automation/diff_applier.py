"""
Diff Applier
=============
Applies unified diff text to the git working tree.
Rejects diffs that touch protected paths.
Splits LLM output into per-file patches and applies each independently.
"""

import subprocess
import tempfile
from pathlib import Path

# New Imports
from automation_config import config, SecurityViolation

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROTECTED_PREFIXES = ["docs/memory/", "docs/epistemic/"]


def _extract_and_split(raw: str) -> list[tuple[str, str]]:
    """Extract diff content, strip markdown, and split into per-file patches.
    Returns list of (filepath, patch_text) tuples."""
    lines = raw.splitlines()
    # Strip markdown fences
    clean = []
    for line in lines:
        if line.strip().startswith("```"):
            continue
        clean.append(line)

    # Split into per-file segments at "--- a/" boundaries
    segments: list[list[str]] = []
    current: list[str] = []

    for line in clean:
        if line.startswith("--- a/") or line.strip().startswith("--- a/"):
            if current:
                segments.append(current)
            current = []
            # Inject diff --git header
            path = line.strip()[6:]
            current.append(f"diff --git a/{path} b/{path}")
            current.append(line)
        elif line.startswith("diff --git"):
            if current:
                segments.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        segments.append(current)

    # Build per-file patches
    results = []
    for seg in segments:
        text = "\n".join(seg) + "\n"
        # Extract file path
        path = ""
        for l in seg:
            if l.startswith("+++ b/") or l.strip().startswith("+++ b/"):
                path = l.strip()[6:]
                break
        if path:
            results.append((path, text))

    return results


def _is_protected(path: str) -> bool:
    """Check if a file path is under protected prefixes."""
    # Normalize path and check
    if ".." in path:
        return True # Suspicious
    return any(path.startswith(p) for p in PROTECTED_PREFIXES)


def _apply_single_patch(patch_text: str, filepath: str) -> tuple[bool, str]:
    """Apply a single-file patch to the working tree."""

    # DRY RUN CHECK
    if config.dry_run:
        # In dry run, we simulate success by checking if it applies cleanly
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".patch", delete=False, encoding="utf-8"
        ) as f:
            f.write(patch_text)
            patch_path = f.name

        try:
            result = subprocess.run(
                ["git", "apply", "--check", patch_path],
                capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            )
            if result.returncode == 0:
                return True, f"{filepath}: (DRY RUN) validated"
            else:
                return False, f"{filepath}: (DRY RUN) validation failed — {result.stderr.strip()[:200]}"
        finally:
            Path(patch_path).unlink(missing_ok=True)

    # REAL RUN
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".patch", delete=False, encoding="utf-8"
    ) as f:
        f.write(patch_text)
        patch_path = f.name

    try:
        # Try strict apply first
        result = subprocess.run(
            ["git", "apply", "--verbose", patch_path],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if result.returncode == 0:
            return True, f"{filepath}: applied"

        # Try with whitespace tolerance
        result2 = subprocess.run(
            ["git", "apply", "--verbose", "--ignore-whitespace", patch_path],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if result2.returncode == 0:
            return True, f"{filepath}: applied (whitespace-tolerant)"

        # Try with --3way merge
        result3 = subprocess.run(
            ["git", "apply", "--3way", patch_path],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if result3.returncode == 0:
            return True, f"{filepath}: applied (3-way merge)"

        return False, f"{filepath}: FAILED — {result.stderr.strip()[:200]}"

    finally:
        Path(patch_path).unlink(missing_ok=True)


def apply(raw_diff: str) -> tuple[bool, str]:
    """
    Apply a unified diff to the working tree.
    Splits into per-file patches and applies each independently.

    Returns:
        (any_success, message) tuple.
    """
    if not raw_diff or not raw_diff.strip():
        return False, "Empty diff — no-op."

    if "NO_CHANGES_REQUIRED" in raw_diff:
        return True, "No changes required."

    # Split into per-file patches
    file_patches = _extract_and_split(raw_diff)
    if not file_patches:
        return False, "No valid unified diff found in output."

    results = []
    applied = 0
    blocked = 0
    failed = 0

    for filepath, patch_text in file_patches:
        # RUNTIME GUARD: Check for protected path violation
        if _is_protected(filepath):
            violation_msg = f"Attempted to modify protected path: {filepath}"
            if config.journal:
                config.journal.log_violation(violation_msg)

            # Raise SecurityViolation to abort the run immediately
            raise SecurityViolation(violation_msg)

        success, msg = _apply_single_patch(patch_text, filepath)
        results.append(f"  {'✅' if success else '❌'} {msg}")

        if success:
            applied += 1
            if config.journal:
                config.journal.log_change(filepath)
        else:
            failed += 1

    summary = f"Applied: {applied}, Failed: {failed}, Blocked: {blocked}"
    if config.dry_run:
        summary += " (DRY RUN)"

    detail = "\n".join(results)
    any_success = applied > 0
    return any_success, f"{summary}\n{detail}"
