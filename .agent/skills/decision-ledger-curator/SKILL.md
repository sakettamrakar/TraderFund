---
name: decision-ledger-curator
description: Structural skill to maintain the integrity and chronological order of the Decision Ledger.
---

# Decision Ledger Curator Skill

**Status:** Operational  
**Skill Category:** Meta (Structural)

## 1. Skill Purpose
The `decision-ledger-curator` enforces the Append-Only nature of the [decisions.md](file:///c:/GIT/TraderFund/docs/epistemic/ledger/decisions.md) and ensures a standardized schema. It prevents "Cowboy Decisions" by requiring explicit rationale, impact, and human attribution.

## 2. Invocation Contract

### Standard Grammar
```
Invoke decision-ledger-curator
Mode: <REAL_RUN | DRY_RUN>
Target: docs/epistemic/ledger/decisions.md
ExecutionScope:
  mode: all
Options:
  title: "<string>"
  decision: "<string>"
  rationale: "<string>"
  impact: "<list_of_docs>"
```

## 3. Supported Modes & Selectors
- **REAL_RUN**: Generates next ID, formats the entry, and appends to the Ledger.
- **DRY_RUN**: Simulates the entry generation and prints the markdown block for review.

## 4. Hook & Skill Chaining
- **Chained From**: Invoked after human agreement (Decision Engine) to persist the outcome.
- **Chained To**: Often followed by `evolution-recorder` to log the event.

## 5. Metadata & State
- **Inputs**: Current Decision Ledger, human input.
- **Outputs**: Append-only entry in `decisions.md`.

## 6. Invariants & Prohibitions
1.  **Format Only**: The Curator manages format and integrity ONLY; it has zero authority to decide content.
2.  **Human Origin**: All decisions MUST originate from humans.
3.  **No Override**: Cannot edit or delete existing decisions.

## 7. Example Invocation
```
Invoke decision-ledger-curator
Mode: REAL_RUN
Target: docs/epistemic/ledger/decisions.md
ExecutionScope:
  mode: all
Options:
  title: "Authorize Task Selector Model"
  decision: "Upgrade build system to support partial execution."
  rationale: "Need granular control for Phase 2 implementation."
  impact: "task_graph.md, DWBS.md"
```
