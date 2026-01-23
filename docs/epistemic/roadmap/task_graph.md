# Task Graph - Post-Freeze

**Status**: Authoritative Planning Artifact.
**Derived From**: `docs/epistemic/roadmap/dwbs_post_freeze.md`
**System State**: Freeze v1.1

## 1. Task Graph Purpose

This document translates the *Detailed Work Breakdown Structure (DWBS)* into executable units of work (Tasks).

*   **Executable Units**: Each task is a discrete unit of work that can be planned, executed, and reviewed.
*   **No Implicit Approval**: The presence of a task here does **NOT** authorize its execution.
*   **Explicit Selection**: Execution requires selecting a task from this graph and creating an active *Implementation Plan*.
*   **Freeze Impact**: The System Freeze remains in effect. Most tasks require a specific *Documented Impact Declaration (DID)* and unfreeze approval to proceed.

## 2. Task Identification Scheme

**Format**: `P<Phase>.<Subphase>.<Task>`
*   `Phase`: Matches DWBS Phase (e.g., P1).
*   `Subphase`: Matches DWBS Item (e.g., 1.1).
*   `Task`: Granular step (e.g., 1).

## 3. Active & Completed Tasks (P1)

### Phase P1: Execution Bridging (Milestone 8)
**Status**: Executed.

#### Task P1.1.1: Create Chat Usage Contract
*   **Name**: Create `chat_execution_contract.md`
*   **Derived From**: DWBS 1.1
*   **Description**: Create the authoritative contract defining rules for chat-drafted commands.
*   **Inputs**: Epistemic norms.
*   **Outputs**: `docs/epistemic/chat_execution_contract.md`.
*   **Dependencies**: None.
*   **Freeze Impact**: Scoped Unfreeze (Approved).
*   **Skill Involvement**: None.

#### Task P1.2.1: Implement Bridge Script
*   **Name**: Create `chat_exec_bridge.py`
*   **Derived From**: DWBS 1.2
*   **Description**: Implement the Python script allowing human confirmation of chat drafts.
*   **Inputs**: `chat_execution_contract.md`.
*   **Outputs**: `bin/chat_exec_bridge.py`.
*   **Dependencies**: P1.1.1.
*   **Freeze Impact**: Scoped Unfreeze (Approved).
*   **Skill Involvement**: None.

#### Task P1.3.1: Verify Bridge Workflow
*   **Name**: Verify Draft-Confirm Loop
*   **Derived From**: DWBS 1.3
*   **Description**: Manually verify the chat-draft -> human-confirm -> execute cycle.
*   **Inputs**: Bridge script.
*   **Outputs**: Verification log/audit.
*   **Dependencies**: P1.2.1.
*   **Freeze Impact**: Scoped Unfreeze (Approved).
*   **Skill Involvement**: None.


#### Task P1.4.1: Graph-Governed Execution Harness (Dry Run)
*   **Name**: Graph-Governed Execution Harness (Dry Run)
*   **Derived From**: Milestone 9 (Correction)
*   **Description**: Introduce a deterministic, non-executing harness that reads the task graph, respects dependencies and freeze state, prints execution order and eligibility, and executes no tasks.
*   **Inputs**: `docs/epistemic/roadmap/task_graph.md`, `docs/epistemic/roadmap/execution_plan.md`
*   **Outputs**: Stdout only (no files modified).
*   **Dependencies**: None.
*   **Freeze Impact**: None.
*   **Skill Involvement**: Execution Harness (CLI).
*   **Note**: This task performs NO execution and is a prerequisite for future execution. Approval via execution_plan.md is required.

## 4. Future Tasks (Frozen)

### Phase P2: Skill Portfolio Expansion
**Status**: FROZEN.

#### Task P2.1.1: Specify Drift Detector Skill
*   **Derived From**: DWBS 2.1
*   **Description**: Create `drift_detector.md` spec defining inputs/outputs for drift detection.
*   **Dependencies**: P1.3.1.
*   **Status**: **EXECUTED**
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P2.2.1: Specify Pattern Matcher Skill
*   **Derived From**: DWBS 2.2
*   **Description**: Create `pattern_matcher.md` spec for historical pattern recognition.
*   **Dependencies**: P1.3.1.
*   **Status**: **EXECUTED**
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P2.3.1: Specify Constraint Validator Skill
*   **Derived From**: DWBS 2.3
*   **Description**: Create `constraint_validator.md` spec for checking logic invariants.
*   **Dependencies**: P1.3.1.
*   **Status**: **EXECUTED**
*   **Freeze Impact**: Scoped Unfreeze (Approved).

### Phase P3: Workflow Stabilization
**Status**: ACTIVE / UNFROZEN.

#### Task P3.1.1: Standardize Start of Day
*   **Derived From**: DWBS 3.1
*   **Description**: Create `runbooks/start_of_day.md` checklist.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P3.2.1: Standardize End of Day
*   **Derived From**: DWBS 3.2
*   **Description**: Create `runbooks/end_of_day.md` checklist.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P3.3.1: Document Troubleshooting
*   **Derived From**: DWBS 3.3
*   **Description**: Create `runbooks/troubleshooting.md`.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P3.4.1: Critical Repair - Narrative CLI
*   **Derived From**: Audit 2026-01-24 (DID 2026-01-24__roadmap__unfreeze_phase_3)
*   **Description**: Implement `bin/run_narrative.py` or similar to unify narrative generation.
*   **Freeze Impact**: Scoped Unfreeze (Approved).
*   **Skill Involvement**: Mode C (Skill-Executable).

#### Task P3.4.2: Critical Repair - Decision Logic
*   **Derived From**: Audit 2026-01-24 (DID 2026-01-24__roadmap__unfreeze_phase_3)
*   **Description**: Connect Narrative output to Decision logic and verify artifact generation.
*   **Freeze Impact**: Scoped Unfreeze (Approved).
*   **Skill Involvement**: Mode C (Skill-Executable).

### Phase P4: Multi-Human Governance
**Status**: ACTIVE / UNFROZEN.

#### Task P4.1.1: Define Conflict Resolution
*   **Derived From**: DWBS 4.1
*   **Description**: Update `impact_resolution_contract.md` for multi-user conflicts.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P4.2.1: Implement Operator Attribution
*   **Derived From**: DWBS 4.2
*   **Description**: Update logging modules to capture detailed operator identity.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

### Phase P5: Observability & Audit Hardening
**Status**: ACTIVE / UNFROZEN.

#### Task P5.1.1: Implement Structured Logging
*   **Derived From**: DWBS 5.1
*   **Description**: Standardize JSON/structured logs across all skills.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P5.2.1: Create Audit Log Viewer
*   **Derived From**: DWBS 5.2
*   **Description**: Create a read-only skill to parse and display audit logs.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P5.3.1: Define Data Retention
*   **Derived From**: DWBS 5.3
*   **Description**: Create `docs/epistemic/data_retention_policy.md`.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

### Phase P6: Selective Automation
**Status**: ACTIVE / UNFROZEN (PASSIVE ONLY).

#### Task P6.1.1: Define Bounded Automation Contract
*   **Derived From**: DWBS 6.1
*   **Description**: Create authoritative contract for any automated triggers.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

#### Task P6.2.1: Prototype Monitor Trigger
*   **Derived From**: DWBS 6.2
*   **Description**: Create a passive monitor that suggests invocations but cannot run them.
*   **Dependencies**: P6.1.1.
*   **Freeze Impact**: Scoped Unfreeze (Approved).

### Phase P7: System Maturity
**Status**: FROZEN.

#### Task P7.1.1: Finalize Epistemic Ledgers
*   **Derived From**: DWBS 7.1
*   **Description**: Review and lock all ledger history.
*   **Freeze Impact**: Requires Unfreeze.

#### Task P7.2.1: Freeze Skill Catalog V1
*   **Derived From**: DWBS 7.2
*   **Description**: Tag and version the entire skill set.
*   **Freeze Impact**: Requires Unfreeze.

#### Task P7.3.1: Archive Development Artifacts
*   **Derived From**: DWBS 7.3
*   **Description**: Move non-essential docs to `docs/archive/`.
*   **Freeze Impact**: Requires Unfreeze.

## 5. Non-Goals

1.  **No Schedule**: This graph does not imply dates or deadlines.
2.  **No Auto-Trigger**: Existence of a task does not trigger the `Change Summarizer` or any other skill.
3.  **No Assignment**: Tasks are unassigned until an Implementation Plan is active.
4.  **No Bypass**: This graph does not bypass the requirement for a DID.

## 6. Summary

*   **Active/Executed Tasks**: 4 (P1)
*   **Frozen Tasks**: 16 (P2-P7)
*   **Total Dependency Edges**: ~5
*   **Note**: All P2+ tasks are currently theoretical and legally blocked by System Freeze v1.1.
