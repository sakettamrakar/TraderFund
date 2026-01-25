# Skill: Monitor Trigger

**Category**: Analysis (Advisory)  
**Stability**: Experimental

## 1. Purpose
The `monitor-trigger` is a passive observer skill. It scans the system's "Inbox" and "Decision State" to identify gaps where human intervention or system tasks are required (e.g. an arrival of a raw event without a following narrative).

## 2. Inputs & Preconditions
- **Required Inputs**: Data directory paths.
- **Preconditions**: Requires read-access to `data/events` and `data/narratives`.

## 3. Outputs & Side Effects
- **Outputs**: A prioritized list of `[SUGGESTION]` entries logged to stdout.
- **Ledger Impact**: NONE (Passive).

## 4. Invariants & Prohibitions
- **Passive Only**: MUST NEVER execute the actions it suggests.
- **Non-Intervention**: Is forbidden from moving or archiving files on its own.

## 5. Invocation Format

```
Invoke monitor-trigger
Mode: REAL_RUN
Target: data/

Options:
  log-suggestions: enabled
```

## 6. Failure Modes
- **Observability Hole**: Access to key data directories is blocked (Terminal).

## 7. Notes for Operators
- **Usage**: Typically run as a cron job or background process to alert humans to pending work.
- **Scope**: Currently covers "Inbox Check" and "Decision Gap Detection."
