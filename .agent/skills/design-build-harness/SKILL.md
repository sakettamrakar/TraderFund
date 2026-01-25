---
name: design-build-harness
description: A meta-engineering skill responsible for deterministically executing the Design/Build Task Graph while obeying epistemic, policy, and validator constraints.
---

# Design/Build Execution Harness Skill

**Status:** Constitutional — Execution-Ready  
**Skill Category:** Orchestration (Structural)

## 1. Skill Purpose
The `design-build-harness` is the authoritative orchestrator for the system's structural evolution. It transforms the [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) into coordinated, validated, and recorded actions, ensuring strict adherence to the [DWBS.md](file:///c:/GIT/TraderFund/docs/architecture/DWBS.md).

## 2. Invocation Contract

### Standard Grammar
```
Invoke design-build-harness
Mode: <DRY_RUN | REAL_RUN | VERIFY>
Target: docs/epistemic/roadmap/task_graph.md
ExecutionScope:
  mode: <all | range | list | first_n | last_n>
  [from_task: <task_id>]
  [to_task: <task_id>]
  [tasks: [<task_id>, ...]]
  [count: <n>]
Options:
  validators: <enabled | disabled>
  ledger: <read-only | append>
  hooks: <enabled | disabled>
```

## 3. Supported Modes & Selectors

### A. Execution Modes
- **DRY_RUN**: Resolve dependencies, validate selectors, and print the execution plan without modifying files or the ledger.
- **REAL_RUN**: Execute tasks, invoke post-hooks, and record outcomes in the ledger. Mandatory pre-execution validator check.
- **VERIFY**: Check existing artifacts and ledger entries against the task graph to ensure system consistency.

### B. Execution Selectors
- `all`: Execute all tasks marked as `ACTIVE`.
- `range`: Execute tasks from `from_task` to `to_task` (inclusive) in the resolved DAG path.
- `list`: Execute specific `task_id`s, verifying that dependencies are already met.
- `first_n` / `last_n`: Execute the first or last N eligible tasks in topological order.

## 4. Hook & Skill Chaining
The harness supports declarative **Post-Execution Hooks**.  
- **Mechanism**: After a task succeeds, the harness automatically invokes skills listed in the task's `Post Hooks` field.
- **Constraints**: Hooks must be recorded in the `evolution_log.md`. Failure of a hook halts the execution cycle.

## 5. Metadata & State
- **Inputs**: `task_graph.md`, `DWBS.md`, current system state.
- **Outputs**: Ledger entries, updated `task_graph.md` statuses, artifact creation.

## 6. Invariants & Prohibitions
1.  **Meta-Only**: NEVER performs trading, signal generation, or belief inference.
2.  **Deterministic**: The same input state and selector MUST produce the same execution sequence.
3.  **No Gaps**: Cannot execute a task if a `Blocking=TRUE` predecessor has not succeeded.
4.  **Validator-First**: `REAL_RUN` is forbidden if the `drift-detector` fails.

## 7. Example Invocation

```
Invoke design-build-harness
Mode: REAL_RUN
Target: docs/epistemic/roadmap/task_graph.md
ExecutionScope:
  mode: range
  from_task: CP-1.1
  to_task: CP-1.2
Options:
  validators: enabled
  ledger: append
  hooks: enabled
```

---

## 8. Failure & Safety Semantics
- **Harness Halt**: The harness stops immediately on any validator FAIL or task failure.
- **Idempotency**: Re-running a completed range results in NO side effects except "Already Synced" logs.
- **Provenance**: Every task execution and hook invocation is etched into the Evolution Log.
