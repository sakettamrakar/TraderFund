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
| **OBL-OP-HARNESS** | **Binding**: Harness must bind to Belief/Policy layers (no mock execution). | Orchestration | TRUE | `OP-2.3` | 🔴 UNMET |
| **OBL-SP-GOVERNANCE** | **Lifecycle**: Strategies must be registered and status-managed (no ad-hoc). | Strategy | TRUE | `SP-3.2`, `SP-3.3` | 🔴 UNMET |
| **OBL-SS-SAFETY** | **Isolation**: Failure of one strategy must not crash the system. | Safety | TRUE | `SS-5.2` | 🔴 UNMET |
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
| **Status** | ACTIVE |
| **DWBS Ref** | 4.2.1 |
| **Plane** | Orchestration |
| **Blocking** | TRUE |
| **Purpose** | Define `TaskSpec` type for harness consumption |
| **Inputs** | `execution_harness_contract.md` |
| **Artifacts** | `src/harness/task_spec.py` |
| **Impacts** | `docs/contracts/execution_harness_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Task validation rules |

---

### Task OP-2.2: Task Graph Model

| Attribute | Value |
|:----------|:------|
| **Task ID** | OP-2.2 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.2.2 |
| **Plane** | Orchestration |
| **Blocking** | TRUE |
| **Purpose** | Implement DAG structure for task sequencing |
| **Inputs** | `OP-2.1` outputs |
| **Artifacts** | `src/harness/task_graph.py` |
| **Impacts** | `docs/epistemic/roadmap/task_graph.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Graph integrity checks |

---

### Task OP-2.3: Execution Harness Binding

| Attribute | Value |
|:----------|:------|
| **Task ID** | OP-2.3 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.2.3 |
| **Plane** | Orchestration |
| **Blocking** | TRUE |
| **Purpose** | Wire harness to Belief, Factor, and Validator layers |
| **Inputs** | `OP-2.1`, `OP-2.2` outputs |
| **Artifacts** | `src/harness/harness.py` |
| **Impacts** | `docs/contracts/execution_harness_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | EH-1, EH-2, EH-3 |
| **Satisfies** | `OBL-OP-HARNESS` |

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
| **Status** | ACTIVE |
| **DWBS Ref** | 4.3.1 |
| **Plane** | Strategy |
| **Blocking** | TRUE |
| **Purpose** | Map strategy definitions to task graphs |
| **Inputs** | Orchestration Plane outputs |
| **Artifacts** | `src/strategy/strategy_mapping.py` |
| **Impacts** | `docs/epistemic/strategy_layer_policy.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Linkage validation |

---

### Task SP-3.2: Strategy Registry

| Attribute | Value |
|:----------|:------|
| **Task ID** | SP-3.2 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.3.2 |
| **Plane** | Strategy |
| **Blocking** | TRUE |
| **Purpose** | Implement registry for governed strategy discovery |
| **Inputs** | `SP-3.1` outputs |
| **Artifacts** | `src/strategy/registry.py` |
| **Impacts** | `docs/epistemic/strategy_layer_policy.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | STR-4, STR-5 |
| **Satisfies** | `OBL-SP-GOVERNANCE` |

---

### Task SP-3.3: Strategy Lifecycle Governance

| Attribute | Value |
|:----------|:------|
| **Task ID** | SP-3.3 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.3.3 |
| **Plane** | Strategy |
| **Blocking** | TRUE |
| **Purpose** | Implement DRAFT → ACTIVE → SUSPENDED → RETIRED machine |
| **Inputs** | `SP-3.2` outputs |
| **Artifacts** | `src/strategy/lifecycle.py` |
| **Impacts** | `docs/epistemic/strategy_layer_policy.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | STR-4, STR-6 |
| **Satisfies** | `OBL-SP-GOVERNANCE` |

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
| **Status** | ACTIVE |
| **DWBS Ref** | 4.4.1 |
| **Plane** | Structural |
| **Blocking** | FALSE |
| **Purpose** | Promote Macro Layer from latent to referenced |
| **Inputs** | `latent_structural_layers.md` |
| **Artifacts** | `src/layers/macro_layer.py` |
| **Impacts** | `docs/epistemic/latent_structural_layers.md` |
| **Post Hooks** | `decision-ledger-curator`, `evolution-recorder` |
| **Validator** | LD-1, MF-1 |

---

### Task SA-4.2: Factor Layer Activation

| Attribute | Value |
|:----------|:------|
| **Task ID** | SA-4.2 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.4.2 |
| **Plane** | Structural |
| **Blocking** | FALSE |
| **Purpose** | Promote Factor Layer to live permissions |
| **Inputs** | `SA-4.1` outputs |
| **Artifacts** | `src/layers/factor_live.py` |
| **Impacts** | `docs/epistemic/factor_layer_policy.md` |
| **Post Hooks** | `decision-ledger-curator`, `evolution-recorder` |
| **Validator** | LD-1, PD-1 |

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
| **Status** | ACTIVE |
| **DWBS Ref** | 4.5.1 |
| **Plane** | Safety |
| **Blocking** | TRUE |
| **Purpose** | Define rules for shared belief/permission space |
| **Inputs** | Structural Activation outputs |
| **Artifacts** | `docs/epistemic/multi_strategy_policy.md` |
| **Impacts** | `docs/architecture/DWBS.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Conflict detection |

---

### Task SS-5.2: Failure Mode Validation

| Attribute | Value |
|:----------|:------|
| **Task ID** | SS-5.2 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.5.2 |
| **Plane** | Safety |
| **Blocking** | TRUE |
| **Purpose** | Implement test coverage for failure isolation |
| **Inputs** | `SS-5.1` outputs |
| **Artifacts** | `tests/failure_modes/` |
| **Impacts** | `docs/operations/end_to_end_runbook.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Test coverage thresholds |
| **Satisfies** | `OBL-SS-SAFETY` |

---

### Task SS-5.3: Permission Revocation Handling

| Attribute | Value |
|:----------|:------|
| **Task ID** | SS-5.3 |
| **Status** | ACTIVE |
| **DWBS Ref** | 4.5.3 |
| **Plane** | Safety |
| **Blocking** | TRUE |
| **Purpose** | Implement mid-execution revocation mechanism |
| **Inputs** | Factor Layer outputs |
| **Artifacts** | `src/harness/revocation.py` |
| **Impacts** | `docs/contracts/execution_harness_contract.md` |
| **Post Hooks** | `evolution-recorder`, `drift-detector` |
| **Validator** | Revocation correctness |

---

## 9. Legacy Task Reconciliation

Legacy tasks are archived in `docs/archive/task_graph_legacy.md`.

---

## 10. Dependency Graph

```
Control Plane (CP) ──► Orchestration Plane (OP) ──► Strategy Plane (SP) ──► Activation (SA) ──► Safety (SS)
```

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
