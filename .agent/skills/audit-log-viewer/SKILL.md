---
name: Audit Log Viewer
description: Read-only tool to inspect system logs and operator actions.
version: 1.0.0
---

# Audit Log Viewer

**Purpose**: To provide a human-readable view of the machine-parseable JSON audit logs. This skill enables "Glass Box" verification of system history.

## 1. Capabilities

### 1.1. Log Inspection
*   **Target**: `logs/*.json`
*   **Action**: Read, Parse, Filter, Display.
*   **Constraint**: Read-Only.

### 1.2. Filtering
*   **By User**: Filter actions by a specific operator (e.g., `--user alice`).
*   **By Time**: Show only recent logs (e.g., `--last 50` or `--day 2026-01-24`).
*   **By Logger**: Filter by component (e.g., `RunNarrativeCLI`).

## 2. Usage

### Command Line
```powershell
python bin/run-skill.py audit-log-viewer --last 20
python bin/run-skill.py audit-log-viewer --user test_user
python bin/run-skill.py audit-log-viewer --day 2026-01-24
```

## 3. Operational Rules
1.  **Transparency**: This skill must not hide any log entries that match the filter.
2.  **Integrity**: This skill must not modify the log files.
3.  **Availability**: This skill must handle malformed JSON lines gracefully (e.g., by printing raw text).
