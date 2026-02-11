"""
Memory Diff Analyzer
====================
Detects semantic changes in memory documents.
"""

import os
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import difflib
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory_diff")

MEMORY_ROOT = Path("docs/memory")
SNAPSHOT_DIR = Path("automation/memory_snapshots")

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

def analyze_diff(old_state: Dict[str, str], new_state: Dict[str, str]) -> List[Dict[str, Any]]:
    """Compares two states and returns structured semantic changes."""
    changes = []
    
    all_files = set(old_state.keys()) | set(new_state.keys())
    
    for filename in all_files:
        old_content = old_state.get(filename, "")
        new_content = new_state.get(filename, "")
        
        if old_content == new_content:
            continue
            
        # If file added
        if not old_content:
            changes.append({
                "file": f"docs/memory/{filename}",
                "change_type": "FILE_ADDED",
                "section": "Global",
                "content": "File created."
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

def main():
    parser = argparse.ArgumentParser(description="Memory Diff Analyzer")
    parser.add_argument("--snapshot", default="last_known_good", help="Snapshot ID to compare against")
    parser.add_argument("--save", action="store_true", help="Update snapshot after analysis")
    parser.add_argument("--output", default="memory_diff.json", help="Output JSON file")
    args = parser.parse_args()
    
    current_state = get_current_memory_state()
    previous_state = load_snapshot(args.snapshot)
    
    if not previous_state:
        logger.info("No previous snapshot found. Assuming initial state or full re-scan needed.")
        # If no snapshot, maybe we treat everything as new? 
        # For now, let's just save the current state and exit if it's the first run
        if args.save:
            save_snapshot(current_state, args.snapshot)
        return

    diffs = analyze_diff(previous_state, current_state)
    
    if diffs:
        logger.info(f"Detected {len(diffs)} semantic changes.")
        output_path = Path(args.output)
        output_path.write_text(json.dumps(diffs, indent=2), encoding="utf-8")
        logger.info(f"Wrote semantic diffs to {output_path}")
    else:
        logger.info("No memory changes detected.")
        # Create empty list file
        Path(args.output).write_text("[]", encoding="utf-8")

    if args.save:
        save_snapshot(current_state, args.snapshot)

if __name__ == "__main__":
    main()
