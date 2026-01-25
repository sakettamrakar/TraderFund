# Skill: Intent Consistency Reviewer

**Category**: Validation (Advisory)  
**Stability**: Auxiliary

## 1. Purpose
The `intent-consistency-reviewer` ensures that the system's development aligns with its Core Philosophy (e.g. "Glass Box", "Context Before Signal"). It flags development patterns that contradict the Project Intent or introduce forbidden concepts (e.g. "Black Boxes").

## 2. Inputs & Preconditions
- **Required Inputs**: File or directory to check.
- **Required Policies**: [project_intent.md](file:///c:/GIT/TraderFund/docs/epistemic/project_intent.md).

## 3. Outputs & Side Effects
- **Outputs**: Advisory Report with warning details and suggested alignment corrections.
- **Ledger Impact**: NONE (Advisory only).

## 4. Invariants & Prohibitions
- **Non-Blocking**: Cannot block execution automatically; only flags warnings for human review.
- **No Interpretation**: Relies on heuristic anti-pattern detection; does not guess at "unspoken" intent.

## 5. Invocation Format

```
Invoke intent-consistency-reviewer
Mode: VERIFY
Target: src/new_strategy/

Options:
  strict: enabled
```

## 6. Failure Modes
- **Policy Missing**: unable to find project intent baseline (Terminal).

## 7. Notes for Operators
- **Review Requirement**: Any warning from this skill during a PR must be addressed by an architect.
- **Heuristics**: Scans for keywords like "Neural Network," "Stochastic," or "Auto-generated" in forbidden contexts.
