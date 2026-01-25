# Macro Integration Obligations (Phase 4.1)

**Status**: Constitutional — Binding  
**Scope**: Macro Integration / Structural Activation Phase (Phase 4.1)  
**Triggered By**: EV-RG Audit Findings & Phase 4.1 Activation  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the **minimal, enforceable obligations** for the integration of macro indicators into the internal system state. These obligations ensure that macro data is properly specified, sourced, and wired to the decision engine without violating the "No-Decision" guarantee.

**Guiding Principle**: Macro data must be descriptive and observable before it can be used to inform (even shadow) decisions.

---

## 2. Obligation Definitions

### OBL-SA-MI-SPEC: Macro Indicator Specification

```yaml
obligation_id: OBL-SA-MI-SPEC
scope:
  plane: StructuralActivation
  layer: Macro
description: |
  All macro indicators required for regime/factor modeling MUST be:
  
  1. Enumerated explicitly (e.g., QQQ, SPY, VIX, ^TNX, ^TYX, HYG, LQD).
  2. Defined by their role (Equity, Volatility, Rates, Credit).
  3. Mapped to their required lookback windows (e.g., 252d, 756d).
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-SA-MI-BIND: Macro Data Source Binding

```yaml
obligation_id: OBL-SA-MI-BIND
scope:
  plane: StructuralActivation
  layer: Macro
description: |
  Specified macro indicators MUST be bound to verified data sources:
  
  1. No manual data entry allowed.
  2. Every indicator must have an automated ingestion path.
  3. Verification of data availability (symbol presence) as per Minimal Regime Contract.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-SA-MI-WIRING: Decision Engine Wiring

```yaml
obligation_id: OBL-SA-MI-WIRING
scope:
  plane: StructuralActivation
  layer: Macro
description: |
  Macro state MUST be wired to the internal decision engine inputs:
  
  1. Decisions must have a dedicated field for `macro_context`.
  2. State flow must be from Ingestion -> Macro Layer -> Decision Object.
  3. No conditional logic (if macro == X) allowed in the wiring.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-SA-MI-TRACE: Macro Observability Trace

```yaml
obligation_id: OBL-SA-MI-TRACE
scope:
  plane: StructuralActivation
  layer: Macro
description: |
  Macro state MUST be observable in all system traces:
  
  1. Shadow decisions must include the macro state at time of decision.
  2. Audit logs must capture macro indicator values used.
  3. Macro state must be visible in the Decision Replay Engine.
blocking: true
satisfied_by: []
evidence: []
```

---

## 3. Obligation Index Update (Phase 4.1)

| Obligation ID | Description | Blocking | Status |
|:--------------|:------------|:---------|:-------|
| **OBL-SA-MI-SPEC** | Indicators enumerated and specified. | TRUE | 🔴 UNMET |
| **OBL-SA-MI-BIND** | Indicators bound to verified sources. | TRUE | 🔴 UNMET |
| **OBL-SA-MI-WIRING** | Macro state wired to decision inputs. | TRUE | 🔴 UNMET |
| **OBL-SA-MI-TRACE** | Macro state observable in all traces. | TRUE | 🔴 UNMET |

---

## 4. Enforcement Rule: READ-ONLY Activation

Any data activated under Phase 4.1 MUST be handled as **READ-ONLY**. Any code that uses macro data to trigger, filter, or size transactions PRIOR to Phase 6 HITL is a structural violation.

**Diagnostic First Principle**: The first implementation of these wires must produce diagnostics/logs only, with zero effect on the decision outcome field.

---

## 5. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [minimal_regime_input_contract.md](file:///c:/GIT/TraderFund/docs/epistemic/contracts/minimal_regime_input_contract.md) | Data requirements source |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | SA-4.1.x task mappings |
| [macro_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/macro_layer_policy.md) | Permitted usage rules |
