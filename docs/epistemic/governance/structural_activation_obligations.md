# Structural Activation Plane Obligations

**Status**: Constitutional — Binding  
**Scope**: Structural Activation Plane (Phase 4)  
**Triggered By**: D012  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the **minimal, enforceable obligations** that must be satisfied before the Structural Activation Plane can be closed. These obligations ensure:

- Runtime state is available
- Runtime state is observable
- **Runtime state cannot be used to decide or act**

This is the most safety-critical plane in the architecture.

---

## 2. Obligation Definitions

### OBL-SA-MACRO: Macro State Availability (Read-Only)

```yaml
obligation_id: OBL-SA-MACRO
scope:
  plane: StructuralActivation
description: |
  Macro-level context (regime, rates, inflation proxies) may be present
  as IMMUTABLE state snapshots.
  
  Permitted:
  - Read current regime label
  - Read rate environment classification
  - Read macro indicator values
  
  Forbidden:
  - Produce signals from macro state
  - Label opportunities based on macro
  - Rank or score assets using macro
  - Apply conditional logic to macro values
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Static analysis confirms no function reads macro state and produces signals, scores, or rankings.

---

### OBL-SA-FACTOR: Factor Exposure Availability (Read-Only)

```yaml
obligation_id: OBL-SA-FACTOR
scope:
  plane: StructuralActivation
description: |
  Factor definitions and exposures may be observable as DESCRIPTIVE
  metadata only.
  
  Permitted:
  - Read factor exposure values
  - Read factor permission status
  - Read factor metadata (name, type, source)
  
  Forbidden:
  - Score securities by factor exposure
  - Trigger allocations based on factors
  - Drive selection using factor values
  - Rank assets by factor score
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Static analysis confirms no function reads factor data and produces allocation, selection, or ranking outputs.

---

### OBL-SA-FLOW: Flow/Microstructure Observability (Read-Only, Optional)

```yaml
obligation_id: OBL-SA-FLOW
scope:
  plane: StructuralActivation
description: |
  Flow or microstructure data may be surfaced as RAW OBSERVABLES.
  
  Permitted:
  - Read volume metrics
  - Read spread metrics
  - Read flow indicators (if declared)
  
  Forbidden:
  - Infer intent from flow data
  - Predict price movement
  - Generate trade signals
  - Apply pattern recognition
blocking: false  # Optional capability
satisfied_by: []
evidence: []
```

**Checkable By**: If implemented, static analysis confirms no function reads flow data and produces signals or predictions.

---

### OBL-SA-NO-DECISION: No-Decision Guarantee (CRITICAL)

```yaml
obligation_id: OBL-SA-NO-DECISION
scope:
  plane: StructuralActivation
description: |
  The system MUST provably guarantee that:
  
  1. No conditional logic is applied to activated state.
  2. No activated state feeds strategy execution.
  3. No activated state results in action.
  4. No activated state produces decision-ready outputs.
  
  This obligation is ABSOLUTE and non-negotiable.
  
  Violation of this obligation invalidates the entire Structural
  Activation Plane and requires rollback.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: 
- Code review confirms no `if/else/switch` on activated state values.
- No function chain from state readers to execution harness.
- Validator rule SA-ND-1 passes.

---

### OBL-SA-CLOSURE: Structural Activation Plane Closure Discipline

```yaml
obligation_id: OBL-SA-CLOSURE
scope:
  plane: StructuralActivation
description: |
  The Structural Activation Plane CANNOT be closed (D013 precondition) until:
  
  1. All OBL-SA-* obligations are SATISFIED.
  2. All SA-4.x tasks are SUCCESS.
  3. No execution pathways exist from state to action.
  4. Read-only guarantees are validated by static analysis.
  
  Plane closure without complete safety validation is forbidden.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Obligation Index shows all OBL-SA-* = SATISFIED; static analysis report attached.

---

## 3. Obligation Index Update

Upon commitment of **D012**, the following obligations become **binding but UNSATISFIED**:

| Obligation ID | Description | Blocking | Status |
|:--------------|:------------|:---------|:-------|
| **OBL-SA-MACRO** | Macro state available as read-only snapshots. | TRUE | 🔴 UNMET |
| **OBL-SA-FACTOR** | Factor exposures available as descriptive metadata. | TRUE | 🔴 UNMET |
| **OBL-SA-FLOW** | Flow/microstructure data as raw observables. | FALSE | 🔴 UNMET |
| **OBL-SA-NO-DECISION** | No decision logic applied to activated state. | TRUE | 🔴 UNMET |
| **OBL-SA-CLOSURE** | All above must be satisfied for plane closure. | TRUE | 🔴 UNMET |

These obligations block the transition to the **Scale & Safety Plane (D013)**.

**Critical Safety Invariant**: No transition to any execution-capable plane is possible until `OBL-SA-NO-DECISION` is verified.

---

## 4. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [D012](file:///c:/GIT/TraderFund/docs/impact/2026-01-25__decision__D012_structural_activation_authorization.md) | Triggering decision |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | Obligation Index location |
| [latent_structural_layers.md](file:///c:/GIT/TraderFund/docs/epistemic/latent_structural_layers.md) | Layer definitions |
| [factor_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/factor_layer_policy.md) | Factor policy constraints |
