---
name: assumption-tracker
description: Structural skill to prevent regression by tracking invalidated assumptions.
---

# Assumption Tracker Skill

**Status:** Operational  
**Skill Category:** Meta (Structural)

## 1. Skill Purpose
The `assumption-tracker` is responsible for maintaining the [assumption_changes.md](file:///c:/GIT/TraderFund/docs/epistemic/ledger/assumption_changes.md) ledger. It ensures that "Learned Failures" are formally recorded and treated as permanent constraints, preventing the system from repeating past mistakes.

## 2. Invocation Contract

### Standard Grammar
```
Invoke assumption-tracker
Mode: <REAL_RUN | DRY_RUN>
Target: docs/epistemic/ledger/assumption_changes.md
ExecutionScope:
  mode: all
Options:
  assumption: "<string>"
  reason: "<string>"
  outcome: "<permanent_constraint_description>"
```

## 3. Supported Modes & Selectors
- **DRY_RUN**: Validate the assumption structure and check for duplicates without appending to the ledger.
- **REAL_RUN**: Append a new invalidated assumption to the ledger.

## 4. Hook & Skill Chaining
- **Chained From**: Often invoked as a `Post Hook` by repair or failure-analysis tasks.
- **Chained To**: May trigger `drift-detector` to verify new constraints.

## 5. Metadata & State
- **Inputs**: Current assumption ledger, new failure evidence.
- **Outputs**: Append-only entry in `assumption_changes.md`.

## 6. Invariants & Prohibitions
1.  **Permanent Death**: Retired assumptions are permanently invalid.
2.  **No Resurrection**: Reintroducing a retired assumption requires a new Decision Ledger entry.
3.  **Silence Forbidden**: Silent resurrection of failed assumptions is explicitly forbidden.

## 7. Example Invocation
```
Invoke assumption-tracker
Mode: REAL_RUN
Target: docs/epistemic/ledger/assumption_changes.md
ExecutionScope:
  mode: all
Options:
  assumption: "Markets are always efficient"
  reason: "Arbitrage detected in signal cycle S02"
  outcome: "PR-01: System must assume local inefficiency during high volatility"
```
