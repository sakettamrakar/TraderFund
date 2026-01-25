# Evolution Phase Obligations

**Status**: Constitutional — Binding  
**Scope**: Evolution Phase (EV)  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the **blocking obligations** that must be satisfied before the Evolution Phase can be closed. These obligations ensure:

- All registered strategies are evaluable
- Every decision is fully visible
- Shadow execution maintains integrity
- Failures are surfaced, not hidden
- Comparative evaluation is possible

**Guiding Principle**: Evolution is about understanding reality, not forcing performance.

---

## 2. Obligation Definitions

### OBL-EV-BULK: Bulk Strategy Availability

```yaml
obligation_id: OBL-EV-BULK
scope:
  plane: Evolution
description: |
  All registered strategies MUST be evaluable without manual wiring.
  
  Requirements:
  - Strategy Registry exposes all ACTIVE strategies.
  - Each strategy can be fed to Decision Factory.
  - No per-strategy setup required for evaluation.
  - Bulk iteration is supported.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Bulk evaluation loop successfully processes all registered strategies.

---

### OBL-EV-VISIBILITY: End-to-End Decision Visibility

```yaml
obligation_id: OBL-EV-VISIBILITY
scope:
  plane: Evolution
description: |
  Every decision MUST expose:
  
  1. Strategy reference (which strategy produced it)
  2. State snapshot (macro, factor, regime context)
  3. Gate outcomes (HITL approval/rejection)
  4. Rejection reasons (if any)
  5. Shadow execution results (if executed)
  
  Decisions with incomplete visibility are INVALID.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Decision audit trail contains all required fields.

---

### OBL-EV-SHADOW-INTEGRITY: Shadow Execution Integrity

```yaml
obligation_id: OBL-EV-SHADOW-INTEGRITY
scope:
  plane: Evolution
description: |
  Paper/shadow execution MUST:
  
  1. Never affect real capital.
  2. Always produce traceable outcomes.
  3. Be clearly labeled as SHADOW.
  4. Generate audit entries.
  
  Any shadow execution affecting real capital is a CRITICAL FAILURE.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Static analysis confirms zero real capital paths; all shadow results labeled.

---

### OBL-EV-FAILURE-SURFACE: Failure & Undefined State Surfacing

```yaml
obligation_id: OBL-EV-FAILURE-SURFACE
scope:
  plane: Evolution
description: |
  Undefined regimes, missing data, or weak signals MUST be:
  
  1. Explicitly logged (not silently ignored).
  2. Attributable to root causes.
  3. Visible in diagnostic outputs.
  4. Treated as first-class signals.
  
  Suppression of failures is FORBIDDEN.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Failure log shows undefined state entries with cause attribution.

---

### OBL-EV-COMPARATIVE: Comparative Evaluation Readiness

```yaml
obligation_id: OBL-EV-COMPARATIVE
scope:
  plane: Evolution
description: |
  The system MUST support side-by-side evaluation across strategies.
  
  Requirements:
  - Multiple strategies evaluable in same run.
  - Results comparable on same time period.
  - Paper P&L attributable per strategy.
  - No strategy-to-strategy interference.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Comparative evaluation report shows multiple strategy results.

---

### OBL-EV-CTX-REGIME: Immutable Regime Context Enforcement

```yaml
obligation_id: OBL-EV-CTX-REGIME
scope:
  plane: Evolution
description: |
  Evaluation execution MUST consume a single, immutable RegimeContext.
  
  Requirements:
  - Regime IS NOT computed locally by evaluation modules.
  - Regime IS bound once per execution session via EV-RUN-0.
  - Persistence of RegimeContext is MANDATORY for downstream tasks.
  - Mismatch between Context and Execution triggers HARD FAILURE.
blocking: true
satisfied_by: ["EV-RUN-0"]
evidence: ["docs/evolution/context/regime_context.json"]
```

**Checkable By**: Verification pass confirms identical regime labels across all EV-RUN artifacts.

---

### OBL-EV-CLOSURE: Evolution Phase Closure Discipline

```yaml
obligation_id: OBL-EV-CLOSURE
scope:
  plane: Evolution
description: |
  The Evolution Phase CANNOT be closed until:
  
  1. All OBL-EV-* obligations are SATISFIED.
  2. All EV-7.x tasks are SUCCESS.
  3. Bulk strategy evaluation demonstrated.
  4. No execution pathway exists.
  
  This obligation is ABSOLUTE.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Obligation Index shows all OBL-EV-* = SATISFIED.

---

## 3. Obligation Index Update

Upon definition, the following obligations become **binding but UNSATISFIED**:

| Obligation ID | Description | Blocking | Status |
|:--------------|:------------|:---------|:-------|
| **OBL-EV-BULK** | Bulk strategy availability for evaluation. | TRUE | 🟢 SATISFIED |
| **OBL-EV-VISIBILITY** | End-to-end decision visibility. | TRUE | 🟢 SATISFIED |
| **OBL-EV-SHADOW-INTEGRITY** | Shadow execution never affects capital. | TRUE | 🟢 SATISFIED |
| **OBL-EV-FAILURE-SURFACE** | Failures and undefined states surfaced. | TRUE | 🟢 SATISFIED |
| **OBL-EV-COMPARATIVE** | Comparative evaluation readiness. | TRUE | 🟢 SATISFIED |
| **OBL-EV-CTX-REGIME** | Immutable context-bound evaluation. | TRUE | 🟢 SATISFIED |
| **OBL-EV-CLOSURE** | All above satisfied for closure. | TRUE | 🟢 SATISFIED |

### Blocking Statement

These obligations **block**:
- Any future Optimization Phase
- Any Execution Plane authorization (D014)

**Real execution remains permanently forbidden.**

---

## 4. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [evolution_phase_definition.md](file:///c:/GIT/TraderFund/docs/epistemic/governance/evolution_phase_definition.md) | Phase definition |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | EV-x task definitions |
| [DWBS.md](file:///c:/GIT/TraderFund/docs/architecture/DWBS.md) | Architectural binding |
