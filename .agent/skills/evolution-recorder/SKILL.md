---
name: Evolution Recorder
description: Structural skill to capture the 'What' and 'Why' of system lifecycle changes.
version: 1.0.0
---

# Evolution Recorder

**Purpose**: To maintain the `evolution_log.md` ledger. This provides a narrative history of the system's growth.

## 1. Capabilities

### 1.1. Record Evolution
*   **Action**: Append entry to `docs/epistemic/ledger/evolution_log.md`.
*   **Inputs**: Scope (Code/Data/Ops), Summary.
*   **Logic**:
    1. Append Date + Scope + Summary.

## 2. Usage

### Command Line
```powershell
python bin/run-skill.py evolution-recorder --scope "Code" --summary "Added 5 new skills" --user recorder_bot
```
