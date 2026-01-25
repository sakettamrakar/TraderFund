---
name: audit-log-viewer
description: Read-only tool to inspect system logs and operator actions.
---

# Audit Log Viewer Skill

**Status:** Operational  
**Skill Category:** Analysis (Informational)

## 1. Skill Purpose
The `audit-log-viewer` provides a human-readable, filterable view of the machine-parseable JSON audit logs. It enables "Glass Box" verification of system history and the provenance of actions.

## 2. Invocation Contract

### Standard Grammar
```
Invoke audit-log-viewer
Mode: <REAL_RUN | VERIFY>
Target: logs/*.json
ExecutionScope:
  mode: <all | selectors>
  [user: <string>]
  [logger: <string>]
  [last: <n>]
  [day: <date>]
Options:
  format: <text | json | table>
```

## 3. Supported Modes & Selectors
- **REAL_RUN / VERIFY**: Parse and display logs based on the provided filters. In this skill, these modes are technically identical as the skill is read-only.
- **Selectors**:
    - `user`: Filter by a specific operator.
    - `logger`: Filter by component (e.g., `RunNarrativeCLI`).
    - `last`: Show the most recent N lines.
    - `day`: Filter logs for a specific calendar date.

## 4. Hook & Skill Chaining
Not Applicable (Passive viewer).

## 5. Metadata & State
- **Inputs**: JSON logs from `logs/`.
- **Outputs**: Structured stdout display.

## 6. Invariants & Prohibitions
1.  **Read-Only**: NEVER modifies or deletes log files.
2.  **Transparency**: Must not hide log entries that match the filter.
3.  **Integrity**: Must report malformed JSON rather than silently skipping it.

## 7. Example Invocation
```
Invoke audit-log-viewer
Mode: REAL_RUN
Target: logs/audit.json
ExecutionScope:
  mode: selectors
  user: "agent_42"
  last: 20
Options:
  format: table
```
