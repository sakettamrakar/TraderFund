---
name: evolution-recorder
description: Structural skill to capture the 'What' and 'Why' of system lifecycle changes.
---

# Evolution Recorder Skill

**Status:** Operational  
**Skill Category:** Meta (Structural)

## 1. Skill Purpose
The `evolution-recorder` maintains the [evolution_log.md](file:///c:/GIT/TraderFund/docs/epistemic/ledger/evolution_log.md) to provide a narrative history of the system's growth. It records architectural milestones and significant lifecycle events.

## 2. Invocation Contract

### Standard Grammar
```
Invoke evolution-recorder
Mode: <REAL_RUN | DRY_RUN>
Target: docs/epistemic/ledger/evolution_log.md
ExecutionScope:
  mode: all
Options:
  scope: <Code | Data | Ops | Cognition>
  summary: "<string>"
```

## 3. Supported Modes & Selectors
- **REAL_RUN**: Appends the formatted entry to the Evolution Log with a timestamp.
- **DRY_RUN**: Prints the formatted entry to stdout.

## 4. Hook & Skill Chaining
- **Chained From**: Invoked as a **Post-Execution Hook** by `design-build-harness`.
- **Chained To**: None.

## 5. Metadata & State
- **Inputs**: Summary of activity, scope of change.
- **Outputs**: Append-only entry in `evolution_log.md`.

## 6. Invariants & Prohibitions
1.  **Descriptive Only**: Logs are descriptive records, not prescriptive decisions.
2.  **No Privilege**: Logs cannot be used to justify or trigger system state changes.
3.  **Subservience**: Logs do not supersede Decisions or Invariants.

## 7. Example Invocation
```
Invoke evolution-recorder
Mode: REAL_RUN
Target: docs/epistemic/ledger/evolution_log.md
ExecutionScope:
  mode: all
Options:
  scope: Code
  summary: "Refactored execution harness to support post-execution hooks."
```
