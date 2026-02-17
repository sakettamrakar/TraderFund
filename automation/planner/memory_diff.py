"""
Memory Diff Analyzer
====================
Detects semantic changes in memory documents.
"""

import argparse
import difflib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .git_utils import (
        get_current_head,
        get_last_processed_commit,
        get_memory_diff_commits,
        save_last_processed_commit,
    )
except ImportError:
    try:
        from planner.git_utils import (
            get_current_head,
            get_last_processed_commit,
            get_memory_diff_commits,
            save_last_processed_commit,
        )
    except ImportError:
        from git_utils import (  # type: ignore
            get_current_head,
            get_last_processed_commit,
            get_memory_diff_commits,
            save_last_processed_commit,
        )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory_diff")

MEMORY_ROOT = Path("docs/memory")
SNAPSHOT_DIR = Path("automation/memory_snapshots")
NO_CHANGE = False
CHANGE_DETECTED = True


def get_current_memory_state() -> Dict[str, str]:
    """Reads all markdown files in docs/memory into a dict {path: content}."""
    state = {}
    if not MEMORY_ROOT.exists():
        logger.warning(f"Memory root {MEMORY_ROOT} does not exist.")
        return state

    for path in MEMORY_ROOT.rglob("*.md"):
        try:
            # Normalize path to unix style for consistency
            rel_path = path.relative_to(MEMORY_ROOT).as_posix()
            state[rel_path] = path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read {path}: {e}")
    return state

def load_snapshot(snapshot_id: str) -> Dict[str, str]:
    """Loads a previous memory state snapshot."""
    file_path = SNAPSHOT_DIR / f"{snapshot_id}.json"
    if not file_path.exists():
        logger.warning(f"Snapshot {snapshot_id} not found.")
        return {}
    
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load snapshot {file_path}: {e}")
        return {}

def save_snapshot(state: Dict[str, str], snapshot_id: str) -> None:
    """Saves current memory state as a snapshot."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = SNAPSHOT_DIR / f"{snapshot_id}.json"
    try:
        file_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        logger.info(f"Saved snapshot to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save snapshot: {e}")

def extract_section(content: str, line_no: int) -> str:
    """
    Identifies the markdown section header closest above the changed line.
    """
    lines = content.splitlines()
    # Iterate backwards from line_no
    for i in range(min(line_no, len(lines)-1), -1, -1):
        line = lines[i].strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "Global"

def _extract_sections_from_content(content: str) -> List[tuple]:
    """Extract (section_name, section_summary) pairs from markdown content."""
    sections = []
    lines = content.splitlines()
    current_section = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            # Save previous section
            if current_section and current_lines:
                summary = "\n".join(l for l in current_lines if l.strip())[:500]
                if summary:
                    sections.append((current_section, summary))
            current_section = stripped.lstrip("#").strip()
            current_lines = []
        elif current_section:
            current_lines.append(stripped)

    # Final section
    if current_section and current_lines:
        summary = "\n".join(l for l in current_lines if l.strip())[:500]
        if summary:
            sections.append((current_section, summary))

    return sections

def analyze_diff(old_state: Dict[str, str], new_state: Dict[str, str]) -> List[Dict[str, Any]]:
    """Compares two states and returns structured semantic changes."""
    changes = []
    
    all_files = set(old_state.keys()) | set(new_state.keys())
    
    for filename in all_files:
        old_content = old_state.get(filename, "")
        new_content = new_state.get(filename, "")
        
        if old_content == new_content:
            continue
            
        # If file added — parse sections for rich intent
        if not old_content:
            sections_found = _extract_sections_from_content(new_content)
            if sections_found:
                for sec_name, sec_content in sections_found:
                    changes.append({
                        "file": f"docs/memory/{filename}",
                        "change_type": "SECTION_ADDED",
                        "section": sec_name,
                        "content": sec_content[:500]
                    })
            else:
                # Fallback: no sections, use first meaningful lines
                summary = new_content.strip()[:300] or "File created."
                changes.append({
                    "file": f"docs/memory/{filename}",
                    "change_type": "FILE_ADDED",
                    "section": "Global",
                    "content": summary
                })
            continue

        # If file deleted
        if not new_content:
            changes.append({
                "file": f"docs/memory/{filename}",
                "change_type": "FILE_DELETED",
                "section": "Global",
                "content": "File deleted."
            })
            continue
            
        # Content changed - calculate diff
        diff = difflib.ndiff(old_content.splitlines(), new_content.splitlines())
        
        line_idx = 0
        for line in diff:
            code = line[0]
            text = line[2:]
            
            if code == ' ':
                line_idx += 1
            elif code == '-':
                # Deletion (we don't increment line_idx for deletions in new file)
                # But we might want to capture what was removed
                pass 
            elif code == '+':
                # Addition / Modification
                # Identify section
                section = extract_section(new_content, line_idx)
                
                # Check if it looks like an invariant (bullet or numbered list)
                if text.strip().startswith(("-", "*", "1.")):
                    changes.append({
                        "file": f"docs/memory/{filename}",
                        "change_type": "INVARIANT_ADDED/MODIFIED",
                        "section": section,
                        "content": text.strip()
                    })
                else:
                    changes.append({
                        "file": f"docs/memory/{filename}",
                        "change_type": "CONTENT_CHANGED",
                        "section": section,
                        "content": text.strip()
                    })
                line_idx += 1
            elif code == '?':
                pass # Intraline diff hints
                
    # Deduplicate changes (adjacent lines might trigger multiple events)
    # For now, simple list.
    return changes


def _write_no_change_output(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("[]", encoding="utf-8")


def detect_commit_memory_changes() -> Dict[str, Any]:
    """
    Commit-aware trigger gate for memory planning.
    Returns a structured result:
      changed: bool
      changed_files: list[str]
      current_head: Optional[str]
      last_processed: Optional[str]
      pending_commit: Optional[str] (set only when planning should run)
      fallback_to_snapshot: bool
      error: Optional[str]
    """
    result: Dict[str, Any] = {
        "changed": NO_CHANGE,
        "changed_files": [],
        "current_head": None,
        "last_processed": None,
        "pending_commit": None,
        "fallback_to_snapshot": False,
        "error": None,
    }

    try:
        current_head = get_current_head()
        last_processed = get_last_processed_commit()
        result["current_head"] = current_head
        result["last_processed"] = last_processed

        logger.info("[CommitTrigger] Current HEAD: %s", current_head)
        logger.info("[CommitTrigger] Last Processed: %s", last_processed)

        # Case 1 — First run
        if last_processed is None:
            save_last_processed_commit(current_head)
            logger.info("First run — initializing commit baseline")
            logger.info("[CommitTrigger] Changed Memory Files: []")
            return result

        # Case 2 — No new commit
        if current_head == last_processed:
            logger.info("[CommitTrigger] Changed Memory Files: []")
            return result

        # Case 3 — New commit(s)
        changed_files = get_memory_diff_commits(last_processed, current_head)
        logger.info("[CommitTrigger] Changed Memory Files: %s", changed_files)

        if not changed_files:
            # Advance baseline for non-memory commits to avoid re-processing.
            save_last_processed_commit(current_head)
            return result

        result["changed"] = CHANGE_DETECTED
        result["changed_files"] = changed_files
        result["pending_commit"] = current_head
        return result
    except Exception as exc:
        # Safety: if git path fails, keep snapshot diff behavior alive.
        result["changed"] = CHANGE_DETECTED
        result["fallback_to_snapshot"] = True
        result["error"] = str(exc)
        logger.warning(
            "[CommitTrigger] Git command failed (%s). Falling back to snapshot diff.",
            exc,
        )
        logger.info("[CommitTrigger] Changed Memory Files: []")
        return result


def mark_commit_processed(commit_hash: Optional[str]) -> None:
    """
    Persist a commit as processed only after planner success.
    """
    if not commit_hash:
        return
    save_last_processed_commit(commit_hash)
    logger.info("[CommitTrigger] Saved last processed commit: %s", commit_hash)


def main() -> int:
    parser = argparse.ArgumentParser(description="Memory Diff Analyzer")
    parser.add_argument("--snapshot", default="last_known_good", help="Snapshot ID to compare against")
    parser.add_argument("--save", action="store_true", help="Update snapshot after analysis")
    parser.add_argument("--output", default="memory_diff.json", help="Output JSON file")
    args = parser.parse_args()

    output_path = Path(args.output)

    trigger_state = detect_commit_memory_changes()
    if not trigger_state.get("changed", NO_CHANGE):
        _write_no_change_output(output_path)
        return 0

    current_state = get_current_memory_state()
    previous_state = load_snapshot(args.snapshot)

    if not previous_state:
        logger.info("No previous snapshot found. Assuming initial state or full re-scan needed.")
        _write_no_change_output(output_path)
        if args.save:
            save_snapshot(current_state, args.snapshot)
        return 0

    diffs = analyze_diff(previous_state, current_state)

    if diffs:
        logger.info(f"Detected {len(diffs)} semantic changes.")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(diffs, indent=2), encoding="utf-8")
        logger.info(f"Wrote semantic diffs to {output_path}")
    else:
        logger.info("No memory changes detected.")
        _write_no_change_output(output_path)

    if args.save:
        save_snapshot(current_state, args.snapshot)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
