---
name: cognitive-order-validator
description: Structural skill to enforce the cognitive hierarchy (Architecture > Logic > Execution).
---

# Cognitive Order Validator Skill

**Status:** Operational  
**Skill Category:** Validation (Structural)

## 1. Skill Purpose
The `cognitive-order-validator` enforces the strict separation of concerns defined in the `architectural_invariants.md`. It ensures that "Thinking" layers (Signals, Narratives) do not perform "Acting" (Execution, Adapters) or import their dependencies.

## 2. Invocation Contract

### Standard Grammar
```
Invoke cognitive-order-validator
Mode: <VERIFY | DRY_RUN>
Target: <path/to/src_dir>
ExecutionScope:
  mode: all
Options:
  enforce: <warnings | errors>
```

## 3. Supported Modes & Selectors
- **VERIFY**: Scan target files and return PASS/FAIL based on layer interaction rules.
- **DRY_RUN**: Perform the scan but return success even if violations are found (used for auditing legacy code).

## 4. Hook & Skill Chaining
- **Chained From**: Invoked as a **Post-Execution Hook** for implementation tasks.
- **Chained To**: Reports are consumed by the `drift-detector`.

## 5. Metadata & State
- **Inputs**: Source code, `architectural_invariants.md`.
- **Outputs**: Error report detailing illegal imports or keyword leaks.

## 6. Invariants & Prohibitions
1.  **Thinking != Acting**: Pure logic files must not contain execution side-effects.
2.  **Unidirectional Flow**: Upper layers cannot be imported by lower layers.
3.  **Market Logic Isolation**: Trading primitives are forbidden in the Regime/Narrative layers.

## 7. Example Invocation
```
Invoke cognitive-order-validator
Mode: VERIFY
Target: src/narratives/
ExecutionScope:
  mode: all
Options:
  enforce: errors
```
