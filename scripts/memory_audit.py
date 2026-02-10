"""
Memory Quality Audit Script
============================
Read-only analysis of project memory against QUALITY.md invariants.
Outputs a structured report to stdout and docs/memory/AUDIT_REPORT.md.

Usage:
    python scripts/memory_audit.py
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = PROJECT_ROOT / "docs" / "memory"
DECISIONS_DIR = MEMORY_DIR / "decisions"

REQUIRED_FILES = [
    MEMORY_DIR / "index.md",
    MEMORY_DIR / "QUALITY.md",
    MEMORY_DIR / "DECISION_PROTOCOL.md",
]

VISION_FILE = MEMORY_DIR / "00_vision" / "vision.md"
BOUNDARIES_FILE = MEMORY_DIR / "01_scope" / "boundaries.md"

# Code block threshold: flag if a single fenced block exceeds this many lines
CODE_BLOCK_LINE_THRESHOLD = 15

# Minimum overlap word-set size to flag potential duplication
OVERLAP_HEADING_THRESHOLD = 3

# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

results: list[dict] = []


def record(invariant: str, status: str, detail: str):
    results.append({"invariant": invariant, "status": status, "detail": detail})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_text(path: Path) -> str | None:
    """Read file contents or return None if missing."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None


def collect_memory_files() -> list[Path]:
    """Collect all .md and .yaml files under docs/memory/."""
    files = []
    for ext in ("*.md", "*.yaml", "*.yml"):
        files.extend(MEMORY_DIR.rglob(ext))

    # Exclude the report itself and appendix to prevent self-auditing
    files = [f for f in files if f.name != "AUDIT_REPORT.md" and "_appendix" not in f.parts]

    return sorted(files)


def extract_headings(text: str) -> list[str]:
    """Extract markdown headings from text."""
    return re.findall(r"^#{1,4}\s+(.+)$", text, re.MULTILINE)


def count_code_blocks(text: str) -> list[int]:
    """Return list of line-counts for each fenced code block."""
    blocks = re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    return [block.count("\n") + 1 for block in blocks]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_required_files():
    """Verify that required memory files exist."""
    all_present = True
    for path in REQUIRED_FILES:
        rel = path.relative_to(PROJECT_ROOT)
        if path.exists():
            record("Required Files", PASS, f"`{rel}` exists")
        else:
            record("Required Files", FAIL, f"`{rel}` is MISSING")
            all_present = False
    return all_present


def check_authority_invariant():
    """
    Authority: vision, scope, and decisions should each live in exactly one place.
    Heuristic: search all memory files for headings containing key terms.
    """
    memory_files = collect_memory_files()
    concern_files = defaultdict(list)

    keywords = {
        "vision": ["vision", "philosophy", "why this project"],
        "scope": ["scope", "boundaries", "non-goals", "out of scope"],
        "decisions": ["ADR", "decision record", "architectural decision"],
    }

    for path in memory_files:
        text = read_text(path)
        if text is None:
            continue
        headings_lower = " ".join(extract_headings(text)).lower()
        rel = str(path.relative_to(PROJECT_ROOT))

        for concern, terms in keywords.items():
            for term in terms:
                if term.lower() in headings_lower:
                    # For decisions, individual ADR files are valid child records; ignore them (authority is README)
                    if concern == "decisions" and path.name.startswith("ADR-"):
                        continue
                    concern_files[concern].append(rel)
                    break

    for concern, files in concern_files.items():
        unique = list(dict.fromkeys(files))  # deduplicate preserving order
        if len(unique) <= 1:
            record("Authority Invariant", PASS,
                   f"`{concern}` is defined in {unique[0] if unique else 'one place'}")
        else:
            record("Authority Invariant", WARN,
                   f"`{concern}` headings found in {len(unique)} files: {', '.join(unique)}. "
                   "Verify only one is authoritative.")

    # Decisions should be under /decisions/
    for path in memory_files:
        rel = str(path.relative_to(PROJECT_ROOT))
        if "decisions" not in rel.lower():
            text = read_text(path)
            if text and re.search(r"^#.*\bADR-\d+", text, re.MULTILINE):
                record("Authority Invariant", WARN,
                       f"ADR reference found outside decisions folder: `{rel}`")


def check_non_goals_invariant():
    """Non-goals must be explicit in boundaries.md (or similar)."""
    text = read_text(BOUNDARIES_FILE)
    if text is None:
        record("Explicit Non-Goals", FAIL,
               f"`{BOUNDARIES_FILE.relative_to(PROJECT_ROOT)}` is missing")
        return

    exclusion_patterns = [
        r"\bnot\b", r"\bnon-goal", r"\bout of scope\b",
        r"\bforbidden\b", r"\bwill not\b", r"\bmust not\b",
        r"\bexcluded\b", r"\bnever\b",
    ]
    found = any(re.search(p, text, re.IGNORECASE) for p in exclusion_patterns)

    if found:
        record("Explicit Non-Goals", PASS,
               "Explicit exclusion language found in boundaries.md")
    else:
        record("Explicit Non-Goals", WARN,
               "No clear exclusion language found in boundaries.md. "
               "Verify non-goals are explicitly stated.")


def check_decision_traceability():
    """Decisions folder must exist and contain at least one ADR."""
    if not DECISIONS_DIR.exists():
        record("Decision Traceability", FAIL,
               f"`{DECISIONS_DIR.relative_to(PROJECT_ROOT)}/` does not exist")
        return

    adrs = list(DECISIONS_DIR.glob("ADR-*.md"))
    if len(adrs) == 0:
        record("Decision Traceability", WARN,
               "Decisions folder exists but contains no ADR files")
    else:
        record("Decision Traceability", PASS,
               f"{len(adrs)} ADR(s) found: {', '.join(f.name for f in adrs)}")


def check_intent_vs_implementation():
    """Memory files should not contain large code blocks."""
    memory_files = collect_memory_files()
    flagged = []

    for path in memory_files:
        text = read_text(path)
        if text is None:
            continue
        blocks = count_code_blocks(text)
        large = [b for b in blocks if b > CODE_BLOCK_LINE_THRESHOLD]
        if large:
            rel = str(path.relative_to(PROJECT_ROOT))
            flagged.append(f"`{rel}` ({len(large)} block(s) >{CODE_BLOCK_LINE_THRESHOLD} lines)")

    if not flagged:
        record("Intent vs Implementation", PASS,
               "No large code blocks found in memory files")
    else:
        for f in flagged:
            record("Intent vs Implementation", WARN,
                   f"Large code block in {f}. Memory should capture intent, not code.")


def check_update_locality():
    """
    Detect potential duplicated definitions across memory files.
    Heuristic: compare heading sets between files for high overlap.
    """
    memory_files = collect_memory_files()
    file_headings: dict[str, set[str]] = {}

    for path in memory_files:
        text = read_text(path)
        if text is None:
            continue
        headings = extract_headings(text)
        # Normalize to lowercase word-sets
        words = set()
        for h in headings:
            words.update(w.lower() for w in re.findall(r"\w+", h) if len(w) > 3)
        rel = str(path.relative_to(PROJECT_ROOT))
        file_headings[rel] = words

    checked = set()
    overlaps_found = False
    for f1, w1 in file_headings.items():
        for f2, w2 in file_headings.items():
            pair = tuple(sorted([f1, f2]))
            if f1 == f2 or pair in checked:
                continue
            checked.add(pair)
            common = w1 & w2
            if len(common) >= OVERLAP_HEADING_THRESHOLD:
                # Filter out very generic terms
                generic = {"source", "model", "purpose", "current", "rules",
                           "status", "version", "phase", "system", "data",
                           "market", "explicit", "invariant", "invariants"}
                meaningful = common - generic
                if len(meaningful) >= OVERLAP_HEADING_THRESHOLD:
                    record("Update Locality", WARN,
                           f"Heading overlap between `{f1}` and `{f2}`: "
                           f"{', '.join(sorted(meaningful)[:5])}")
                    overlaps_found = True

    if not overlaps_found:
        record("Update Locality", PASS,
               "No significant heading overlaps detected across memory files")


def check_machine_parsability():
    """Check that all memory markdown files have at least one heading."""
    memory_files = [f for f in collect_memory_files() if f.suffix == ".md"]
    no_headings = []

    for path in memory_files:
        text = read_text(path)
        if text is None:
            continue
        if not extract_headings(text):
            rel = str(path.relative_to(PROJECT_ROOT))
            no_headings.append(rel)

    if not no_headings:
        record("Machine Parsability", PASS,
               "All markdown memory files contain structured headings")
    else:
        for f in no_headings:
            record("Machine Parsability", WARN,
                   f"`{f}` has no markdown headings — may be hard to parse")


def check_drift_detection():
    """Check for [TBD] markers that indicate incomplete knowledge."""
    memory_files = collect_memory_files()
    tbd_files = []

    for path in memory_files:
        text = read_text(path)
        if text is None:
            continue
        tbd_count = len(re.findall(r"\[TBD\]", text))
        if tbd_count > 0:
            rel = str(path.relative_to(PROJECT_ROOT))
            tbd_files.append((rel, tbd_count))

    if not tbd_files:
        record("Drift Detection", PASS,
               "No [TBD] markers found — all sections appear populated")
    else:
        for f, count in tbd_files:
            record("Drift Detection", WARN,
                   f"`{f}` contains {count} [TBD] marker(s) — incomplete knowledge")


def check_regeneration_safety():
    """
    Check that index.md references all memory subdirectories.
    If a directory exists but isn't in the index, it's an orphan risk.
    """
    index_text = read_text(MEMORY_DIR / "index.md")
    if index_text is None:
        record("Regeneration Safety", FAIL, "index.md is missing")
        return

    subdirs = [d.name for d in MEMORY_DIR.iterdir()
               if d.is_dir() and not d.name.startswith(".")]
    missing = [d for d in subdirs if d not in index_text]

    if not missing:
        record("Regeneration Safety", PASS,
               "All memory subdirectories are referenced in index.md")
    else:
        for d in missing:
            record("Regeneration Safety", WARN,
                   f"Directory `{d}/` exists but is not referenced in index.md")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_status_icon(status: str) -> str:
    icons = {PASS: "✅", WARN: "⚠️", FAIL: "❌"}
    return icons.get(status, "?")


def print_report():
    """Print clean summary to stdout."""
    print("=" * 60)
    print("  MEMORY QUALITY AUDIT REPORT")
    print("=" * 60)
    print()

    for r in results:
        icon = format_status_icon(r["status"])
        print(f"  {icon} [{r['status']}] {r['invariant']}")
        print(f"         {r['detail']}")
        print()

    # Summary
    counts = defaultdict(int)
    for r in results:
        counts[r["status"]] += 1
    print("-" * 60)
    print(f"  Summary: {counts[PASS]} PASS, {counts[WARN]} WARN, {counts[FAIL]} FAIL")
    print("-" * 60)


def write_markdown_report():
    """Write AUDIT_REPORT.md."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Memory Quality Audit Report",
        "",
        f"**Generated**: {timestamp}",
        f"**Script**: `scripts/memory_audit.py`",
        f"**Status**: READ-ONLY ANALYSIS — no files were modified",
        "",
        "---",
        "",
    ]

    current_invariant = None
    for r in results:
        if r["invariant"] != current_invariant:
            current_invariant = r["invariant"]
            lines.append(f"## {current_invariant}")
            lines.append("")

        icon = format_status_icon(r["status"])
        lines.append(f"- {icon} **{r['status']}**: {r['detail']}")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary table
    counts = defaultdict(int)
    for r in results:
        counts[r["status"]] += 1

    lines.append("## Summary")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("| :--- | :--- |")
    lines.append(f"| ✅ PASS | {counts[PASS]} |")
    lines.append(f"| ⚠️ WARN | {counts[WARN]} |")
    lines.append(f"| ❌ FAIL | {counts[FAIL]} |")
    lines.append("")

    report_path = MEMORY_DIR / "AUDIT_REPORT.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  Report written to: {report_path.relative_to(PROJECT_ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not MEMORY_DIR.exists():
        print(f"FATAL: Memory directory not found: {MEMORY_DIR}")
        sys.exit(1)

    # Run all checks
    all_present = check_required_files()
    if not all_present:
        print("\n  ❌ Required files missing. Remaining checks may be incomplete.\n")

    check_authority_invariant()
    check_non_goals_invariant()
    check_decision_traceability()
    check_intent_vs_implementation()
    check_update_locality()
    check_machine_parsability()
    check_drift_detection()
    check_regeneration_safety()

    # Output
    print_report()
    write_markdown_report()


if __name__ == "__main__":
    main()
