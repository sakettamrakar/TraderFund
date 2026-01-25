# Strategy Plane Obligations

**Status**: Constitutional — Binding  
**Scope**: Strategy Plane (Phase 3)  
**Triggered By**: D011  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the **minimal, enforceable obligations** that must be satisfied before the Strategy Plane can be closed. These obligations ensure:

- Strategies are fully registered and discoverable
- Strategy lifecycle is governed, not ad-hoc
- Strategies contain zero executable logic

---

## 2. Obligation Definitions

### OBL-SP-REGISTRY: Registry Completeness

```yaml
obligation_id: OBL-SP-REGISTRY
scope:
  plane: Strategy
description: |
  Every strategy MUST exist as a registered, versioned, discoverable entity 
  before it can be referenced anywhere in the system.
  
  Requirements:
  - Strategies are stored in a governed registry (not loose files).
  - Each strategy has a unique, stable identifier.
  - Each strategy has explicit version metadata.
  - Strategies are discoverable via registry query (not source inspection).
  
  Unregistered strategies are INVALID and cannot be executed.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Registry query returns metadata for all declared strategies; no orphan strategy references exist.

---

### OBL-SP-LIFECYCLE: Lifecycle Enforcement

```yaml
obligation_id: OBL-SP-LIFECYCLE
scope:
  plane: Strategy
description: |
  Every strategy MUST move through explicit lifecycle states governed by policy:
  
  DRAFT → ACTIVE → SUSPENDED → RETIRED
  
  Requirements:
  - Strategies begin in DRAFT (not directly ACTIVE).
  - Transition from DRAFT to ACTIVE requires explicit governance action.
  - SUSPENDED strategies cannot be executed but can be resumed.
  - RETIRED strategies are permanently invalid.
  - No implicit activation (no "auto-activate on registration").
  
  State transitions are auditable and ledger-tracked.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: All registered strategies have a valid `status` field; no strategy has been activated without a corresponding ledger entry.

---

### OBL-SP-DECLARATIVE: No-Logic-in-Strategy Rule

```yaml
obligation_id: OBL-SP-DECLARATIVE
scope:
  plane: Strategy
description: |
  Strategies are governed intent declarations. They are NOT executable logic.
  
  Strategies MAY declare:
  - Epistemic dependencies (required beliefs)
  - Factor requirements (required permissions)
  - Regime compatibility (permitted regimes)
  - Task graph references (what to execute)
  - Decision ledger references (authorizing decision)
  
  Strategies MAY NOT contain:
  - Signal generation logic
  - Indicator computation
  - Conditional branching
  - Price/volume analysis
  - Execution steps
  - Any function that reads market data
  
  If a strategy contains logic, it is INVALID.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Static analysis of strategy definitions shows zero callable functions, zero imports of market data modules, zero conditional logic.

---

### OBL-SP-CLOSURE: Strategy Plane Closure Discipline

```yaml
obligation_id: OBL-SP-CLOSURE
scope:
  plane: Strategy
description: |
  The Strategy Plane CANNOT be closed (D012 precondition) until:
  - All OBL-SP-* obligations are SATISFIED.
  - All SP-3.x tasks are SUCCESS.
  - At least one strategy is registered in DRAFT state (as proof of registry function).
  
  Plane closure without complete governance is forbidden.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Obligation Index shows all OBL-SP-* = SATISFIED; at least one strategy in registry.

---

## 3. Obligation Index Update

Upon commitment of **D011**, the following obligations become **binding but UNSATISFIED**:

| Obligation ID | Description | Blocking | Status |
|:--------------|:------------|:---------|:-------|
| **OBL-SP-REGISTRY** | All strategies must be registered and discoverable. | TRUE | 🔴 UNMET |
| **OBL-SP-LIFECYCLE** | Strategies must follow governed lifecycle states. | TRUE | 🔴 UNMET |
| **OBL-SP-DECLARATIVE** | Strategies must be pure declarations (no logic). | TRUE | 🔴 UNMET |
| **OBL-SP-CLOSURE** | All above must be satisfied for plane closure. | TRUE | 🔴 UNMET |

These obligations block the transition to the **Structural Activation Plane (D012)**.

---

## 4. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [D011](file:///c:/GIT/TraderFund/docs/impact/2026-01-25__decision__D011_strategy_plane_authorization.md) | Triggering decision |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | Obligation Index location |
| [strategy_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/strategy_layer_policy.md) | Governing policy |
