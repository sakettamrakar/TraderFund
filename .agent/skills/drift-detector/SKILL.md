---
name: drift-detector
description: A skill to detect and report structural, configuration, logic, and epistemic discrepancies against defining baselines.
---

# Drift Detector Skill

**Status:** Operational  
**Skill Category:** Validation (Structural)

## 1. Skill Purpose
The `drift-detector` ensures the system's actual state matches its intended state as defined by baselines and epistemic contracts. It answers: 
1. "Has the system structure or config changed since last approval?" (Syntactic)
2. "Is the system violating its own epistemic laws?" (Semantic)

## 2. Invocation Contract

### Standard Grammar
```
Invoke drift-detector
Mode: <DRY_RUN | REAL_RUN | VERIFY>
Target: <path/to/check>
ExecutionScope:
  mode: <all | selectors>
  [rule_id: <OD-1 | CD-1 | ...>]
Options:
  validators: <enabled | disabled>
  config: <check | ignore>
  structure: <check | ignore>
```

## 3. Supported Modes & Selectors

### A. Execution Modes
- **DRY_RUN**: Identical to VERIFY, but does not trigger any potential side-effect hooks (though drift-detector is primarily read-only).
- **REAL_RUN**: Execute full scan and generate a persistent [Drift Report].
- **VERIFY**: Perform a read-only comparison against baselines and return a status code (PASS/FAIL).

### B. Selectors
- `all`: Run all 13 epistemic rules and all structural/config checks.
- `rule_id`: Target a specific epistemic rule (e.g., `PD-1` for permission bypass).

## 4. Hook & Skill Chaining
- **Chained From**: Invoked as a **Pre-Execution Gate** by `design-build-harness`.
- **Chained To**: If `CRITICAL` drift is detected, may inform `monitor-trigger`.

## 5. Metadata & State
- **Inputs**: Epistemic documents, `.env`, project root structure, source code.
- **Outputs**: JSON Drift Report, violation count.

## 6. Invariants & Prohibitions
1.  **Read-Only**: NEVER modifies files; only reports drift.
2.  **No Interpretation**: Judges against baselines, not "intent" or "quality."
3.  **Deterministic**: Two runs on the same state MUST produce the same report.

## 7. Example Invocation
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

---

## 8. Epistemic Validation Rules
| Category | Rules | What They Detect |
|:---------|:------|:-----------------|
| Drift Taxonomy | OD-1 to LD-1 | Ontological, causal, boundary, permission, temporal, latent→active drift |
| Macro/Factor | MF-1 to MF-4 | Macro dependency, factor policy, execution inference |
| Harness Safety | EH-1 to EH-3 | Belief inference, factor bypass, implicit strategy |
