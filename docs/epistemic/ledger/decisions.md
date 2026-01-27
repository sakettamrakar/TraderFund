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

---

### [2026-01-24] D009: Control Plane Authorization

**Decision**: Authorize the commencement of work on the Control Plane (Tasks CP-1.1 through CP-1.4).
**Rationale**: All epistemic foundations (Belief Policy, Factor Policy, Strategy Policy) are frozen. The Task Graph v2.1 is validated and the Execution Harness is operational.
**Impacted Documents**: `task_graph.md`, `DWBS.md`, `current_phase.md`

---

### [2026-01-25] D010: Orchestration Plane Authorization

**Decision**: Authorize entry into the Orchestration Plane (Phase 2) for structural work only.
**Rationale**: All Control Plane obligations (`OBL-CP-*`) are SATISFIED. CP-1.5 verification passed. The gate to the Orchestration Plane is open.
**Scope**: Tasks `OP-2.1` through `OP-2.3`. No strategy, macro, or execution logic is authorized.
**Impacted Documents**: `task_graph.md`, `DWBS.md`, `execution_harness_contract.md`
**Non-Authorizations**: Strategy registration, execution, macro activation, factor live binding, market-facing logic.

---

### [2026-01-25] D011: Strategy Plane Authorization

**Decision**: Authorize entry into the Strategy Plane (Phase 3) for strategy definition and registration only.
**Rationale**: All Control Plane obligations (`OBL-CP-*`) and Orchestration Plane obligations (`OBL-OP-*`) are SATISFIED. The gate to the Strategy Plane is open.
**Scope**: Tasks `SP-3.1` through `SP-3.3`. Only declarative, governed, non-executable strategy definitions.
**Impacted Documents**: `task_graph.md`, `strategy_layer_policy.md`
**Non-Authorizations**: Strategy execution, signal generation, belief inference, macro/factor runtime, market-facing behavior.

---

### [2026-01-25] D012: Structural Activation Plane Authorization

**Decision**: Authorize entry into the Structural Activation Plane for read-only runtime state availability.
**Rationale**: All prior plane obligations (CP, OP, SP) are SATISFIED. Strategies exist as governed intent only. The gate to Structural Activation is open.
**Scope**: Tasks `SA-4.1` through `SA-4.2`. Read-only macro and factor state only.
**Impacted Documents**: `task_graph.md`, `latent_structural_layers.md`, `factor_layer_policy.md`
**Non-Authorizations**: Strategy execution, signal computation, scoring/ranking, conditional logic on state, market interaction, decision-ready outputs.
**Safety Assertion**: Structural Activation exposes facts, not choices. All decision-making remains forbidden.

---

### [2026-01-25] D012.5: Scale & Safety Plane Authorization

**Decision**: Authorize entry into the Scale & Safety Plane for pre-decision survivability constraint definition.
**Rationale**: All prior plane obligations (CP, OP, SP, SA) are SATISFIED. System has complete visibility but zero execution capability. Survivability constraints must be established before any decision plane.
**Scope**: Tasks `SS-5.1` through `SS-5.3`. Kill-switch, bounds, determinism, circuit breakers, audit scalability.
**Impacted Documents**: `task_graph.md`, `execution_harness_contract.md`, `bounded_automation_contract.md`
**Non-Authorizations**: Decision-making, strategy execution, signal evaluation, market interaction, conditional branching on outcomes.
**Safety Assertion**: Scale & Safety constrains future behavior but enables none. All decision authority remains absolutely forbidden.

---

### [2026-01-25] D013: Decision Plane Authorization (HITL + Shadow)

**Decision**: Authorize entry into the Decision Plane for governed choice formation.
**Rationale**: All prior plane obligations (CP, OP, SP, SA, SS) are SATISFIED. System has complete visibility, survivability, and no execution capability. The gate to choice formation is open.
**Scope**: Tasks `DE-6.1` through `DE-6.4`. Decision objects, HITL approval, Shadow execution, Audit wiring.
**Impacted Documents**: `task_graph.md`, `DWBS.md`, Decision Plane contract
**Non-Authorizations**: Real market execution, broker connectivity, capital deployment, automated action without approval, order placement, irreversible side effects.
### [2026-01-26] EV-001: Bear / Risk-Off Stress Evaluation

**Action**: Executed `EV-FORCED-BEAR-RISKOFF-V1` counterfactual evaluation.
**Authority**: D013 (Decision Plane Authorization)
**Rationale**: Required to prove "Robustness under Adversity" per Epistemic Policy.
**Outcome**:
*   `STRATEGY_MOMENTUM_V1`: Graceful failure (Rejection) confirmed.
*   `STRATEGY_VALUE_QUALITY_V1`: Robustness confirmed (0 rejections).
### [2026-01-26] EV-002: Factor Context Layer Design

**Action**: Defined `FactorContext` schema and updated DWBS `PRIN-7`.
**Authority**: Governance Obligation `OBL-EV-FACTOR-CONTEXT`.
**Rationale**: Factor resolution required to explain strategy behavior (Suitability vs Permissibility).
### [2026-01-26] EV-003: Factor Context Execution Binding

**Action**: Implemented `EV-RUN-CTX-FACTOR` and updated pipeline consumers.
**Authority**: Governance Obligation `OBL-EV-FACTOR-CONTEXT` (Constraint satisfaction).
**Rationale**: Enables observational explanation of strategy behavior without mutation.
### [2026-01-26] EV-004: Factor Context Extension v1.1

**Action**: Extended Factor Context Schema to v1.1.0 (enriched resolution).
**Authority**: Governance Obligation `OBL-EV-FACTOR-CONTEXT-V1.1`.
**Rationale**: Provide granular explanatory power for rejections without coercing strategy behavior.
### [2026-01-26] EV-005: Momentum Strategy Evolution

**Action**: Registered `STRICT`, `ACCELERATING`, and `PERSISTENT` Momentum variants.
**Authority**: Governance Obligation `OBL-SP-MOMENTUM-EVOLUTION`.
**Rationale**: Specialization of strategy logic to consume Factor Context v1.1 resolution.
**Impacted Documents**: `src/strategy/registry.py`, `bulk_evaluator.py`, `rejection_analysis.py`
### [2026-01-27] EV-006: Readiness & Portfolio Intelligence
**Action**: Executed `EV-RUN-WATCH-READINESS` and `EV-RUN-PORTFOLIO-PAPER` diagnostics.
**Authority**: D013 (Decision Plane Authorization)
**Rationale**: Required to diagnose structural opportunity sets and quantify strategy interaction before any optimization or activation is considered.
**Outcome**:
*   **Expansion/Dispersion**: `NONE` (confirmed stagnation).
*   **Portfolio Overlap**: `0.0` (confirmed regime-partitioned architecture).
**Impacted Documents**: `task_graph.md`, `evolution_comparative_summary.md`, `paper_portfolio_schema.md`
