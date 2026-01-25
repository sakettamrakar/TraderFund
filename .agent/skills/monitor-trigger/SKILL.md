---
name: monitor-trigger
description: Passive monitor to detect actionable system states and suggest interventions.
---

# Monitor Trigger Skill (Passive)

**Status:** Operational  
**Skill Category:** Analysis (Advisory)

## 1. Skill Purpose
The `monitor-trigger` continuously observes the system state (Inbox, Artifacts, Logs) to identify when human intervention or specific system tasks are required. It is strictly passive and never acts on its own suggestions.

## 2. Invocation Contract

### Standard Grammar
```
Invoke monitor-trigger
Mode: <VERIFY | REAL_RUN>
Target: <data_dir_path>
ExecutionScope:
  mode: all
Options:
  log-suggestions: <enabled | disabled>
```

## 3. Supported Modes & Selectors
- **VERIFY**: Scan directories for actionable states (e.g., raw files in inbox) and return a list of suggestions.
- **REAL_RUN**: Identical to VERIFY, but explicitly logs `[SUGGESTION]` entries to the system log.

## 4. Hook & Skill Chaining
Passive only. Does not chain or trigger other skills.

## 5. Metadata & State
- **Inputs**: `data/events/inbox`, `data/narratives`.
- **Outputs**: List of suggested command-line actions.

## 6. Invariants & Prohibitions
1.  **Passive Only**: Must NEVER execute the actions it suggests.
2.  **Log Only**: Outputs must be informational suggestions.
3.  **State-Driven**: Suggestions are based strictly on current file presence or gap detection.

## 7. Example Invocation
```
Invoke monitor-trigger
Mode: REAL_RUN
Target: data/
ExecutionScope:
  mode: all
Options:
  log-suggestions: enabled
```
