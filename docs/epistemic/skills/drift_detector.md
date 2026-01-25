# Skill: Drift Detector

**Category**: Validation (Structural)  
**Stability**: Core

## 1. Purpose
The `drift-detector` is the system's "Senses." It ensures that the system's actual state (files, config, structure) matches its intended state as defined by baselines and epistemic contracts. It answers: 
1. "Has something changed since last approval?" (Syntactic)
2. "is the system violating an invariant?" (Semantic drift)

## 2. Inputs & Preconditions
- **Required Inputs**: Active `.env` or `config.py`, Project directory structure.
- **Required Context**: `Architecture_Overview.md`, `skills_catalog.md`, and 13 Epistemic Rules.

## 3. Outputs & Side Effects
- **Outputs**: Detailed Drift Report (JSON) with severity levels (INFO, WARNING, FAIL, CRITICAL).
- **Ledger Impact**: NONE (Read-Only).

## 4. Invariants & Prohibitions
- **Read-Only**: NEVER modifies or "fixes" files; it only reports discrepancies.
- **Determinism**: Identical system states MUST produce identical reports.
- **Constitutional**: Treats epistemic documents as absolute Law.

## 5. Invocation Format

```
Invoke drift-detector
Mode: VERIFY
Target: c:\GIT\TraderFund\

ExecutionScope:
  mode: all

Options:
  validators: enabled
  config: check
  structure: check
```

## 6. Failure Modes
- **Missing Baseline**: Authoritative manifest not found (Terminal).
- **Observability Gap**: Permissions deny read access to project root (Terminal).

## 7. Notes for Operators
- **Maintenance**: Update the structural baseline after every intentional architectural decision.
- **Gating**: Any `CRITICAL` drift detection is a hard stop for all autonomous execution.
