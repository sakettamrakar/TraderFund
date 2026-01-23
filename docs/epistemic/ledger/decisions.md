# Decision Ledger

**Status**: Authoritative. Append-Only.

### Epistemic Authority

The global hierarchy of truth is strictly defined as:

1.  **Decision Ledger** (Authoritative)
2.  **Architectural Invariants**
3.  **Active Constraints**
4.  **Current Phase Rules**
5.  **Assumption Changes**
6.  **Evolution Log** (Informational)

Lower layers cannot override higher layers. Conflicts must be resolved upward, never downward.

### Decision Precedence & Immutability

*   **Immutable**: Decisions are immutable once recorded.
*   **Explicit Supersession**: New decisions may only extend or supersede older ones with explicit reference.
*   **No Implicit Weakening**: No decision may weaken a prior decision implicitly.
*   **No Temporary Exceptions**: Temporary exceptions are forbidden; strict adherence is required.

---

### [2026-01-18] D003: Shadow-Mode Validation

**Decision**: The system will validate strategies via a "Shadow Mode" where live data is processed and signals are logged but not executed, rather than relying solely on backtests.
**Rationale**: Backtests are prone to overfitting and operational drift. Live Shadow Mode proves the entire pipeline (ingestion -> signal) works in reality before risking capital.
**Impacted Documents**: `current_phase.md`, `project_intent.md`

---

### [2026-01-18] D002: Separation of Signal vs Execution

**Decision**: The Signal Generation layer (Momentum Engine) is strictly decoupled from the Execution layer. Use of a "Signal" object as the only interface.
**Rationale**: Prevents execution constraints (capital, broker availability) from polluting the purity of the alpha signal. Allows reuse of the same signal engine for different capital bases.
**Impacted Documents**: `architectural_invariants.md`, `project_intent.md`

---

### [2026-01-18] D001: Adoption of Regime-First Cognition

**Decision**: All strategy execution must be preceded by a Market Regime classification step. Strategies are only valid within specific regimes.
**Rationale**: Momentum strategies fail in chopping markets. Explicit regime recognition prevents "strategy drift" and protects capital during unfavorable conditions.
**Impacted Documents**: `project_intent.md` (Context Before Signal)
### [2026-01-24] D004: Unfreeze Phase 2 (Skill Portfolio)

**Decision**: Authorize the specification and execution of Phase 2 skills (Drift Detector, Pattern Matcher, Constraint Validator) while keeping the wider system Frozen.
**Rationale**: These skills are "Epistemic Guards" required to enforce the Freeze itself. Building the police force does not violate the law.
**Impacted Documents**: `task_graph.md`, `execution_plan.md`

---

### [2026-01-24] D005: Authorize Phase 3 (Workflow Stabilization & Repair)
**Decision**: Unfreeze Phase 3 and augment its scope to include "Critical Pipeline Repairs" (Narrative/Decision link) alongside Runbook definition.
**Rationale**: System Audit confirmed the "Brain" is disconnected. Defining runbooks for a broken system is futile. We must stabilize (fix) the workflow to make it documentable.
**Impacted Documents**: `task_graph.md`, `execution_plan.md`

---

### [2026-01-24] D006: Authorize Phase 4 (Multi-Human Governance)
**Decision**: Unfreeze Phase 4 (Conflict Resolution & Operator Attribution).
**Rationale**: System is transitioning to multi-context operation. Explicit rules for human agreement and attribution are required to prevent epistemic forks.
**Impacted Documents**: `task_graph.md`, `execution_plan.md`, `impact_resolution_contract.md`

---

### [2026-01-24] D007: Authorize Phase 5 (Observability & Audit Hardening)
**Decision**: Unfreeze Phase 5 (Structured Logging, Audit Viewer, Retention Policy).
**Rationale**: To maintain "Glass Box" observability at scale, we must move from ad-hoc text logs to machine-parseable structured logs.
**Impacted Documents**: `task_graph.md`, `execution_plan.md`, `logging.py`

---

### [2026-01-24] D008: Authorize Phase 6 (Selective Automation - Passive Only)
**Decision**: Unfreeze Phase 6 for **Passive Monitoring** purposes only.
**Rationale**: User requested next skill. Automation must be introduced gradually. First step is "Suggest, Don't Act".
**Impacted Documents**: `task_graph.md`, `bounded_automation_contract.md`
