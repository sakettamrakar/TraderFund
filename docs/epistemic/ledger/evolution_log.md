# Evolution Log

**Status**: Informational. Append-Only.

### Epistemic Authority

The global hierarchy of truth is strictly defined as:

1.  **Decision Ledger** (Authoritative)
2.  **Architectural Invariants**
3.  **Active Constraints**
4.  **Current Phase Rules**
5.  **Assumption Changes**
6.  **Evolution Log** (Informational)

Lower layers cannot override higher layers. Conflicts must be resolved upward, never downward.

### Non-Authoritative Status

*   **Descriptive**: This log is descriptive, not prescriptive.
*   **No Permission**: Entries do not grant permission to change system behavior.
*   **Authority Location**: All authoritative changes must be reflected in the Decision Ledger.

---

### [2026-01-18] Transition to Live Shadow Mode

**What Changed**: System moved from "Research/Backtest only" to "Live Shadow Mode".
**Why**: Backtesting phase completed initial validation. Need real-world data flow to verify operational stability and signal integrity.
**Scope**: Ops / Data

---

### [2026-01-10] Introduction of India Market Ingestion

**What Changed**: Added India Market (Angel One) ingestion pipeline alongside US Market.
**Why**: Expanded opportunity set to include Indian equities.
**Scope**: Data / Code

---

### [2025-12-01] Historical Replay Engine V1

**What Changed**: Implemented "Time Travel" replay capability using `CandleCursor`.
**Why**: To allow true "No Lookahead" simulation of strategies on historical data.
**Scope**: Core Engine


2026-01-22 — Validated Chat → CLI execution bridge using no-op command.
Confirmed explicit approval gate, CLI authority, and zero side effects.

2026-01-22 — Ran graph-governed execution harness in dry-run mode.
Verified authorization gating, dependency resolution, and zero side effects.

2026-01-22 — Added P1.4.1 to execution plan.
Verified authorization gating, dependency resolution, and zero side effects.
### [2026-01-24] Phase 2 Execution: Skill Portfolio Expansion

**What Changed**: Defined specifications for `Drift Detector`, `Pattern Matcher`, and `Constraint Validator`. Implemented `Drift Detector` base capability.
**Why**: To operationalize the Epistemic Foundation with automated verification skills, as authorized by `2026-01-24__roadmap__unfreeze_phase_2.md`.
**Scope**: Code / Epistemic

---

### [2026-01-24] Phase 2 Completion: Guided Guardrails
**What Changed**: Successfully implemented and verified `Drift Detector`, `Pattern Matcher`, and `Constraint Validator`.
**Why**: Completes the "Conscience" layer, allowing governed execution of future repairs.
**Scope**: Code / Epistemic

---

### [2026-01-24] EXECUTION: Control Plane Start (CP-1.1 to CP-1.2)

- **Mode**: REAL_RUN (Automated Build Harness)
- **Authorization**: D009 (Control Plane Authorization)
- **Outcome**:
    - **CP-1.1 (Belief Layer)**: SUCCESS. Created `src/layers/belief_layer.py`. Generated DID for `DWBS.md`.
    - **CP-1.2 (Factor Policy)**: SUCCESS. Created `src/layers/factor_layer.py`. Generated DID for `factor_layer_policy.md`.
- **Validation**: Epistemic Validator PASS (13/13).
- **Post-Hooks**: Standard hooks (`evolution-recorder`, `drift-detector`) completed successfully.

---

### [2026-01-24] EXECUTION: Control Plane Finalized (CP-1.3 to CP-1.4)

- **Mode**: REAL_RUN (Automated Build Harness)
- **Outcome**:
    - **CP-1.3 (Strategy Governance)**: SUCCESS. Created `src/governance/strategy_governance.py`. Generated DID for `strategy_layer_policy.md`.
    - **CP-1.4 (Validator Integration)**: SUCCESS. Created `.github/workflows/epistemic_check.yml`. Generated DID for `epistemic_drift_validator_specification.md`.
- **Validation**: Epistemic Validator PASS (13/13).
- **Milestone**: Control Plane structural objectives satisfied. Gate to Orchestration Plane is now OPEN.

