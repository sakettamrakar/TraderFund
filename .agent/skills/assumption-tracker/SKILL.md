---
name: Assumption Tracker
description: Structural skill to prevent regression by tracking invalidated assumptions.
version: 1.0.0
---

# Assumption Tracker

**Purpose**: To maintain `assumption_changes.md`. Ensures that "Learned Failures" are not repeated.

## 1. Capabilities

### 1.1. Invalidate Assumption
*   **Action**: Append entry to `docs/epistemic/ledger/assumption_changes.md`.
*   **Inputs**: Assumption ID (if any), Description, Failure Reason.

## 2. Usage

### Command Line
```powershell
python bin/run-skill.py assumption-tracker --assumption "Markets are efficient" --reason "Arbitrage exists" --user tracker
```
