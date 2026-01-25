# Skill: Decision Ledger Curator

**Category**: Meta (Structural)  
**Stability**: Core

## 1. Purpose
The `decision-ledger-curator` is the system's "Notary Public." It manages the integrity and chronological order of [decisions.md](file:///c:/GIT/TraderFund/docs/epistemic/ledger/decisions.md). It ensures that all significant system changes have a formal rationale and human attribution.

## 2. Inputs & Preconditions
- **Required Inputs**: Decision Title, Summary, Rationale, and Impacted Documents.
- **Required Files**: `docs/epistemic/ledger/decisions.md`.
- **Preconditions**: MUST be triggered by a human decision cycle.

## 3. Outputs & Side Effects
- **Ledger Impact**: Appends an immutable, formatted block to the Decision Ledger.
- **Artifacts**: Increments global Decision ID (DXXX).

## 4. Invariants & Prohibitions
- **Format Only**: The Curator manages FORMAT only; it has zero authority to decide the CONTENT of a decision.
- **Human Origin**: All entries MUST originate from human operators.
- **No Mutation**: Cannot modify or retract historical decisions.

## 5. Invocation Format

```
Invoke decision-ledger-curator
Mode: REAL_RUN
Target: docs/epistemic/ledger/decisions.md

Options:
  title: "Authorize Task Selector Model"
  decision: "Upgrade build system to support partial execution."
  rationale: "Need granular control for Phase 2 implementation."
  impact: "task_graph.md, DWBS.md"
```

## 6. Failure Modes
- **ID Conflict**: Internal counter mismatch (Terminal).
- **Incomplete Metadata**: Missing rationale or attribution (Terminal).

## 7. Notes for Operators
- **Rule of Record**: If a decision is not in the ledger, it did not happen.
- **Traceability**: Always list the Rule IDs or Invariant IDs impacted by the decision.
