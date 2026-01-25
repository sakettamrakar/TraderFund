# Skill Invocation Grammar

**Status**: Constitutional — Binding  
**Scope**: All Skills

This document defines the canonical grammar for invoking any skill within the Trader Fund ecosystem. All humans and agents MUST follow this format to ensure deterministic behavior and auditability.

## 1. Canonical Format

```
Invoke <SkillName>
Mode: <MODE>
Target: <TARGET>

ExecutionScope:
  mode: <all | range | list | first_n | last_n>
  [from_task: <task_id>]
  [to_task: <task_id>]
  [tasks: [<task_id>, ...]]
  [count: <n>]

Options:
  <key>: <value>
  <key>: <value>
```

## 2. Field Definitions

| Field | Requirement | Values | Description |
|:------|:------------|:-------|:------------|
| **Invoke** | Mandatory | Canonical Name | The unique name of the skill (e.g. `drift-detector`). |
| **Mode** | Mandatory | `REAL_RUN`, `DRY_RUN`, `VERIFY` | The intent of the execution (Mutation, Simulation, or Validation). |
| **Target** | Mandatory | Path or Ref | The file, directory, or state object the skill operates on. |
| **ExecutionScope** | Optional | Map | Parameters to restrict the scope of operation (standardized across the harness). |
| **Options** | Optional | Key-Value Pairs | Custom configuration specific to the skill. |

## 3. Mode Semantics

### REAL_RUN
- **Action**: Performs intended state changes (e.g. appending to the ledger, creating files).
- **Enforcement**: Mandatory Validator checks.
- **Audit**: Commitment to the Evolution Log.

### DRY_RUN
- **Action**: Simulates the execution and prints the projected outcome.
- **Side Effects**: NONE. No files modified, no ledger commits.
- **Usage**: Mandatory before significant structural `REAL_RUN`s.

### VERIFY
- **Action**: Compares current state against expected patterns or baselines.
- **Action**: Returns PASS/FAIL status.
- **Usage**: Used by guardrail skills (e.g. `constraint-validator`).

## 4. Examples

### Orchestration Example
```
Invoke design-build-harness
Mode: REAL_RUN
Target: docs/epistemic/roadmap/task_graph.md
ExecutionScope:
  mode: range
  from_task: CP-1.1
  to_task: CP-1.3
Options:
  validators: enabled
```

### Analysis Example
```
Invoke pattern-matcher
Mode: VERIFY
Target: SPY
ExecutionScope:
  mode: price
Options:
  threshold: 0.8
```
