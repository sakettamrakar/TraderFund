# Skill: Evolution Recorder

**Category**: Meta (Structural)  
**Stability**: Core

## 1. Purpose
The `evolution-recorder` maintains the [evolution_log.md](file:///c:/GIT/TraderFund/docs/epistemic/ledger/evolution_log.md). Unlike the Decision Ledger (which records *Intent*), the Evolution Recorder documented *Growth*—providing a narrative history of system changes, artifact production, and milestone completions.

## 2. Inputs & Preconditions
- **Required Inputs**: Summary of activity, scope of change (Code/Data/Ops/Cognition).
- **Required Files**: `docs/epistemic/ledger/evolution_log.md`.

## 3. Outputs & Side Effects
- **Ledger Impact**: Appends formatted, timestamped entries to the Evolution Log.
- **Side Effects**: NONE (Append-Only).

## 4. Invariants & Prohibitions
- **Informational Only**: Logs are descriptive, NOT prescriptive; they do not grant authority.
- **Subservience**: Log entries CANNOT override higher-order epistemic documents (Decisions).
- **Transparency**: Changes must be described accurately without omitting negative outcomes.

## 5. Invocation Format

```
Invoke evolution-recorder
Mode: REAL_RUN
Target: docs/epistemic/ledger/evolution_log.md

Options:
  scope: Code
  summary: "Standardized all 13 skill documentation files in epistemic/skills/."
```

## 6. Failure Modes
- **Log Corruption**: Unexpected formatting in target log (Terminal).
- **Write Error**: Filesystem permission issue (Terminal).

## 7. Notes for Operators
- **Mandatory Usage**: This skill is typically invoked as a `Post Hook` by the build harness on every task success.
- **Tone**: Keep summaries concise and focused on "What changed" and "Why it matters."
