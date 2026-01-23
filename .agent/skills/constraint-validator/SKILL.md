---
name: constraint-validator
description: A skill to verify that the system is adhering to its own epistemic and operational rules.
---

# Constraint Validator Skill

**Status**: Defined (Phase 2 Unfreeze)
**Authority**: Epistemic Enforcer (Read-Only)

## 1. Purpose
The Constraint Validator is responsible for semantic logic verification. While the Drift Detector checks *files*, the Constraint Validator checks *truth*. It answers the question: "Are we following our own rules?"

## 2. Core Capabilities

### A. Narrative Integrity Check
*   **Input**: JSON/Markdown of a Narrative.
*   **Action**: Verify it contains required fields (Genesis, Regime, Invalidation Criteria).
*   **Check**: Ensure no "Future Leaks" (e.g., narrative created at T0 references T+1 data).
*   **Output**: Pass/Fail with reason.

### B. Signal-to-Regime Check
*   **Input**: Active signals + Active Regime.
*   **Action**: Verify that the signals are valid *for* that regime.
*   **Output**: Pass/Fail (e.g., "Momentum signal invalid in Mean Reversion regime").

### C. Decision Logic Audit
*   **Input**: Decision Artifact.
*   **Action**: Trace the decision back to its root narrative.
*   **Check**: Is the "Why" explicitly stated? Is the "Stop" defined?
*   **Output**: Pass/Fail.

## 3. Operational Constraints

1.  **Read-Only**: This skill **NEVER** alters decisions or data.
2.  **Binary Judgment**: It returns PASS or FAIL. It does not offer "Partial Credit."
3.  **No Override**: A Validation Failure is a hard stop for the pipeline (if enforced).

## 4. Input Schema

```json
{
  "mode": "narrative | signal | decision",
  "target_object": { ... },
  "context": { ... }
}
```

## 5. Output Schema

```json
{
  "status": "PASS | FAIL",
  "violations": [
    "Narrative missing 'Invalidation Criteria'",
    "Decision references future timestamp"
  ],
  "validator_version": "1.0"
}
```

## 6. Failure Behavior
*   If validation fails: **FAIL**.
*   If validation logic errors: **FAIL** (Fail safe).

## 7. Relationship to Epistemic Framework
*   **Validation = Integrity**.
*   This skill operationalizes the "Invariants" defined in the epistemic ledgers.
*   It is the automated conscience of the system.
