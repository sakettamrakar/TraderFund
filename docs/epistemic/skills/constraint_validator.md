# Skill: Constraint Validator

**Category**: Validation (Semantic)  
**Stability**: Core

## 1. Purpose
The `constraint-validator` performs semantic logic verification. While other skills check structure, this skill verifies **Truth**. It ensures system artifacts (Narratives, Signals, Decisions) follow logic rules, most critically the prohibition of "Future Leaks" and "Regime Incompatibility."

## 2. Inputs & Preconditions
- **Required Inputs**: JSON/Markdown artifacts, active regime context.
- **Required Policies**: `Regime_Taxonomy.md`, `layer_interaction_contract.md`.

## 3. Outputs & Side Effects
- **Outputs**: PASS/FAIL status with detailed violation reasons.
- **Ledger Impact**: Failure is logged as a `HARNESS_VIOLATION` in REAL_RUN.
- **Side Effects**: NONE (Read-Only).

## 4. Invariants & Prohibitions
- **Binary Judgment**: Returns ONLY PASS or FAIL; NO "Partial Credit" for nearly-correct truth.
- **No Revision**: Is forbidden from "fixing" timestamps or regime labels; artifacts must be corrected at the source.
- **Independence**: Logic checks must not depend on market data, only on semantic labels and timestamps.

## 5. Invocation Format

```
Invoke constraint-validator
Mode: VERIFY
Target: data/narratives/2026-01-24__narrative.json

ExecutionScope:
  mode: narrative

Options:
  strict: enabled
```

## 6. Failure Modes
- **Semantic Conflict**: e.g. Signal dated T+1 in context T0 (Terminal).
- **Incompatible State**: e.g. Momentum signal in CHOPPING regime (Terminal).

## 7. Notes for Operators
- **Mandatory Filter**: This skill is always invoked by the Build Harness before any and all structural changes.
- **Operator Attribution**: Failures should be escalated to the operator's decision engine for re-analysis.
