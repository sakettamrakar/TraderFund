# V3 Memory Convergence — Detailed LLM Task Definitions

**Generated**: 2026-02-23
**Objective**: Provide deeply contextualized, ready-to-execute task definitions for converging the V3 Memory layers with V2 operational contracts. Each task is scoped and detailed so that an agent with minimal prior context can independently execute it successfully.

---

## Phase 1: Deep Foundation Stabilization (P0 Risks)
*Context: The V3 foundational layers (00-02) are currently too narrative and lack the enforcement depth of the V2 system. These tasks anchor V3 intents to V2 realities.*

### Task 1.1: `00_vision.md` Contract Synthesis & Alignment
**Objective**: Anchor the aspirational V3 vision layer to binding V2 operational contracts so that vision anti-patterns and hierarchies are structurally enforced.
**Target Files**: 
- `docs/memory/00_vision.md`
*Reference*: `docs/epistemic/architectural_invariants.md`, `docs/contracts/layer_interaction_contract.md`

**Task Context**: 
The audit revealed `00_vision.md` operates as a purely narrative philosophy document. Its anti-patterns and 13-level cognitive hierarchy are stated but lack enforcement chains. To fix this, V3 vision must formally cite the V2 documents holding the binding rules.

**Execution Instructions**:
1. Open `docs/memory/00_vision.md`.
2. Locate the "Anti-Patterns" section. For each anti-pattern, explicitly document its V2 enforcement mechanism by referencing `docs/epistemic/architectural_invariants.md` and related validators.
3. Locate the "Cognitive Hierarchy" section. Add explicit references mapping this hierarchy to `docs/contracts/layer_interaction_contract.md`, stating that the interaction boundaries are governed constitutionally by that V2 contract.
4. Add a new `## Binding Contracts` section at the end of the document, declaring that the vision principles are operationally enforced via V2 contracts.

**Acceptance Criteria**:
- Contains a `## Binding Contracts` section.
- Every anti-pattern has a paired, explicit reference to a V2 enforcement mechanism.
- Hierarchy definitions explicitly cite `layer_interaction_contract.md`.

---

### Task 1.2: `01_scope.md` Adapter Declaration
**Objective**: Declare `01_scope.md` as an intent layer that delegates actual enforcement to the V2 truth advancement gates.
**Target Files**: 
- `docs/memory/01_scope.md`
*Reference*: `docs/epistemic/current_phase.md`, `docs/governance/truth_advancement_gates.md`

**Task Context**: 
The scope document states strict "Three Worlds" rules (Vision/Research/Production) and Research Exit Criteria but has no mechanism to block violations. The actual gating logic exists in V2 execution code.

**Execution Instructions**:
1. Open `docs/memory/01_scope.md`.
2. Below the main header, insert an explicit "Adapter Declaration" warning box. It must state: *"Scope enforcement is delegated to V2 governance gates (see `docs/governance/truth_advancement_gates.md`). This document represents the structural intent."*
3. Link the Phase Exit Criteria directly to the exact gating mechanisms in V2 documentation. Add a formal synchronization trigger note: *"When `docs/epistemic/current_phase.md` completes or advances, this Scope document MUST be synchronized."*

**Acceptance Criteria**:
- Explicit Adapter Declaration warning is present.
- Phase Exit Criteria section contains explicit links back to V2 gate checks.
- A synchronization rule for `current_phase.md` is clearly stated.

---

### Task 1.3: `02_success.md` Canonical Definition Realignment
**Objective**: Expand the rigorous L3 invariant pattern to other layers and cleanse the document of unrelated testing mechanisms.
**Target Files**: 
- `docs/memory/02_success.md`

**Task Context**: 
`02_success.md` strongly defines success parameters, but only L3 Meta-Analysis has formally embedded invariants. Additionally, unrelated testing configurations (TEST_ROUTER, commit triggers) are dirtying the system's canonical success definition.

**Execution Instructions**:
1. Open `docs/memory/02_success.md`.
2. Replicate the formal "invariant" declaration pattern used for L3 Meta-Analysis and apply it to:
   - L1 Regime (e.g., invariants preventing false regime state flips)
   - L6-L7 Discovery (e.g., invariants preventing opportunity leakage)
   - L8-L9 Portfolio Intelligence (e.g., capital allocation boundaries)
3. Remove testing framework artifacts (such as references to TEST_ROUTER or CI commit triggers T2/T4). Create a note that testing implementations belong in the `tests/` directory or a separate testing contract.
4. Wire the "Phase Exit Criteria" to point directly to the mechanisms in V2 truth advancement documentation.

**Acceptance Criteria**:
- L1, L6-L7, and L8-L9 have explicitly defined formal invariants matching the existing L3 format.
- Test routing and CI triggers are purged from the canonical success criteria.

---

### Task 1.4: `07_execution.md` Authority Unification
**Objective**: Eliminate the authority ambiguity between the V3 Execution layer and the V2 Constitutional Harness Contract.
**Target Files**: 
- `docs/memory/07_execution.md`
*Reference*: `docs/contracts/execution_harness_contract.md`

**Task Context**: 
`07_execution.md` states "Intent only," while V2 `execution_harness_contract.md` declares itself "Constitutional — Binding." Both documents list identical rules (e.g., harness prohibitions). We need a clear pointer to the V2 document as the sole operational authority.

**Execution Instructions**:
1. Open `docs/memory/07_execution.md`.
2. Add a prominent `> [!IMPORTANT]` or primary header stating: *"Runtime authority is legally bound by `docs/contracts/execution_harness_contract.md` (Constitutional — Binding). This document serves purely as a reference summary."*
3. In the "Harness Prohibitions" or rules section, remove the fully duplicated rule text and replace it with a section-by-section cross-reference to the appropriate clauses in the V2 contract, so if V2 changes, V3 doesn't go stale.

**Acceptance Criteria**:
- The document clearly defers to `execution_harness_contract.md` as the binding authority.
- Redundant prohibition rules are replaced with pointers to the V2 contract.

---

## Phase 2: Epistemic Unification & Invariant Alignment (P1 Risks)

### Task 2.1: Invariant Reconciliation (`09_security.md` vs V2)
**Objective**: Reconcile the 7 invariants in V3 against the 9 in V2 to create a single, unified canonical invariant list.
**Target Files**: 
- `docs/memory/09_security.md`
*Reference*: `docs/epistemic/architectural_invariants.md`, `docs/capital/kill_switch.md`

**Task Context**: 
V3 lists 7 ABSOLUTE invariants, while V2 lists 9. Neither is a perfect superset of the other, resulting in ~11 total unique invariants across both systems. System safety guarantees cannot be split.

**Execution Instructions**:
1. Read `docs/epistemic/architectural_invariants.md` and `docs/memory/09_security.md`.
2. Merge the two lists into a definitive, unified superset of all invariants inside `09_security.md`.
3. For each invariant, add explicit provenance links showing where it is enforced in V2 code/documentation.
4. Next to the `INV-NO-SELF-ACTIVATION` or relevant capital invariants, explicitly add a reference to `docs/capital/kill_switch.md` as the enforcement authority.
5. Add a note declaring `09_security.md` as the unified source, superseding the V2 invariant listing.

**Acceptance Criteria**:
- `09_security.md` contains the complete superset of invariants from both V2 and V3.
- Provenance/enforcement links are attached to every invariant.

---

### Task 2.2: Degraded State Registry Consolidation (`08_reliability.md`)
**Objective**: Resolve the duplicate documentation of Degraded States to prevent desynchronization.
**Target Files**: 
- `docs/memory/08_reliability.md`
*Reference*: `docs/data/degraded_state_registry.md`

**Task Context**: 
Authorized degraded states (like DEG-IN-001) are defined in both V3 `08_reliability.md` and V2 `data/degraded_state_registry.md`. This is a dual-maintenance risk.

**Execution Instructions**:
1. Open `docs/memory/08_reliability.md`.
2. Remove the full definitions of DEG-IN-001, DEG-US-001, and similar states.
3. Replace them with a summarized table that points explicitly to V2 `docs/data/degraded_state_registry.md` as the "exclusive live, operative registry."
4. Add a required "Last Synced from V2" timestamp field in the table to track freshness.

**Acceptance Criteria**:
- Duplicate degraded state definitions are removed from V3.
- V3 explicitly points operators to the V2 registry for live state definitions.

---

## Phase 3: Contract Adapting & Version Locking (P1 & P2 Risks)

### Task 3.1: `04_architecture.md` BAN Rules Adapter
**Objective**: Explicitly separate V3 design declarations from V2 runtime enforcement to eliminate authority confusion for the BAN rules.
**Target Files**: 
- `docs/memory/04_architecture.md`
*Reference*: `docs/contracts/layer_interaction_contract.md`

**Task Context**: 
V3 Architecture defines rules BAN-1 through BAN-4. These exact rules exist in V2 contracts. V3 should frame these as the "Design Summary" and point to V2 as the "Enforcing Code".

**Execution Instructions**:
1. Open `docs/memory/04_architecture.md`.
2. Locate the BAN rules section. Mark the section visually as a "Design Declaration".
3. For each BAN rule, attach the exact Section/Document reference from V2 `docs/contracts/layer_interaction_contract.md` where that rule is constitutionally enforced.

**Acceptance Criteria**:
- BAN rules are marked as design-level summaries.
- Each BAN rule has a direct link to its V2 enforcement contract.

---

### Task 3.2: `06_data.md` Version Locking
**Objective**: Implement version/date-locking for V2 contracts referenced in the V3 Data layer to detect staleness automatically.
**Target Files**: 
- `docs/memory/06_data.md`

**Task Context**: 
`06_data.md` correctly consolidates multiple V2 schema and contract documents. However, if a V2 schema changes, V3 will silently become outdated.

**Execution Instructions**:
1. Open `docs/memory/06_data.md`.
2. For every referenced V2 contract or schema (e.g., proxy sets, lineage rules, schema contracts), append a `[Last Validated Version/Date: <Date>]` tag next to the link.
3. Explicitly flag the three key V2 locked contracts (`CON-001`, `CON-002`, `CON-003 NEVER`) as immutable external dependencies that must not be overridden by V3 changes.

**Acceptance Criteria**:
- All V2 contract references include a "Last Validated" date stamp.
- Immutable external dependencies are explicitly flagged to operators.

---

### Task 3.3: `11_deployment.md` DWBS Synchronization
**Objective**: Prevent the V3 deployment summary from drifting away from the live V2 build system tracking.
**Target Files**: 
- `docs/memory/11_deployment.md`
*Reference*: `docs/architecture/DWBS.md`, `docs/governance/MODULE_AUTHORITY_MATRIX.md`

**Task Context**: 
The V3 layer summarizes build history (Planes 1-7) but the V2 DWBS is the actual build tracker. As planes are completed, V3 goes stale.

**Execution Instructions**:
1. Open `docs/memory/11_deployment.md`.
2. Add a bolded formal synchronization rule: *"CRITICAL: Whenever `docs/architecture/DWBS.md` adds or completes a new engineering Plane, Section 5.1 of this document MUST be updated in the same PR."*
3. Update the migration pending items to link dynamically (via reference) to the current state of V2 `docs/governance/MODULE_AUTHORITY_MATRIX.md`.

**Acceptance Criteria**:
- The DWBS synchronization mandate is clearly visible and documented.

---

## Phase 4: Observability Restructuring & Component Backporting

### Task 4.1: Component Health Validation Standard (`05_components.md`)
**Objective**: Formalize the tracking of the new V3 Universal Health Contract across all system component definitions.
**Target Files**: 
- `docs/memory/05_components.md`
- Auditing: All `docs/memory/05_components/*.yaml` files

**Task Context**: 
V3 introduced a brilliant OK/DEGRADED/FAILED universal health contract. However, we haven't systematically tracked which of the 18+ components actually implements it in their YAML definitions.

**Execution Instructions**:
1. Perform a quick sweep of all `.yaml` files in the `docs/memory/05_components/` directory to see which ones contain the `health_contract` field.
2. Open `docs/memory/05_components.md`.
3. Create a new "YAML Compliance Tracker" checklist section showing all 18 components, with a checkmark for the ones that currently implement the health interface properly, and an empty box for the ones that do not.
4. Add instructions indicating that a component cannot move out of the Shadow phase unless this health contract is checked off.

**Acceptance Criteria**:
- `05_components.md` contains an accurate checklist of which YAMLs implement the new health contract.

### Task 4.2: Restructure `10_observability.md` Depth
**Objective**: Link the 28-file depth from the V2 dashboard spec into the V3 observability layer so granular UI constraints are not lost.
**Target Files**: 
- `docs/memory/10_observability.md`

**Task Context**: 
V3 limits observability to a high-level summary. It missed critical deeper contracts like the provenance matrix, stress inspection mode, and staleness checks.

**Execution Instructions**:
1. Open `docs/memory/10_observability.md`.
2. Create a "Deep Dive Operational Contracts" subsection.
3. Explicitly link to and summarize the role of the following V2 documents:
   - `docs/dashboard/provenance_matrix.md`
   - `docs/dashboard/stress_inspection_mode_contract.md`
   - `docs/dashboard/regime_visibility_rules.md`
   - `docs/dashboard/staleness_and_honesty_checks.md`
4. State that for rigorous UI guardrail implementations, the V2 `dashboard/` directory holds the complete operational specifications.

**Acceptance Criteria**:
- V3 Observability points to the 4 missing V2 dashboard contracts explicitly, preserving system observability constraints.

---

## Phase 5: Orchestration Issue Resolution (P2 Risks)

### Task 5.1: Resolving `12_orchestration.md` Gaps
**Objective**: Elevate 3 identified "OPEN_QUESTION" segments into formal delivery tasks and resolve the component matrix ambiguity.
**Target Files**: 
- `docs/memory/12_orchestration.md`
*Reference*: `docs/contracts/decision_policy_contract.md`

**Task Context**: 
`12_orchestration.md` honestly flags some gaps as "OPEN_QUESTIONS". These need to be converted to formal actionable obligations.

**Execution Instructions**:
1. Open `docs/memory/12_orchestration.md`.
2. Locate the 3 `OPEN_QUESTION`s. Convert them into formal `TODO`s or `ACTION ITEMS` labeled with "Target Resolution: Needs Assignee".
3. For the shadow mode governance enforcement anomaly, specifically add a pointer to the V2 `decision_policy_contract.md` to indicate where the enforcement logic needs to be constructed.
4. Add a "Source YAML Version" metadata column to the component retry policy table, indicating the date or version of the YAML from which the retry data was aggregated, helping detect staleness.

**Acceptance Criteria**:
- Open questions are now tracked Action Items.
- The Retry table includes a column for tracking YAML source freshness.

### Task 5.2: Domain Enforcement via Skill Binding (`03_domain.md`)
**Objective**: Connect the CANONICAL domain definitions to the actual automation skill that checks for semantic violations.
**Target Files**: 
- `docs/memory/03_domain.md`

**Task Context**: 
The domain model is excellent, but an LLM or human modifying a file might violate the schema because there's no mention of how violations are detected.

**Execution Instructions**:
1. Open `docs/memory/03_domain.md`.
2. Add a new section titled `## Violation Detection & Enforcement`.
3. In this section, state that the structural integrity of this CANONICAL domain model is actively monitored and enforced by the `epistemic/cognitive_order_validator.md` skill (or similar V2 validators), meaning deviations will be caught conceptually by the system's review layer.

**Acceptance Criteria**:
- `03_domain.md` lists the validator/skill responsible for policing its canonical structure.
