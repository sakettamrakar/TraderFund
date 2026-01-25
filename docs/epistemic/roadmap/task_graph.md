# Task Graph — DWBS-Aligned

**Status:** Constitutional — Execution-Ready  
**Version:** 2.1  
**Derived From:** `docs/architecture/DWBS.md` v1.0  
**Date:** 2026-01-24  
**Authority:** Every task derives from a DWBS item. Orphan tasks are invalid.

---

## 1. Purpose

This document translates the DWBS into executable units of work (Tasks).

- **Constitutional Derivation:** Every task MUST map to a DWBS item
- **No Orphan Tasks:** Tasks without DWBS parent are invalid
- **Deterministic Selectors:** Supports execution via `range`, `list`, `first_n`, `last_n`
- **Post-Execution Hooks:** Supports declarative skill chaining (e.g., automated ledger updates)

---

## 1.1 Obligation Schema (Meta-Governance)

To prevent structural debt, this graph tracks **Obligations**—explicit expectations that must be satisfied before plane transition.

**Schema:**
- **ID**: `OBL-<PLANE>-<TYPE>` (e.g., `OBL-CP-BELIEF`)
- **Description**: The invariant or capability that must exist.
- **Scope**: The conceptual plane this applies to.
- **Blocking**: If `TRUE`, the plane cannot be closed until satisfied.
- **Evidence**: The specific artifact or state that proves satisfaction.

---

## 2. Obligation Index (Single Source of Truth)

### Control Plane Obligations

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-CP-BELIEF** | **Belief Governance**: Belief Layer must be operationalized in code. | Control | TRUE | `CP-1.1` | ✅ SATISFIED |
| **OBL-CP-POLICY** | **Policy Governance**: Factor/Strategy policies must be operationalized. | Control | TRUE | `CP-1.2`, `CP-1.3` | ✅ SATISFIED |
| **OBL-CP-SAFETY** | **Execution Safety**: 13 Epistemic Rules enforced in CI/CD. | Control | TRUE | `CP-1.4` | ✅ SATISFIED |
| **OBL-CP-AUDIT** | **Provenance**: All artifacts must have DIDs and Ledger entries. | Control | TRUE | *All CP Tasks* | ✅ SATISFIED |

### Orchestration Plane Obligations

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-OP-HARNESS** | **Binding Integrity**: Harness must bind to Control Plane governance. | Orchestration | TRUE | `OP-2.3` | ✅ SATISFIED |
| **OBL-OP-DETERMINISM** | **Ordering**: Task execution must be deterministic (DAG-enforced). | Orchestration | TRUE | `OP-2.2` | ✅ SATISFIED |
| **OBL-OP-NO-IMPLICIT** | **Purity**: No undeclared side effects from execution. | Orchestration | TRUE | `OP-2.1`, `OP-2.3` | ✅ SATISFIED |
| **OBL-OP-VISIBILITY** | **Predictability**: Operators can predict execution outcomes (DRY_RUN). | Orchestration | TRUE | `OP-2.3` | ✅ SATISFIED |
| **OBL-OP-CLOSURE** | **Closure**: All OBL-OP-* must be satisfied for plane closure. | Orchestration | TRUE | *All OP Tasks* | ✅ SATISFIED |

### Strategy Plane Obligations

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-SP-REGISTRY** | **Registry**: All strategies must be registered in a governed registry. | Strategy | TRUE | `SP-3.2` | ✅ SATISFIED |
| **OBL-SP-LIFECYCLE** | **Lifecycle**: Strategies must follow DRAFT → ACTIVE → SUSPENDED → RETIRED. | Strategy | TRUE | `SP-3.3` | ✅ SATISFIED |
| **OBL-SP-DECLARATIVE** | **Declarative**: Strategies declare intent, they do not compute state. | Strategy | TRUE | `SP-3.1` | ✅ SATISFIED |
| **OBL-SP-CLOSURE** | **Closure**: All OBL-SP-* must be satisfied for plane closure. | Strategy | TRUE | *All SP Tasks* | ✅ SATISFIED |

### Structural Activation Plane Obligations

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-SA-MACRO** | **Macro State**: Read-only macro context (regime, rates, inflation). | Structural | TRUE | `SA-4.1` | ✅ SATISFIED |
| **OBL-SA-FACTOR** | **Factor State**: Read-only factor exposures as descriptive metadata. | Structural | TRUE | `SA-4.2` | ✅ SATISFIED |
| **OBL-SA-FLOW** | **Flow State**: Raw flow/microstructure observables (optional). | Structural | FALSE | *If Implemented* | ⚪ N/A |
| **OBL-SA-NO-DECISION** | **No-Decision**: No conditional logic on activated state. ABSOLUTE. | Structural | TRUE | *Validator* | ✅ SATISFIED |
| **OBL-SA-CLOSURE** | **Closure**: All OBL-SA-* must be satisfied for plane closure. | Structural | TRUE | *All SA Tasks* | ✅ SATISFIED |

### Macro Integration Obligations (Phase 4.1 Sub-phase)

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-SA-MI-SPEC** | **Specification**: Macro indicators enumerated and defined. | Structural | TRUE | `SA-4.1.1` | 🔴 UNMET |
| **OBL-SA-MI-BIND** | **Binding**: Indicators bound to verified data sources. | Structural | TRUE | `SA-4.1.2` | 🔴 UNMET |
| **OBL-SA-MI-WIRING** | **Wiring**: Macro state wired to decision inputs (Read-Only). | Structural | TRUE | `SA-4.1.3` | 🔴 UNMET |
| **OBL-SA-MI-TRACE** | **Trace**: Macro state observable in all system traces. | Structural | TRUE | `SA-4.1.4` | 🔴 UNMET |

### Scale & Safety Plane Obligations

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-SS-KILLSWITCH** | **Kill-Switch**: Global halt mechanism verified and tested. | Scale & Safety | TRUE | `SS-5.1`, `SS-5.3` | ✅ SATISFIED |
| **OBL-SS-BOUNDS** | **Limits**: Hard limits on strategies, frequency, fan-out enforced. | Scale & Safety | TRUE | `SS-5.1` | ✅ SATISFIED |
| **OBL-SS-DETERMINISM** | **Determinism**: Behavior remains deterministic under load. | Scale & Safety | TRUE | `SS-5.2` | ✅ SATISFIED |
| **OBL-SS-CIRCUIT** | **Circuit Breakers**: Safe degradation and failure isolation. | Scale & Safety | TRUE | `SS-5.2` | ✅ SATISFIED |
| **OBL-SS-AUDIT** | **Audit**: Bounded, governed audit at scale. | Scale & Safety | TRUE | `SS-5.3` | ✅ SATISFIED |
| **OBL-SS-CLOSURE** | **Closure**: All OBL-SS-* must be satisfied for plane closure. | Scale & Safety | TRUE | *All SS Tasks* | ✅ SATISFIED |

### Decision Plane Obligations

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-DE-DECISION-OBJ** | **Decision Objects**: Immutable, versioned decision specs. | Decision | TRUE | `DE-6.1` | ✅ SATISFIED |
| **OBL-DE-HITL** | **HITL Gate**: Human approval required before effect. | Decision | TRUE | `DE-6.2` | ✅ SATISFIED |
| **OBL-DE-SHADOW** | **Shadow Sink**: Paper trading / simulation only. | Decision | TRUE | `DE-6.3` | ✅ SATISFIED |
| **OBL-DE-NO-EXEC** | **No-Execution**: No real broker/market interaction. ABSOLUTE. | Decision | TRUE | *Validator* | ✅ SATISFIED |
| **OBL-DE-AUDIT** | **Audit**: Every decision produces ledger + DID. | Decision | TRUE | `DE-6.4` | ✅ SATISFIED |
| **OBL-DE-CLOSURE** | **Closure**: All OBL-DE-* must be satisfied for plane closure. | Decision | TRUE | *All DE Tasks* | ✅ SATISFIED |

### Evolution Phase Obligations

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-EV-BULK** | **Bulk Availability**: All strategies evaluable without manual wiring. | Evolution | TRUE | `EV-7.1` | ✅ SATISFIED |
| **OBL-EV-VISIBILITY** | **Decision Visibility**: Every decision exposes full context. | Evolution | TRUE | `EV-7.2` | ✅ SATISFIED |
| **OBL-EV-SHADOW-INTEGRITY** | **Shadow Integrity**: Paper execution never affects capital. | Evolution | TRUE | `EV-7.3` | ✅ SATISFIED |
| **OBL-EV-FAILURE-SURFACE** | **Failure Surfacing**: Undefined states explicitly logged. | Evolution | TRUE | `EV-7.4` | ✅ SATISFIED |
| **OBL-EV-COMPARATIVE** | **Comparative Eval**: Side-by-side strategy evaluation. | Evolution | TRUE | `EV-7.5` | ✅ SATISFIED |
| **OBL-EV-FACTOR-CONTEXT** | **Factor Context**: Observational context schema defined & governed. | Evolution | TRUE | `EV-CTX-FACTOR-DESIGN` | ✅ SATISFIED |
| **OBL-EV-CLOSURE** | **Closure**: All OBL-EV-* must be satisfied for closure. | Evolution | TRUE | *All EV Tasks* | ✅ SATISFIED |

### Regime Observability Obligations (EV Sub-phase)

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-RG-SYMBOLS** | **Symbol Availability**: Required symbols enumerated and checked. | Evolution (Regime) | TRUE | `EV-RG-1`, `EV-RG-2` | ✅ SATISFIED |
| **OBL-RG-DEPTH** | **Historical Depth**: Lookback windows satisfiable. | Evolution (Regime) | TRUE | `EV-RG-3` | ✅ SATISFIED |
| **OBL-RG-ALIGNMENT** | **Temporal Alignment**: Symbols align on timestamps. | Evolution (Regime) | TRUE | `EV-RG-4` | ✅ SATISFIED |
| **OBL-RG-VIABILITY** | **State Viability**: Regime state constructible. | Evolution (Regime) | TRUE | `EV-RG-5` | ✅ SATISFIED |
| **OBL-RG-ATTRIBUTION** | **Undefined Attribution**: Every undefined has cause. | Evolution (Regime) | TRUE | `EV-RG-6` | ✅ SATISFIED |
| **OBL-RG-CLOSURE** | **Closure**: All RG-* satisfied for audit closure. | Evolution (Regime) | TRUE | `EV-RG-7` | ✅ SATISFIED |

### Regime Ingestion Obligations (EV Sub-phase)

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-RG-ING-SYMBOLS** | **Contract Symbols**: All Minimal Regime Contract symbols ingested. | Evolution (Regime) | TRUE | *Ingestion Layer* | ✅ SATISFIED |
| **OBL-RG-ING-HISTORY** | **History Depth**: Minimum 3-year lookback satisfied. | Evolution (Regime) | TRUE | *Ingestion Layer* | ✅ SATISFIED |
| **OBL-RG-ING-ALIGNMENT** | **Alignment**: Symbols align on daily timestamps. | Evolution (Regime) | TRUE | *Ingestion Layer* | ✅ SATISFIED |
| **OBL-RG-ING-QUALITY** | **Quality**: No forward-fill or interpolation. | Evolution (Regime) | TRUE | *Ingestion Layer* | ✅ SATISFIED |
| **OBL-RG-ING-ENFORCEMENT** | **Enforcement**: Regime computation gated by data. | Evolution (Regime) | TRUE | *Regime Gate* | ✅ SATISFIED |

### Cross-Plane Obligations

| Obligation ID | Description | Scope | Blocking | Satisfied By | Status |
|:--------------|:------------|:------|:---------|:-------------|:-------|
| **OBL-X-NO-SIDE** | **Purity**: Zero persistent side effects outside of Ledger/Artifacts. | Cross | TRUE | *Validator* | ✅ SATISFIED |
| **OBL-X-USABILITY** | **Usability**: No source-code guessing; clear interfaces/runbooks. | Cross | FALSE | *Skill: Runbooks* | ✅ SATISFIED |

---

## 3. DWBS → Task Coverage Report

### Coverage Matrix

| DWBS Item | DWBS ID | Task Coverage | Status |
|:----------|:--------|:--------------|:-------|
| **CONTROL PLANE** | | | |
| Belief Layer Completion | 4.1.1 | CP-1.1 | ✅ Covered |
| Policy Layer — Factor | 4.1.2 | CP-1.2 | ✅ Covered |
| Policy Layer — Strategy | 4.1.3 | CP-1.3 | ✅ Covered |
| Validator Gatekeeping | 4.1.4 | CP-1.4 | ✅ Covered |
| **ORCHESTRATION PLANE** | | | |
| Task Abstraction | 4.2.1 | OP-2.1 | ✅ Covered |
| Task Graph Model | 4.2.2 | OP-2.2 | ✅ Covered |
| Execution Harness Binding | 4.2.3 | OP-2.3 | ✅ Covered |
| **STRATEGY PLANE** | | | |
| Strategy Mapping | 4.3.1 | SP-3.1 | ✅ Covered |
| Strategy Registry | 4.3.2 | SP-3.2 | ✅ Covered |
| Strategy Lifecycle | 4.3.3 | SP-3.3 | ✅ Covered |
| **STRUCTURAL ACTIVATION PLANE** | | | |
| Macro Layer Activation | 4.4.1 | SA-4.1 | ✅ Covered |
| Factor Layer Activation | 4.4.2 | SA-4.2 | ✅ Covered |
| **SCALE & SAFETY PLANE** | | | |
| Multi-Strategy Coexistence | 4.5.1 | SS-5.1 | ✅ Covered |
| Failure Mode Validation | 4.5.2 | SS-5.2 | ✅ Covered |
| Permission Revocation | 4.5.3 | SS-5.3 | ✅ Covered |

**Coverage:** 14/14 DWBS items (100%)

---

## 3. Task Identification Scheme

**Format:** `<Plane>-<Phase>.<Item>`

| Prefix | Plane |
|:-------|:------|
| CP | Control Plane |
| OP | Orchestration Plane |
| SP | Strategy Plane |
| SA | Structural Activation Plane |
| SS | Scale & Safety Plane |

---

## 4. Control Plane Tasks

**Gate:** Must complete before Orchestration Plane begins.

---

### Task CP-1.1: Belief Layer Completion

| Attribute | Value |
|:----------|:------|
| **Task ID** | CP-1.1 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.1.1 |
| **Plane** | Control |
| **Blocking** | TRUE |
| **Purpose** | Operationalize Belief Layer to produce `BeliefState` objects |
| **Inputs** | `belief_layer_policy.md`, `Regime Layer` |
| **Artifacts** | `src/layers/belief_layer.py` |
| **Impacts** | `docs/architecture/DWBS.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | EH-1, BEL-1 to BEL-6 |
| **Satisfies** | `OBL-CP-BELIEF` |

---

### Task CP-1.2: Factor Policy Layer Operationalization

| Attribute | Value |
|:----------|:------|
| **Task ID** | CP-1.2 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.1.2 |
| **Plane** | Control |
| **Blocking** | TRUE |
| **Purpose** | Operationalize Factor Layer to produce `FactorPermission` objects |
| **Inputs** | `factor_layer_policy.md`, `Regime Layer` |
| **Artifacts** | `src/layers/factor_layer.py` |
| **Impacts** | `docs/epistemic/factor_layer_policy.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | PD-1, FAC-1 to FAC-4 |
| **Satisfies** | `OBL-CP-POLICY` |

---

### Task CP-1.3: Strategy Governance Operationalization

| Attribute | Value |
|:----------|:------|
| **Task ID** | CP-1.3 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.1.3 |
| **Plane** | Control |
| **Blocking** | TRUE |
| **Purpose** | Implement strategy registration and validation rules |
| **Inputs** | `strategy_layer_policy.md` |
| **Artifacts** | `src/governance/strategy_governance.py` |
| **Impacts** | `docs/epistemic/strategy_layer_policy.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | STR-1 to STR-6 |
| **Satisfies** | `OBL-CP-POLICY` |

---

### Task CP-1.4: Validator Integration

| Attribute | Value |
|:----------|:------|
| **Task ID** | CP-1.4 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.1.4 |
| **Plane** | Control |
| **Blocking** | TRUE |
| **Purpose** | Integrate epistemic validator into build/deploy pipeline |
| **Inputs** | `epistemic_validator.py`, CI/CD config |
| **Artifacts** | `.github/workflows/epistemic_check.yml` |
| **Impacts** | `docs/contracts/epistemic_drift_validator_specification.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Self-validating |
| **Satisfies** | `OBL-CP-SAFETY` |

---

### Task CP-1.5: Control Plane Obligation Verification (Closure)

| Attribute | Value |
|:----------|:------|
| **Task ID** | CP-1.5 |
| **Status** | ACTIVE |
| **DWBS Ref** | Meta |
| **Plane** | Control |
| **Blocking** | TRUE |
| **Purpose** | Verify all Control Plane obligations are SATISFIED before closure |
| **Inputs** | `task_graph.md`, `OBL-CP-*` definitions |
| **Artifacts** | `docs/audits/cp_obligation_verification.md` |
| **Impacts** | None |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | Obligation Check |
| **Satisfies** | `OBL-CP-AUDIT` |

---

### Gate: Control Plane Complete

**Ledger Entry Required:** D009 — Control Plane Completion

---

## 5. Orchestration Plane Tasks

**Gate:** Must complete before Strategy Plane begins.

---

### Task OP-2.1: Task Abstraction Definition

| Attribute | Value |
|:----------|:------|
| **Task ID** | OP-2.1 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.2.1 |
| **Plane** | Orchestration |
| **Blocking** | TRUE |
| **Purpose** | Define `TaskSpec` type for harness consumption |
| **Inputs** | `execution_harness_contract.md` |
| **Artifacts** | `src/harness/task_spec.py` |
| **Impacts** | `docs/contracts/execution_harness_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Task validation rules |
| **Satisfies** | `OBL-OP-NO-IMPLICIT` |

---

### Task OP-2.2: Task Graph Model

| Attribute | Value |
|:----------|:------|
| **Task ID** | OP-2.2 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.2.2 |
| **Plane** | Orchestration |
| **Blocking** | TRUE |
| **Purpose** | Implement DAG structure for task sequencing |
| **Inputs** | `OP-2.1` outputs |
| **Artifacts** | `src/harness/task_graph.py` |
| **Impacts** | `docs/epistemic/roadmap/task_graph.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Graph integrity checks |
| **Satisfies** | `OBL-OP-DETERMINISM` |

---

### Task OP-2.3: Execution Harness Binding

| Attribute | Value |
|:----------|:------|
| **Task ID** | OP-2.3 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.2.3 |
| **Plane** | Orchestration |
| **Blocking** | TRUE |
| **Purpose** | Wire harness to Belief, Factor, and Validator layers |
| **Inputs** | `OP-2.1`, `OP-2.2` outputs |
| **Artifacts** | `src/harness/harness.py` |
| **Impacts** | `docs/contracts/execution_harness_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | EH-1, EH-2, EH-3 |
| **Satisfies** | `OBL-OP-HARNESS`, `OBL-OP-VISIBILITY` |

---

### Gate: Orchestration Plane Complete

**Ledger Entry Required:** D010 — Orchestration Plane Completion

---

## 6. Strategy Plane Tasks

**Gate:** Must complete before Structural Activation Plane begins.

---

### Task SP-3.1: Strategy Mapping

| Attribute | Value |
|:----------|:------|
| **Task ID** | SP-3.1 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.3.1 |
| **Plane** | Strategy |
| **Blocking** | TRUE |
| **Purpose** | Map strategy definitions to task graphs |
| **Inputs** | Orchestration Plane outputs |
| **Artifacts** | `src/strategy/strategy_mapping.py` |
| **Impacts** | `docs/epistemic/strategy_layer_policy.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Linkage validation |
| **Satisfies** | `OBL-SP-DECLARATIVE` |

---

### Task SP-3.2: Strategy Registry

| Attribute | Value |
|:----------|:------|
| **Task ID** | SP-3.2 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.3.2 |
| **Plane** | Strategy |
| **Blocking** | TRUE |
| **Purpose** | Implement registry for governed strategy discovery |
| **Inputs** | `SP-3.1` outputs |
| **Artifacts** | `src/strategy/registry.py` |
| **Impacts** | `docs/epistemic/strategy_layer_policy.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | STR-4, STR-5 |
| **Satisfies** | `OBL-SP-REGISTRY` |

---

### Task SP-3.3: Strategy Lifecycle Governance

| Attribute | Value |
|:----------|:------|
| **Task ID** | SP-3.3 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.3.3 |
| **Plane** | Strategy |
| **Blocking** | TRUE |
| **Purpose** | Implement DRAFT → ACTIVE → SUSPENDED → RETIRED machine |
| **Inputs** | `SP-3.2` outputs |
| **Artifacts** | `src/strategy/lifecycle.py` |
| **Impacts** | `docs/epistemic/strategy_layer_policy.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | STR-4, STR-6 |
| **Satisfies** | `OBL-SP-LIFECYCLE` |

---

### Gate: Strategy Plane Complete

**Ledger Entry Required:** D011 — Strategy Plane Completion

---

## 7. Structural Activation Plane Tasks

**Gate:** Must complete before Scale & Safety Plane begins.

---

### Task SA-4.1: Macro Layer Activation

| Attribute | Value |
|:----------|:------|
| **Task ID** | SA-4.1 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.4.1 |
| **Plane** | Structural |
| **Blocking** | FALSE |
| **Purpose** | Promote Macro Layer from latent to referenced |
| **Inputs** | `latent_structural_layers.md` |
| **Artifacts** | `src/layers/macro_layer.py` |
| **Impacts** | `docs/epistemic/latent_structural_layers.md` |
| **Post Hooks** | `decision-ledger-curator`, `evolution-recorder` |
| **Validator** | LD-1, MF-1 |
| **Satisfies** | `OBL-SA-MACRO` |

---

### Task SA-4.1.1: Macro Indicator Specification

| Attribute | Value |
|:----------|:------|
| **Task ID** | SA-4.1.1 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.4.1.1 |
| **Plane** | Structural (Macro Integration) |
| **Blocking** | TRUE |
| **Purpose** | Explicitly enumerate and specify required macro indicators |
| **Inputs** | `minimal_regime_input_contract.md` |
| **Artifacts** | `src/layers/macro/specification.py` |
| **Impacts** | `docs/epistemic/macro_layer_policy.md` |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | MF-1 |
| **Satisfies** | `OBL-SA-MI-SPEC` |

---

### Task SA-4.1.2: Macro Data Source Binding

| Attribute | Value |
|:----------|:------|
| **Task ID** | SA-4.1.2 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.4.1.2 |
| **Plane** | Structural (Macro Integration) |
| **Blocking** | TRUE |
| **Purpose** | Bind specified indicators to verified automated data sources |
| **Inputs** | `SA-4.1.1` outputs, Ingestion metadata |
| **Artifacts** | `src/layers/macro/binding.py` |
| **Impacts** | `docs/epistemic/contracts/minimal_regime_input_contract.md` |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | MF-2 |
| **Satisfies** | `OBL-SA-MI-BIND` |

---

### Task SA-4.1.3: Macro Decision Wiring

| Attribute | Value |
|:----------|:------|
| **Task ID** | SA-4.1.3 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.4.1.3 |
| **Plane** | Structural (Macro Integration) |
| **Blocking** | TRUE |
| **Purpose** | Wire macro state to the Decision Engine inputs (Read-Only) |
| **Inputs** | `SA-4.2.1` outputs, DecisionSpec |
| **Artifacts** | `src/layers/macro/wiring.py` |
| **Impacts** | `docs/epistemic/governance/macro_integration_obligations.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | SA-ND-1 |
| **Satisfies** | `OBL-SA-MI-WIRING` |

---

### Task SA-4.1.4: Macro Observability Trace

| Attribute | Value |
|:----------|:------|
| **Task ID** | SA-4.1.4 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.4.1.4 |
| **Plane** | Structural (Macro Integration) |
| **Blocking** | TRUE |
| **Purpose** | Integrate macro state into Shadow traces and Replay Engine |
| **Inputs** | `SA-4.3.1` outputs, Shadow Sink |
| **Artifacts** | `src/layers/macro/observability.py` |
| **Impacts** | `docs/diagnostics/macro_integration_report.md` |
| **Post Hooks** | `evolution-recorder`, `decision-ledger-curator` |
| **Validator** | SA-ND-2 |
| **Satisfies** | `OBL-SA-MI-TRACE` |

---

### Task SA-4.2: Factor Layer Activation

| Attribute | Value |
|:----------|:------|
| **Task ID** | SA-4.2 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.4.2 |
| **Plane** | Structural |
| **Blocking** | FALSE |
| **Purpose** | Promote Factor Layer to live permissions |
| **Inputs** | `SA-4.1` outputs |
| **Artifacts** | `src/layers/factor_live.py` |
| **Impacts** | `docs/epistemic/factor_layer_policy.md` |
| **Post Hooks** | `decision-ledger-curator`, `evolution-recorder` |
| **Validator** | LD-1, PD-1 |
| **Satisfies** | `OBL-SA-FACTOR` |

---

### Gate: Structural Activation Plane Complete

**Ledger Entry Required:** D012 — Structural Activation Completion

---

## 8. Scale & Safety Plane Tasks

**Gate:** Terminal plane — completion means PRODUCTION READY.

---

### Task SS-5.1: Multi-Strategy Coexistence Rules

| Attribute | Value |
|:----------|:------|
| **Task ID** | SS-5.1 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.5.1 |
| **Plane** | Safety |
| **Blocking** | TRUE |
| **Purpose** | Define rules for shared belief/permission space |
| **Inputs** | Structural Activation outputs |
| **Artifacts** | `docs/epistemic/multi_strategy_policy.md` |
| **Impacts** | `docs/architecture/DWBS.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Conflict detection |
| **Satisfies** | `OBL-SS-BOUNDS`, `OBL-SS-KILLSWITCH` |

---

### Task SS-5.2: Failure Mode Validation

| Attribute | Value |
|:----------|:------|
| **Task ID** | SS-5.2 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.5.2 |
| **Plane** | Safety |
| **Blocking** | TRUE |
| **Purpose** | Implement test coverage for failure isolation |
| **Inputs** | `SS-5.1` outputs |
| **Artifacts** | `tests/failure_modes/` |
| **Impacts** | `docs/operations/end_to_end_runbook.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Test coverage thresholds |
| **Satisfies** | `OBL-SS-CIRCUIT`, `OBL-SS-DETERMINISM` |

---

### Task SS-5.3: Permission Revocation Handling

| Attribute | Value |
|:----------|:------|
| **Task ID** | SS-5.3 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.5.3 |
| **Plane** | Safety |
| **Blocking** | TRUE |
| **Purpose** | Implement mid-execution revocation mechanism |
| **Inputs** | Factor Layer outputs |
| **Artifacts** | `src/harness/revocation.py` |
| **Impacts** | `docs/contracts/execution_harness_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Revocation correctness |
| **Satisfies** | `OBL-SS-KILLSWITCH`, `OBL-SS-AUDIT` |

---

## 9. Decision Plane Tasks

**Gate:** Must complete before Execution Plane can be authorized. **HITL + Shadow only.**

---

### Task DE-6.1: Decision Object Specification

| Attribute | Value |
|:----------|:------|
| **Task ID** | DE-6.1 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.6.1 |
| **Plane** | Decision |
| **Blocking** | TRUE |
| **Purpose** | Define DecisionSpec schema for immutable, versioned decisions |
| **Inputs** | Scale & Safety outputs |
| **Artifacts** | `src/decision/decision_spec.py` |
| **Impacts** | `docs/contracts/decision_plane_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Schema validation |
| **Satisfies** | `OBL-DE-DECISION-OBJ` |

---

### Task DE-6.2: HITL Approval Gate

| Attribute | Value |
|:----------|:------|
| **Task ID** | DE-6.2 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.6.2 |
| **Plane** | Decision |
| **Blocking** | TRUE |
| **Purpose** | Implement Human-in-the-Loop approval interface |
| **Inputs** | `DE-6.1` outputs |
| **Artifacts** | `src/decision/hitl_gate.py` |
| **Impacts** | `docs/operations/approval_workflow.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Approval workflow coverage |
| **Satisfies** | `OBL-DE-HITL` |

---

### Task DE-6.3: Shadow Execution Sink

| Attribute | Value |
|:----------|:------|
| **Task ID** | DE-6.3 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.6.3 |
| **Plane** | Decision |
| **Blocking** | TRUE |
| **Purpose** | Implement paper trading / simulation environment |
| **Inputs** | `DE-6.1`, `DE-6.2` outputs |
| **Artifacts** | `src/decision/shadow_sink.py` |
| **Impacts** | `docs/contracts/shadow_execution_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | No real capital path |
| **Satisfies** | `OBL-DE-SHADOW` |

---

### Task DE-6.4: Decision Audit Wiring

| Attribute | Value |
|:----------|:------|
| **Task ID** | DE-6.4 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.6.4 |
| **Plane** | Decision |
| **Blocking** | TRUE |
| **Purpose** | Wire decision creation to Ledger + DID generation |
| **Inputs** | `DE-6.1` outputs |
| **Artifacts** | `src/decision/audit_integration.py` |
| **Impacts** | `docs/epistemic/ledger/decisions.md` |
| **Post Hooks** | `decision-ledger-curator`, `evolution-recorder` |
| **Validator** | Audit completeness |
| **Satisfies** | `OBL-DE-AUDIT` |

---

### Gate: Decision Plane Complete

**Ledger Entry Required:** D013 — Decision Plane Completion (HITL + Shadow Only)

---

## 10. Evolution Phase Tasks

**Gate:** Learning and debugging phase. No execution. **Shadow + Diagnostics only.**

---

### Task EV-CTX-FACTOR-DESIGN: Factor Context Design

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-CTX-FACTOR-DESIGN |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.4.2 |
| **Plane** | Evolution |
| **Blocking** | TRUE |
| **Purpose** | Define Factor Context schema, binding rules, and DWV integration. |
| **Inputs** | `DWBS.md`, `Regime Context` |
| **Artifacts** | `docs/evolution/context/factor_context_schema.md` |
| **Impacts** | `docs/architecture/DWBS.md` |
| **Post Hooks** | `decision-ledger-curator` |
| **Validator** | Schema Verification |
| **Satisfies** | `OBL-EV-FACTOR-CONTEXT` |

---

### Task EV-RUN-CTX-FACTOR: Factor Context Builder

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RUN-CTX-FACTOR |
| **Status** | SUCCESS |
| **DWBS Ref** | Meta |
| **Plane** | Evolution |
| **Blocking** | TRUE |
| **Purpose** | Compute and bind Factor Context per window for EV-RUN execution. |
| **Inputs** | `EV-RUN-0` (Regime Context) |
| **Artifacts** | `factor_context.json` |
| **Impacts** | `src/evolution/pipeline_runner.py` |
| **Post Hooks** | None |
| **Validator** | Viability Check |
| **Satisfies** | `OBL-EV-FACTOR-CONTEXT` |

---

### Task EV-CTX-FACTOR-V1.1: Factor Context Extension

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-CTX-FACTOR-V1.1 |
| **Status** | SUCCESS |
| **DWBS Ref** | Meta |
| **Plane** | Evolution |
| **Blocking** | TRUE |
| **Purpose** | Extend Factor Context from v1 to v1.1 with higher-resolution observational descriptors. |
| **Inputs** | `EV-CTX-FACTOR-DESIGN` |
| **Artifacts** | `factor_context_schema.md` |
| **Impacts** | `factor_context_builder.py` |
| **Post Hooks** | None |
| **Validator** | Schema Check |
| **Satisfies** | `OBL-EV-FACTOR-CONTEXT-V1.1` |

---

### Task SP-MOMENTUM-VARIANTS: Momentum Strategy Evolution

| Attribute | Value |
|:----------|:------|
| **Task ID** | SP-MOMENTUM-VARIANTS |
| **Status** | SUCCESS |
| **DWBS Ref** | Meta |
| **Plane** | Strategy |
| **Blocking** | TRUE |
| **Purpose** | Register factor-informed Momentum strategy variants. |
| **Inputs** | `EV-CTX-FACTOR-V1.1` |
| **Artifacts** | `src/strategy/registry.py` |
| **Impacts** | `bulk_evaluator.py`, `rejection_analysis.py` |
| **Post Hooks** | None |
| **Validator** | EV-RUN Rejection Analysis |
| **Satisfies** | `OBL-SP-MOMENTUM-EVOLUTION` |

---



### Task EV-7.1: Bulk Strategy Registration

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-7.1 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.7.1 |
| **Plane** | Evolution |
| **Blocking** | TRUE |
| **Purpose** | Enable bulk strategy evaluation without manual wiring |
| **Inputs** | Strategy Registry, Decision Plane |
| **Artifacts** | `src/evolution/bulk_evaluator.py` |
| **Impacts** | `docs/contracts/evolution_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Bulk iteration works |
| **Satisfies** | `OBL-EV-BULK` |

---

### Task EV-7.2: Decision Cycle Replay Engine

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-7.2 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.7.2 |
| **Plane** | Evolution |
| **Blocking** | TRUE |
| **Purpose** | Replay decision cycles in shadow mode |
| **Inputs** | `EV-7.1` outputs, Shadow Sink |
| **Artifacts** | `src/evolution/replay_engine.py` |
| **Impacts** | `docs/operations/replay_runbook.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Replay produces audit trail |
| **Satisfies** | `OBL-EV-VISIBILITY` |

---

### Task EV-7.3: Paper P&L Attribution

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-7.3 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.7.3 |
| **Plane** | Evolution |
| **Blocking** | TRUE |
| **Purpose** | Calculate non-actionable paper P&L per strategy |
| **Inputs** | `EV-7.2` outputs |
| **Artifacts** | `src/evolution/paper_pnl.py` |
| **Impacts** | `docs/diagnostics/pnl_attribution.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | P&L traceable to decisions |
| **Satisfies** | `OBL-EV-SHADOW-INTEGRITY` |

---

### Task EV-7.4: Regime & Factor Coverage Diagnostics

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-7.4 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.7.4 |
| **Plane** | Evolution |
| **Blocking** | TRUE |
| **Purpose** | Diagnose regime coverage and factor alignment |
| **Inputs** | Structural Activation (macro/factor state) |
| **Artifacts** | `src/evolution/coverage_diagnostics.py` |
| **Impacts** | `docs/diagnostics/regime_factor_coverage.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Undefined states surfaced |
| **Satisfies** | `OBL-EV-FAILURE-SURFACE` |

---

### Task EV-7.5: Decision Rejection Analysis

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-7.5 |
| **Status** | SUCCESS |
| **DWBS Ref** | 4.7.5 |
| **Plane** | Evolution |
| **Blocking** | TRUE |
| **Purpose** | Analyze HITL rejections and failure reasons |
| **Inputs** | HITL Gate, Decision Audit |
| **Artifacts** | `src/evolution/rejection_analysis.py` |
| **Impacts** | `docs/diagnostics/rejection_report.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Rejection reasons visible |
| **Satisfies** | `OBL-EV-COMPARATIVE` |

---

### Gate: Evolution Phase Complete

**Ledger Entry Required:** Evolution Phase Completion — Strategy Evaluation Authorized

---

## 10.1 Regime Observability Audit Tasks

**Sub-phase:** Audit-only diagnostic tasks for regime data observability. **No logic changes.**

---

### Task EV-RG-1: Enumerate Regime-Required Symbols

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-1 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Subsystem) |
| **Blocking** | TRUE |
| **Purpose** | List all symbols required for regime classification |
| **Inputs** | Regime definition |
| **Artifacts** | `src/evolution/regime_audit/symbol_enumeration.py` |
| **Impacts** | `docs/diagnostics/regime_symbol_requirements.md` |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | Symbol list complete |
| **Satisfies** | `OBL-RG-SYMBOLS` |

---

### Task EV-RG-2: Ingestion Coverage Audit

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-2 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Subsystem) |
| **Blocking** | TRUE |
| **Purpose** | Audit symbol × time ingestion coverage |
| **Inputs** | `EV-RG-1` outputs, ingestion metadata |
| **Artifacts** | `src/evolution/regime_audit/ingestion_coverage.py` |
| **Impacts** | `docs/diagnostics/regime_coverage_matrix.md` |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | Coverage matrix generated |
| **Satisfies** | `OBL-RG-SYMBOLS` |

---

### Task EV-RG-3: Historical Depth Audit

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-3 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Subsystem) |
| **Blocking** | TRUE |
| **Purpose** | Verify lookback windows are satisfiable |
| **Inputs** | `EV-RG-2` outputs |
| **Artifacts** | `src/evolution/regime_audit/depth_audit.py` |
| **Impacts** | `docs/diagnostics/lookback_sufficiency.md` |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | Sufficiency report generated |
| **Satisfies** | `OBL-RG-DEPTH` |

---

### Task EV-RG-4: Temporal Alignment Audit

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-4 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Subsystem) |
| **Blocking** | TRUE |
| **Purpose** | Verify timestamp alignment across symbols |
| **Inputs** | `EV-RG-2` outputs |
| **Artifacts** | `src/evolution/regime_audit/alignment_audit.py` |
| **Impacts** | `docs/diagnostics/alignment_heatmap.md` |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | Alignment report generated |
| **Satisfies** | `OBL-RG-ALIGNMENT` |

---

### Task EV-RG-5: State Construction Feasibility Check

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-5 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Subsystem) |
| **Blocking** | TRUE |
| **Purpose** | Check if regime state can be constructed |
| **Inputs** | `EV-RG-3`, `EV-RG-4` outputs |
| **Artifacts** | `src/evolution/regime_audit/viability_check.py` |
| **Impacts** | `docs/diagnostics/state_viability.md` |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | Viability determined |
| **Satisfies** | `OBL-RG-VIABILITY` |

---

### Task EV-RG-6: Undefined Regime Attribution Report

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-6 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Subsystem) |
| **Blocking** | TRUE |
| **Purpose** | Attribute every undefined regime to a cause |
| **Inputs** | All EV-RG-* outputs |
| **Artifacts** | `src/evolution/regime_audit/undefined_attribution.py` |
| **Impacts** | `docs/diagnostics/undefined_attribution_table.md` |
| **Post Hooks** | `evolution-recorder`, `decision-ledger-curator` |
| **Validator** | All undefined attributed |
| **Satisfies** | `OBL-RG-ATTRIBUTION` |

---

### Task EV-RG-7: Regime Observability Closure

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-7 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Subsystem) |
| **Blocking** | TRUE |
| **Purpose** | Generate Regime Observability Summary |
| **Inputs** | All EV-RG-* outputs |
| **Artifacts** | `docs/diagnostics/regime_observability_summary.md` |
| **Impacts** | Regime logic tuning eligibility |
| **Post Hooks** | `evolution-recorder` |
| **Validator** | Summary generated, all obligations satisfied |
| **Satisfies** | `OBL-RG-CLOSURE` |

---

### Gate: Regime Observability Complete

**Ledger Entry Required:** Regime Observability Audit Complete — Logic Tuning Eligibility Open

---

## 10.2 Regime Audit Execution Tasks (EV-RG-RUN)

**Sub-phase:** Execute audit modules against ingested data. **Read-only. Repeatable.**

**Relationship:**
- `EV-RG` defines **capability** (audit modules)
- `EV-RG-RUN` performs **execution** (diagnostic artifacts)

**Execution is idempotent and repeatable whenever ingestion changes.**

---

### Task EV-RG-RUN-1: Execute Symbol Enumeration

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-RUN-1 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Execution) |
| **Blocking** | FALSE |
| **Purpose** | Execute symbol enumeration against regime definition |
| **Script** | `src/evolution/regime_audit/symbol_enumeration.py` |
| **Output** | `docs/diagnostics/regime/symbol_coverage_matrix.csv` |
| **Post Hooks** | `evolution-recorder` |
| **Failure If** | Required symbols list is empty |

---

### Task EV-RG-RUN-2: Execute Ingestion Coverage Audit

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-RUN-2 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Execution) |
| **Blocking** | FALSE |
| **Purpose** | Execute ingestion coverage audit against current data |
| **Script** | `src/evolution/regime_audit/ingestion_coverage.py` |
| **Output** | `docs/diagnostics/regime/ingestion_coverage_report.csv` |
| **Post Hooks** | `evolution-recorder` |
| **Failure If** | Zero overlapping timestamps across symbols |

---

### Task EV-RG-RUN-3: Execute Historical Depth Audit

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-RUN-3 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Execution) |
| **Blocking** | FALSE |
| **Purpose** | Execute historical depth audit against ingested history |
| **Script** | `src/evolution/regime_audit/depth_audit.py` |
| **Output** | `docs/diagnostics/regime/lookback_sufficiency_report.md` |
| **Post Hooks** | `evolution-recorder` |
| **Failure If** | Any required lookback window is unsatisfiable |

---

### Task EV-RG-RUN-4: Execute Temporal Alignment Audit

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-RUN-4 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Execution) |
| **Blocking** | FALSE |
| **Purpose** | Execute temporal alignment audit across symbols |
| **Script** | `src/evolution/regime_audit/alignment_audit.py` |
| **Output** | `docs/diagnostics/regime/temporal_alignment_report.md` |
| **Post Hooks** | `evolution-recorder` |
| **Failure If** | Alignment intersection < minimum viable range |

---

### Task EV-RG-RUN-5: Execute State Viability Check

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-RUN-5 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Execution) |
| **Blocking** | FALSE |
| **Purpose** | Execute state viability check |
| **Script** | `src/evolution/regime_audit/viability_check.py` |
| **Output** | `docs/diagnostics/regime/state_viability_report.md` |
| **Post Hooks** | `evolution-recorder` |
| **Failure If** | Regime state cannot be constructed |

---

### Task EV-RG-RUN-6: Execute Undefined Regime Attribution

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-RUN-6 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Execution) |
| **Blocking** | FALSE |
| **Purpose** | Execute undefined regime attribution |
| **Script** | `src/evolution/regime_audit/undefined_attribution.py` |
| **Output** | `docs/diagnostics/regime/undefined_regime_attribution.csv` |
| **Post Hooks** | `evolution-recorder` |
| **Failure If** | Any undefined regime lacks attribution |

---

### Task EV-RG-RUN-7: Compile Regime Diagnostics Bundle

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RG-RUN-7 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Regime Execution) |
| **Blocking** | FALSE |
| **Purpose** | Compile all audit results into single diagnostic bundle |
| **Inputs** | All EV-RG-RUN-1 to EV-RG-RUN-6 outputs |
| **Output** | `docs/diagnostics/regime/regime_diagnostics_bundle.md` |
| **Post Hooks** | `evolution-recorder`, `decision-ledger-curator` |
| **Failure If** | Any upstream audit failed |

---

### Gate: Regime Audit Execution Complete

**Note:** EV-RG-RUN tasks are **non-blocking**. Failures inform next ingestion or logic tasks but do not reopen Strategy or Decision planes.

---

## 11. Legacy Task Reconciliation

Legacy tasks are archived in `docs/archive/task_graph_legacy.md`.

---

## 12. Dependency Graph

```
Control (CP) ──► Orchestration (OP) ──► Strategy (SP) ──► Activation (SA) ──► Safety (SS) ──► Decision (DE) ──► Evolution (EV)
                                                                                                                      │
                                                                                                                      ▼
                                                                                                             Optimization [BLOCKED]
                                                                                                                      │
                                                                                                                      ▼
                                                                                                             Execution (D014) [PERMANENTLY BLOCKED]
```

## 10.3 Evolution Evaluation Execution Tasks (EV-RUN)

**Sub-phase:** Execute Evolution evaluation logic against current data. **Read-only. Repeatable.**

**Relationship:**
- `EV-7.x` defines **capability** (evaluation modules)
- `EV-RUN` performs **execution** (material evaluation artifacts)

**Execution is repeatable whenever data or strategies change.**

### Task EV-RUN-0: Build Regime Context

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RUN-0 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Execution Context) |
| **Blocking** | TRUE |
| **Purpose** | Establish immutable regime context for evaluation |
| **Script** | `src/evolution/regime_context_builder.py` |
| **Output** | `docs/evolution/context/regime_context.json` |
| **Post Hooks** | `evolution-recorder` |
| **Safety** | READ-ONLY |

---

### Task EV-RUN-1: Execute Bulk Strategy Evaluation

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RUN-1 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Execution) |
| **Blocking** | FALSE |
| **Purpose** | Evaluate all registered strategies under current regime |
| **Script** | `src/evolution/bulk_evaluator.py` |
| **Output** | `docs/evolution/evaluation/strategy_activation_matrix.csv` |
| **Post Hooks** | `evolution-recorder` |
| **Safety** | READ-ONLY, SHADOW-ONLY |

---

### Task EV-RUN-2: Execute Decision Replay Engine

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RUN-2 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Execution) |
| **Blocking** | FALSE |
| **Purpose** | Replay full decision lifecycle and generate trace logs |
| **Script** | `src/evolution/decision_replay.py` |
| **Output** | `docs/evolution/evaluation/decision_trace_log.parquet` |
| **Post Hooks** | `evolution-recorder` |
| **Safety** | READ-ONLY, SHADOW-ONLY |

---

### Task EV-RUN-3: Execute Paper P&L Engine

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RUN-3 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Execution) |
| **Blocking** | FALSE |
| **Purpose** | Compute descriptive, non-actionable P&L attribution |
| **Script** | `src/evolution/paper_pnl.py` |
| **Output** | `docs/evolution/evaluation/paper_pnl_summary.csv` |
| **Post Hooks** | `evolution-recorder` |
| **Safety** | READ-ONLY, SHADOW-ONLY |

---

### Task EV-RUN-4: Execute Coverage Diagnostics

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RUN-4 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Execution) |
| **Blocking** | FALSE |
| **Purpose** | Diagnose regime and factor coverage gaps |
| **Script** | `src/evolution/coverage_diagnostics.py` |
| **Output** | `docs/evolution/evaluation/coverage_diagnostics.md` |
| **Post Hooks** | `evolution-recorder` |
| **Safety** | READ-ONLY, SHADOW-ONLY |

---

### Task EV-RUN-5: Execute Rejection Analysis

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RUN-5 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Execution) |
| **Blocking** | FALSE |
| **Purpose** | Analyze reasons for decision rejections |
| **Script** | `src/evolution/rejection_analysis.py` |
| **Output** | `docs/evolution/evaluation/rejection_analysis.csv` |
| **Post Hooks** | `evolution-recorder` |
| **Safety** | READ-ONLY, SHADOW-ONLY |

---

### Task EV-RUN-6: Compile Evolution Evaluation Bundle

| Attribute | Value |
|:----------|:------|
| **Task ID** | EV-RUN-6 |
| **Status** | SUCCESS |
| **Plane** | Evolution (Execution) |
| **Blocking** | FALSE |
| **Purpose** | Aggregate all evaluation artifacts into a single summary |
| **Script** | `src/evolution/compile_bundle.py` |
| **Output** | `docs/evolution/evaluation/evolution_evaluation_bundle.md` |
| **Post Hooks** | `evolution-recorder`, `decision-ledger-curator` |
| **Safety** | READ-ONLY, SHADOW-ONLY |

---

## 11. Configuration & Selectors

The Execution Harness supports the following task selection model:

- `all`: Execute all active tasks in dependency order.
- `range`: `from_task_id` to `to_task_id`.
- `list`: Explicit list of `task_id`s.
- `first_n`: First N available tasks.
- `last_n`: Last N available tasks.

---

## 12. Change Log

| Version | Date | Changes |
|:--------|:-----|:--------|
| 2.1 | 2026-01-24 | Added execution control fields (Status, Blocking, Artifacts, Impacts, Post Hooks). Hardened schema for harness consumption. |
| 2.0 | 2026-01-24 | DWBS-aligned restructure, plane-based organization |
| 1.x | Legacy | Pre-DWBS operational phases (archived) |
