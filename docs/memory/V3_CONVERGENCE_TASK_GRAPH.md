# V3 Memory Convergence & Migration Task Graph

**Generated**: 2026-02-23
**Based on**: `CONVERGENCE_AUDIT_ALL_LAYERS.md`
**Objective**: Systematically resolve capability gaps, authority ambiguities, and structural drift between V3 intent layers and V2 operational contracts, achieving a unified canonical reference state.

---

## Phase 1: Deep Foundation Stabilization (P0 Risks)
*Targeting the Bimodal Maturity Risk where layers 00-02 lack operational rigor, and resolving the P0 Authority Ambiguity.*

### 1.1 `00_vision` Contract Synthesis
- [ ] **T1.1.1**: Add a "Binding Contracts" section to `00_vision.md`.
- [ ] **T1.1.2**: Map each stated vision anti-pattern to its enforcement mechanism in V2 `epistemic/architectural_invariants.md`.
- [ ] **T1.1.3**: Map the 13-level cognitive hierarchy explicitly to V2 `contracts/layer_interaction_contract.md` to bind vision to build sequence.

### 1.2 `01_scope` Adapter Declaration
- [ ] **T1.2.1**: Insert an explicit adapter declaration in `01_scope.md` stating scope enforcement is operationally delegated to V2 `governance/truth_advancement_gates.md`.
- [ ] **T1.2.2**: Define a formal synchronization trigger ensuring changes to `epistemic/current_phase.md` mandate a review of `01_scope.md`.

### 1.3 `02_success` Canonical Definition Realignment
- [ ] **T1.3.1**: Replicate the formal L3 invariant pattern to create explicit invariants for the L1 Regime layer.
- [ ] **T1.3.2**: Replicate the formal L3 invariant pattern to create explicit invariants for L6-L7 Discovery.
- [ ] **T1.3.3**: Replicate the formal L3 invariant pattern to create explicit invariants for L8-L9 Portfolio Intelligence.
- [ ] **T1.3.4**: Cleanse `02_success.md` by moving non-success test invariants (TEST_ROUTER, commit triggers) to a separate V2 testing contract.
- [ ] **T1.3.5**: Wire the 02_success Phase Exit Criteria to point directly to the exact gating mechanisms in V2 documentation.

### 1.4 `07_execution` Authority Unification
- [ ] **T1.4.1**: Add a primary header to `07_execution.md` declaring: "Runtime authority is `docs/contracts/execution_harness_contract.md` (Constitutional — Binding)."
- [ ] **T1.4.2**: Remove redundant rule declarations and create section-by-section cross-references to the V2 contract for harness prohibitions.

---

## Phase 2: Epistemic Unification & Invariant Alignment (P1 Risks)
*Targeting the Invariant Coverage Gap (7 vs 9) and identifying sources of truth.*

### 2.1 Invariant Reconciliation (`09_security` & V2 Contracts)
- [ ] **T2.1.1**: Conduct a line-by-line reconciliation of the 7 V3 ABSOLUTE invariants against the 9 V2 architectural invariants.
- [ ] **T2.1.2**: Generate a unified superset invariant list (likely ~11 invariants).
- [ ] **T2.1.3**: Update `09_security.md` to host this unified list with explicit provenance links to V2 code/enforcement layers.
- [ ] **T2.1.4**: Add a direct enforcement reference to V2 `capital/kill_switch.md` next to the `INV-NO-SELF-ACTIVATION` invariant.

### 2.2 Degraded State Registry Consolidation (`08_reliability`)
- [ ] **T2.2.1**: Update `08_reliability.md` to declare V2 `data/degraded_state_registry.md` as the exclusive live, operative registry.
- [ ] **T2.2.2**: Convert the degraded state list in `08_reliability.md` to a summary format and add a required "last synced" timestamp field.
- [ ] **T2.2.3**: Remove DEG-IN-001 and DEG-US-001 duplicate definitions from V3 and point to the V2 references.

---

## Phase 3: Contract Adapting & Version Locking (P1 & P2 Risks)
*Establishing adapter layers for files that merely wrap V2 functionality, preventing synchronization drift.*

### 3.1 `04_architecture` Adapter Pattern
- [ ] **T3.1.1**: Mark the BAN rules in `04_architecture.md` as "Design Declaration" to separate them from V2 "Runtime Enforcement".
- [ ] **T3.1.2**: Attach exact V2 contract section numbers as reference links to each mapped BAN rule.

### 3.2 `06_data` Version Locking
- [ ] **T3.2.1**: Implement version/date-locking for every V2 contract referenced in `06_data.md` to detect staleness.
- [ ] **T3.2.2**: Explicitly flag V2 locked contracts (`CON-001`, `CON-002`, `CON-003 NEVER`) as immutable external dependencies within `06_data.md`.

### 3.3 `11_deployment` DWBS Synchronization
- [ ] **T3.3.1**: Add a formal synchronization rule stating 11_deployment §5.1 must be updated strictly within the same PR when `architecture/DWBS.md` is updated.
- [ ] **T3.3.2**: Link pending phase/module migrations dynamically to V2 `MODULE_AUTHORITY_MATRIX.md`.

---

## Phase 4: Observability Restructuring & Component Backporting
*Expanding V3 capabilities to mirror V2 reporting depths, and utilizing V3 novel contracts to augment V2.*

### 4.1 Component Health Validation (`05_components`)
- [ ] **T4.1.1**: Perform a sweep of all component YAMLs (`docs/memory/05_components/*.yaml`) verifying the existence of the `health_contract` field.
- [ ] **T4.1.2**: Embed a YAML compliance checklist within `05_components.md` tracking which components have successfully integrated the OK/DEGRADED/FAILED health interface.

### 4.2 Restructure `10_observability` Depth
- [ ] **T4.2.1**: Integrate or cross-reference the missing V2 `dashboard/provenance_matrix.md` into `10_observability.md`.
- [ ] **T4.2.2**: Integrate or cross-reference V2 `dashboard/stress_inspection_mode_contract.md`.
- [ ] **T4.2.3**: Integrate or cross-reference V2 `dashboard/regime_visibility_rules.md`.
- [ ] **T4.2.4**: Integrate or cross-reference V2 `dashboard/staleness_and_honesty_checks.md`.
- [ ] **T4.2.5**: Upgrade `10_observability.md` to link directly to the V2 dashboard folder treating it as the authoritative operational spec rather than a summarized abstract.

---

## Phase 5: Orchestration Issue Resolution (P2 Risks)
*Directly addressing the OPEN_QUESTION gaps identified in `12_orchestration` and domain linkage.*

### 5.1 Orchestration Gaps (`12_orchestration`)
- [ ] **T5.1.1**: Convert the 3 identified `OPEN_QUESTION` instances inside `12_orchestration.md` into formally tracked internal issues with target owners.
- [ ] **T5.1.2**: Resolve the shadow mode governance enforcement anomaly by explicitly referencing the V2 decision policy contract.
- [ ] **T5.1.3**: Add a "Source Version" metadata column to the component retry policy table, indicating which YAML version the table rows were consolidated from.
- [ ] **T5.1.4**: Define an explicit adapter/implementation plan to route the Narrative Engine missing adapter gap, closing the "NOT_WIRED" loop.

### 5.2 Domain Violation Detection (`03_domain`)
- [ ] **T5.2.1**: Enhance `03_domain.md` to include a "Violation Detection" clause, pointing to the `epistemic/cognitive_order_validator.md` skill to enforce structural integrity of the CANONICAL domain model.
