---
name: Monitor Trigger (Passive)
description: Passive monitor to detect actionable system states and suggest interventions.
version: 1.0.0
---

# Monitor Trigger (Passive)

**Purpose**: To continuously observe the system state (Inbox, Artifacts, Logs) and identify when human intervention is required.

**Constraint**: This skill is **PASSIVE ONLY**. It must never execute the actions it suggests.

## 1. Capabilities

### 1.1. Inbox Watcher
*   **Target**: `data/events/inbox`
*   **Condition**: Files exist.
*   **Output**: Suggest `bin/run_narrative.py`.

### 1.2. Decision Gap Detector
*   **Target**: `data/narratives` vs `data/decisions`.
*   **Condition**: Narrative exists without a corresponding Decision.
*   **Output**: Suggest `bin/run_decision.py`.

## 2. Usage

### Command Line
```powershell
python bin/run-skill.py monitor-trigger --user monitor_agent
```

## 3. Operational Rules
1.  **Log Only**: Outputs must be logged as `[SUGGESTION] ...`.
2.  **No Side Effects**: Do not move, delete, or modify scanned files.
3.  **Idempotency**: Runs must be stateless.
