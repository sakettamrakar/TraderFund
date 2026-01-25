# Skill: Assumption Tracker

**Category**: Meta (Structural)  
**Stability**: Core

## 1. Purpose
The `assumption-tracker` is responsible for formalizing the system's "memory of failure." It maintains the [assumption_changes.md](file:///c:/GIT/TraderFund/docs/epistemic/ledger/assumption_changes.md) ledger, ensuring that once an assumption is invalidated by real-world data or logic, it is treated as a permanent constraint to prevent regression.

## 2. Inputs & Preconditions
- **Required Files**: `docs/epistemic/ledger/assumption_changes.md`
- **Required State**: Evidence of assumption failure (e.g. log trace, audit report).
- **Validators**: Must pass `drift-detector` before execution.

## 3. Outputs & Side Effects
- **Ledger Impact**: Appends a formatted entry to `assumption_changes.md`.
- **DID Impact**: Produces a Documentation Impact Declaration (DID) if the retired assumption affects active components.
- **Artifacts**: Updated ledger file.

## 4. Invariants & Prohibitions
- **Permanent Death**: NEVER allows the deletion of an assumption entry.
- **No Resurrection**: Cannot "re-validate" an assumption; this requires a separate `Decision Ledger` entry.
- **Non-Goal**: Does NOT predict future failures; only records historical ones.

## 5. Invocation Format

```
Invoke assumption-tracker
Mode: REAL_RUN
Target: docs/epistemic/ledger/assumption_changes.md

Options:
  assumption: "Markets are always efficient"
  reason: "Arbitrage detected in signal cycle S02"
  outcome: "PR-01: System must assume local inefficiency during high volatility"
```

## 6. Failure Modes
- **Access Denied**: Filesystem lock on the ledger (Retriable).
- **Duplicate ID**: Attempting to record an already retired assumption (Terminal).
- **Inconsistent State**: Ledger hash mismatch (Terminal).

## 7. Notes for Operators
- **Mandatory Alignment**: The `outcome` field should ideally map to a new Rule ID in the validator.
- **When to Use**: Use immediately following a post-mortem or after identifying a logic flaw in a strategy.
