---
name: constraint-validator
description: A skill to verify that the system is adhering to its own epistemic and operational rules.
---

# Constraint Validator Skill

**Status:** Operational  
**Skill Category:** Validation (Semantic)

## 1. Skill Purpose
The `constraint-validator` performs semantic logic verification on system artifacts (Narratives, Signals, Decisions). It ensures that the *truth* contained in these artifacts following the system's own logical constraints (e.g., No Future Leaks).

## 2. Invocation Contract

### Standard Grammar
```
Invoke constraint-validator
Mode: <VERIFY>
Target: <path/to/artifact | artifact_json>
ExecutionScope:
  mode: <narrative | signal | decision>
Options:
  strict: <enabled | disabled>
```

## 3. Supported Modes & Selectors
- **VERIFY**: This is the only supported mode. It provides a binary PASS/FAIL judgment on the target object.
- **Selectors (Scopes)**: 
    - `narrative`: Checks for regime alignment, genesis fields, and temporal integrity.
    - `signal`: Verifies signal-to-regime compatibility.
    - `decision`: Traces decisions back to roots and verifies "Why"/ "Stop" fields.

## 4. Hook & Skill Chaining
- **Chained From**: Triggered by `design-build-harness` after artifact-producing tasks.
- **Chained To**: Fed into the `audit-log-viewer`.

## 5. Metadata & State
- **Inputs**: JSON/Markdown artifacts, active regime/factor state.
- **Outputs**: Binary status, violation report.

## 6. Invariants & Prohibitions
1.  **Read-Only**: NEVER alters the target data.
2.  **No Partial Credit**: Verification is strictly binary; a single violation fails the object.
3.  **Temporal Consistency**: Future timestamps or "lookahead" data in past artifacts are terminal failures.

## 7. Example Invocation
```
Invoke constraint-validator
Mode: VERIFY
Target: data/narratives/2026-01-24__narrative.json
ExecutionScope:
  mode: narrative
Options:
  strict: enabled
```
