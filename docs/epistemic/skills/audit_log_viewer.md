# Skill: Audit Log Viewer

**Category**: Analysis (Informational)  
**Stability**: Core

## 1. Purpose
The `audit-log-viewer` provides a human-readable, filterable view of machine-parseable JSON audit logs. It is the primary tool for "Glass Box" verification, allowing architects to trace the provenance of any system action.

## 2. Inputs & Preconditions
- **Required Files**: `logs/*.json`
- **Preconditions**: Logs must be in standardized JSON format.
- **Preconditions**: Read-only access to the logs directory.

## 3. Outputs & Side Effects
- **Outputs**: Structured terminal display or Markdown summary.
- **Ledger Impact**: NONE.
- **Side Effects**: NONE (Read-Only).

## 4. Invariants & Prohibitions
- **Transparency**: MUST NOT hide log entries that match the provided filters.
- **No Mutation**: Is forbidden from deleting or modifying log files.
- **Graceful Failure**: Must handle malformed lines without crashing.

## 5. Invocation Format

```
Invoke audit-log-viewer
Mode: VERIFY
Target: logs/audit.json

ExecutionScope:
  mode: selectors
  user: "agent_42"
  last: 50

Options:
  format: table
```

## 6. Failure Modes
- **Malformed JSON**: Encountered invalid log entry (Retriable/Non-Fatal).
- **Path Not Found**: Logs directory is missing or empty (Terminal).

## 7. Notes for Operators
- **Safe Usage**: This skill is safe to run in any system state.
- **Performance**: High-volume log directories should be filtered by `day` or `last` to avoid memory overflow.
