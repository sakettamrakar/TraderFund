# Decision Plane Obligations

**Status**: Constitutional — Binding  
**Scope**: Decision Plane (DE)  
**Triggered By**: D013  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the **blocking obligations** that must be satisfied before the Decision Plane can be closed. These obligations ensure:

- Decisions exist as first-class objects
- Decisions are auditable
- Decisions cannot act directly
- Real execution remains impossible

**Guiding Principle**: The system may now think, but it must still ask permission or simulate.

---

## 2. Obligation Definitions

### OBL-DE-DECISION-OBJ: Decision Object Formalization

```yaml
obligation_id: OBL-DE-DECISION-OBJ
scope:
  plane: Decision
description: |
  All decisions MUST exist as immutable, versioned decision objects.
  
  A DecisionSpec must include:
  - decision_id (unique, stable)
  - strategy_ref (bound to registered strategy)
  - state_snapshot (macro, factor context at decision time)
  - proposed_action (what the decision recommends)
  - routing (HITL or SHADOW)
  - timestamp (creation time)
  - version (semantic versioning)
  
  Decisions are IMMUTABLE once formed.
  Modification requires a new decision object.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: DecisionSpec schema exists; all decisions conform to schema.

---

### OBL-DE-HITL: Human-in-the-Loop Approval Gate

```yaml
obligation_id: OBL-DE-HITL
scope:
  plane: Decision
description: |
  Decisions routed to HITL require EXPLICIT human approval before
  any downstream effect.
  
  HITL gate must:
  - Present decision details to human operator
  - Require explicit APPROVE / REJECT action
  - Log approval with timestamp and authority
  - Block any effect until approved
  
  Automatic approval is FORBIDDEN.
  Timeout-based approval is FORBIDDEN.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: HITL interface stub exists; approval workflow documented.

---

### OBL-DE-SHADOW: Shadow / Paper Execution Sink

```yaml
obligation_id: OBL-DE-SHADOW
scope:
  plane: Decision
description: |
  Decisions may be executed ONLY in a simulated, non-capital-affecting
  environment.
  
  Shadow execution must:
  - Operate on simulated state only
  - Affect zero real capital
  - Produce audit trail identical to real execution
  - Be clearly labeled as SHADOW
  
  Shadow execution is useful for:
  - Strategy validation
  - Performance measurement
  - Risk estimation
  
  Shadow execution MAY NOT affect real positions.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Shadow sink exists; no connection to real brokers.

---

### OBL-DE-NO-EXEC: No-Execution Guarantee (CRITICAL)

```yaml
obligation_id: OBL-DE-NO-EXEC
scope:
  plane: Decision
description: |
  The system MUST provably prevent:
  
  1. Broker API calls
  2. Order placement
  3. Capital movement
  4. Position modification
  5. Any market interaction
  
  This obligation is ABSOLUTE and non-negotiable.
  
  Verification requires:
  - Static analysis showing no broker imports
  - No network calls to trading endpoints
  - No API keys or credentials loaded
  
  Violation of this obligation invalidates the entire Decision Plane.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Static analysis confirms zero broker/trading code paths.

---

### OBL-DE-AUDIT: Decision Auditability

```yaml
obligation_id: OBL-DE-AUDIT
scope:
  plane: Decision
description: |
  Every decision MUST produce:
  
  1. Ledger entry (creation, routing, approval/rejection)
  2. DID artifact (linked to strategy and state)
  3. Strategy traceability (which strategy produced this)
  4. State traceability (what state was observed)
  5. Outcome traceability (what happened to this decision)
  
  Decisions without audit trail are INVALID.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Decision creation produces ledger entry; DID artifact exists.

---

### OBL-DE-CLOSURE: Decision Plane Closure Discipline

```yaml
obligation_id: OBL-DE-CLOSURE
scope:
  plane: Decision
description: |
  The Decision Plane CANNOT be closed (D014 precondition) until:
  
  1. All OBL-DE-* obligations are SATISFIED.
  2. All DE-6.x tasks are SUCCESS.
  3. No real execution pathway exists.
  4. HITL and SHADOW sinks are operational.
  5. Static analysis confirms no broker code.
  
  This obligation is ABSOLUTE.
  
  D014 (Execution Plane) CANNOT be defined until DE closure is proven.
blocking: true
satisfied_by: []
evidence: []
```

**Checkable By**: Obligation Index shows all OBL-DE-* = SATISFIED; verification report attached.

---

## 3. Obligation Index Update

Upon commitment of **D013**, the following obligations become **binding but UNSATISFIED**:

| Obligation ID | Description | Blocking | Status |
|:--------------|:------------|:---------|:-------|
| **OBL-DE-DECISION-OBJ** | Decisions as immutable, versioned objects. | TRUE | 🔴 UNMET |
| **OBL-DE-HITL** | Human-in-the-Loop approval gate. | TRUE | 🔴 UNMET |
| **OBL-DE-SHADOW** | Shadow/paper execution sink. | TRUE | 🔴 UNMET |
| **OBL-DE-NO-EXEC** | No real execution pathway. ABSOLUTE. | TRUE | 🔴 UNMET |
| **OBL-DE-AUDIT** | Every decision produces ledger + DID. | TRUE | 🔴 UNMET |
| **OBL-DE-CLOSURE** | All above must be satisfied for closure. | TRUE | 🔴 UNMET |

### Blocking Statement

These obligations **absolutely block**:
- D014 (Execution Plane Authorization)
- Any broker connectivity
- Any real capital movement
- Any production trading

**No system may execute until choice formation is governed and auditable.**

---

## 4. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [D013](file:///c:/GIT/TraderFund/docs/impact/2026-01-25__decision__D013_decision_plane_authorization.md) | Triggering decision |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | Obligation Index + DE tasks |
| [DWBS.md](file:///c:/GIT/TraderFund/docs/architecture/DWBS.md) | Architectural binding |
| [strategy_registry_schema.md](file:///c:/GIT/TraderFund/docs/contracts/strategy_registry_schema.md) | Strategy linkage |
