# Skill: Cognitive Order Validator

**Category**: Validation (Structural)  
**Stability**: Core

## 1. Purpose
The `cognitive-order-validator` enforces the strict separation of concerns defined in the `architectural_invariants.md`. It ensures that "Thinking" layers (Signals, Narratives) do not perform "Acting" (Execution) or import execution dependencies, preventing signal/execution leakage.

## 2. Inputs & Preconditions
- **Required Files**: Source code files (`src/*.py`), `docs/epistemic/architectural_invariants.md`.
- **Preconditions**: Syntax must be valid (Python AST parsing).

## 3. Outputs & Side Effects
- **Outputs**: Detailed violation report (Illegal imports, Leakage keywords).
- **Ledger Impact**: Results are committed to the execution audit by the harness.
- **Side Effects**: NONE (Read-Only).

## 4. Invariants & Prohibitions
- **Thinking != Acting**: Cognitive files MUST NOT contain side-effect keywords (e.g. `buy`, `place_order`).
- **Unidirectional Flow**: Upper layers (Execution) cannot be imported by lower layers (Cognition).
- **No Optimization**: Does not suggest fixes; only reports violations.

## 5. Invocation Format

```
Invoke cognitive-order-validator
Mode: VERIFY
Target: src/narratives/

Options:
  enforce: errors
```

## 6. Failure Modes
- **Parser Error**: Unable to parse AST of target file (Terminal).
- **Config Missing**: Invariants document not found (Terminal).

## 7. Notes for Operators
- **Gating**: This skill is a mandatory blocker for any task in the **Control Plane** and **Strategy Plane**.
- **Safe Usage**: Always run in `VERIFY` mode before committing new code.
