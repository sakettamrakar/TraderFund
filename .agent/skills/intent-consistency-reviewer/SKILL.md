---
name: intent-consistency-reviewer
description: Advisory skill to ensure alignment with Project Intent and Trading Philosophy.
---

# Intent Consistency Reviewer Skill

**Status:** Operational  
**Skill Category:** Validation (Advisory)

## 1. Skill Purpose
The `intent-consistency-reviewer` verifies that proposed changes align with the Core Project Intent (e.g., "Glass Box") and do not introduce explicitly Forbidden patterns (e.g., "Black Box").

## 2. Invocation Contract

### Standard Grammar
```
Invoke intent-consistency-reviewer
Mode: <VERIFY | DRY_RUN>
Target: <path/to/check>
ExecutionScope:
  mode: all
Options:
  strict: <enabled | disabled>
```

## 3. Supported Modes & Selectors
- **VERIFY**: Scan target and return PASS/FAIL report.
- **DRY_RUN**: Print warnings only, do not return non-zero exit code.

## 4. Hook & Skill Chaining
- **Chained From**: Triggered by humans or build-harness for structural tasks.
- **Chained To**: Reports are used as merge blockers.

## 5. Metadata & State
- **Inputs**: Target code/docs, [project_intent.md](file:///c:/GIT/TraderFund/docs/epistemic/project_intent.md).
- **Outputs**: Advisory Report with warning details.

## 6. Invariants & Prohibitions
1.  **Advisory Only**: CANNOT block execution automatically; only flags violations for human review.
2.  **No Negotiation**: The Project Intent is immutable relative to this skill.
3.  **Pattern Matcher**: Relies on heuristic anti-pattern detection (e.g., "HFT", "Arbitrage").

## 7. Example Invocation
```
Invoke intent-consistency-reviewer
Mode: VERIFY
Target: src/new_strategy/
ExecutionScope:
  mode: all
Options:
  strict: enabled
```
