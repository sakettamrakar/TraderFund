# Skill: Design/Build Execution Harness

**Category**: Orchestration (Structural)  
**Stability**: Core

## 1. Purpose
The `design-build-harness` is the authoritative orchestrator for the system's structural evolution. It transforms the [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) into a series of coordinated, validated, and recorded actions, ensuring strict adherence to the [DWBS.md](file:///c:/GIT/TraderFund/docs/architecture/DWBS.md).

## 2. Inputs & Preconditions
- **Required Inputs**: `docs/epistemic/roadmap/task_graph.md`.
- **Required State**: `docs/architecture/DWBS.md`.
- **Preconditions**: Current Plane Gate must be open (authorized in ledger).
- **Validators**: Mandatory `drift-detector` PASS before REAL_RUN.

## 3. Outputs & Side Effects
- **Ledger Impact**: Appends outcome records to `evolution_log.md`.
- **DID Impact**: Automatically generates Documentation Impact Declarations for impacted files.
- **Artifacts**: Updates `task_graph.md` statuses and creates task-specific files.

## 4. Invariants & Prohibitions
- **Meta-Only**: NEVER performs trading, signal generation, or belief inference.
- **Deterministic**: Input state + Selector MUST produce identical execution sequences.
- **No Gaps**: Cannot skip tasks marked as `Blocking=TRUE`.
- **Obedience**: The harness is powerful ONLY because it is strictly obedient to the DWBS.

## 5. Invocation Format

```
Invoke design-build-harness
Mode: REAL_RUN
Target: docs/epistemic/roadmap/task_graph.md

ExecutionScope:
  mode: range
  from_task: CP-1.1
  to_task: CP-1.4

Options:
  validators: enabled
  hooks: enabled
  ledger: append
```

## 6. Failure Modes
- **Validator Failure**: Immediate HALT of the entire cycle (Terminal for cycle).
- **Dependency Violation**: Running tasks out of order (Terminal).
- **Stale State**: Invariants doc older than last decision (Terminal).

## 7. Notes for Operators
- **Dry-Run First**: ALWAYS run in `DRY_RUN` mode before committing structural changes.
- **Verification**: Post-execution, the system status is updated based on physical artifact presence.
