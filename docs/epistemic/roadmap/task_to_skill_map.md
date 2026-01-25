# Task to Skill Map - Post-Freeze

**Status**: Authoritative Planning Artifact.
**Derived From**: `docs/epistemic/roadmap/task_graph.md`
**System State**: Freeze v1.1

## 1. Mapping Purpose

This document maps the actionable tasks defined in the Task Graph to their authorized execution modes.

*   **Human-Only (A)**: Task must be performed entirely by a human.
*   **Skill-Assisted (B)**: Human performs task with help from an existing skill (e.g., Change Summarizer).
*   **Skill-Executable (C)**: Task can be fully executed via `run-skill` (Human initiated).
*   **Future Skill Required (D)**: Task requires a skill that does not yet exist.
*   **Deferred / Frozen (E)**: Task is blocked by policy or logic.

## 2. Task Mapping Table

| Task ID | Task Name | Mode | Skill Name | Skill Role | Justification | Impact | Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P1.1.1** | Create Chat Usage Contract | **A** | N/A | N/A | Epistemic definition is strictly human domain. | Unfrozen | Low |
| **P1.2.1** | Implement Bridge Script | **A** | N/A | N/A | Coding critical infrastructure requires human engineering. | Unfrozen | Med |
| **P1.3.1** | Verify Bridge Workflow | **B** | Change Summarizer | Observational | Verification involves running the bridge; Summarizer can verify diffs. | Unfrozen | Low |
| **P1.4.1** | Graph-Governed Execution Harness (Dry Run) | **C** | execute-task-graph | Executable | Required to safely observe task graph execution order before authorizing real execution. | Unfrozen | Low |
| **P2.1.1** | Specify Drift Detector Skill | **A** | N/A | N/A | Specification of new capability is human design work. | Unfreeze Req | Low |
| **P2.2.1** | Specify Pattern Matcher Skill | **A** | N/A | N/A | Specification of new capability is human design work. | Unfreeze Req | Low |
| **P2.3.1** | Specify Constraint Validator Skill | **A** | N/A | N/A | Specification of new capability is human design work. | Unfreeze Req | Low |
| **P3.1.1** | Standardize Start of Day | **A** | N/A | N/A | Defining operational runbooks is a human process. | Unfrozen | Low |
| **P3.2.1** | Standardize End of Day | **A** | N/A | N/A | Defining operational runbooks is a human process. | Unfrozen | Low |
| **P3.3.1** | Document Troubleshooting | **A** | N/A | N/A | Defining operational runbooks is a human process. | Unfrozen | Low |
| **P3.4.1** | Repair Narrative CLI | **B** | N/A | N/A | Coding task. Will require verification. | Unfrozen | Med |
| **P3.4.2** | Repair Decision Logic | **B** | Constraint Validator | Validation | Coding task. Validator monitors artifacts. | Unfrozen | High |
| **P4.1.1** | Define Conflict Resolution | **A** | N/A | N/A | Governance policy definition is human domain. | Unfreeze Req | Low |
| **P4.2.1** | Implement Operator Attribution | **A** | N/A | N/A | Coding critical infrastructure requires human engineering. | Unfreeze Req | Med |
| **P5.1.1** | Implement Structured Logging | **A** | N/A | N/A | Architectural change to codebase. | Unfreeze Req | Med |
| **P5.2.1** | Create Audit Log Viewer Skill | **A** | N/A | N/A | Creation of a new skill is a human coding task. | Unfreeze Req | Med |
| **P5.3.1** | Define Data Retention | **A** | N/A | N/A | Policy definition is human domain. | Unfreeze Req | Low |
| **P6.1.1** | Define Bounded Automation Contract | **A** | N/A | N/A | High-risk policy definition requires human authority. | Unfreeze Req | High |
| **P6.2.1** | Prototype Monitor Trigger | **A** | N/A | N/A | Prototyping risky automation requires human control. | Unfreeze Req | High |
| **P7.1.1** | Finalize Epistemic Ledgers | **A** | N/A | N/A | Final review of truth sources is human domain. | Unfreeze Req | Low |
| **P7.2.1** | Freeze Skill Catalog V1 | **A** | N/A | N/A | Governance decision to freeze. | Unfreeze Req | Low |
| **P7.3.1** | Archive Development Artifacts | **A** | N/A | N/A | Cleanup and organization. | Unfreeze Req | Low |

## 3. Summary & Metrics

*   **Total Tasks Mapped**: 20
*   **Mode A (Human-Only)**: 18
*   **Mode B (Skill-Assisted)**: 1 (P1.3.1 - Verification assistance)
*   **Mode C (Skill-Executable)**: 1 (P1.4.1 - Harness Dry Run)
*   **Mode D (Future Skill Required)**: 0
*   **Mode E (Deferred)**: 0 (All are technically deferred by Freeze, but mapped to their execute mode).

### Analysis
The overwhelming prevalence of **Mode A (Human-Only)** reflects the system's current lifecycle phase: **Construction & Definition**. We are building the skills and defining the rules (Human work), rather than operating the system at scale (Skill work).

As P2 (Skill Expansion) completes, future Task Graphs (Post-P2) will likely contain more Mode C and B tasks (e.g., "Analyze Daily Logs" -> Audit Viewer Skill).

### Governance Note
No task in this roadmap grants autonomous decision-making authority to any skill. Even high-risk automation (P6) is strictly strictly prototype/definition at this stage.
