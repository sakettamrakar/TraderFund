# Evolution Phase Definition

**Status**: Constitutional — Binding  
**Scope**: Evolution Phase (EV)  
**Date**: 2026-01-25

---

## 1. Purpose

The Evolution Phase exists to **evaluate, compare, and debug strategies** using shadow execution and full auditability.

**Guiding Principle**: Evolution is about understanding reality, not forcing performance.

---

## 2. Core Definitions

### What Evolution IS

| Aspect | Definition |
|:-------|:-----------|
| **Descriptive** | Outputs describe what happened, not what should happen. |
| **Non-Prescriptive** | No actions are recommended or executed. |
| **Failure-First** | Failures are first-class signals, not errors to hide. |
| **Learning-Oriented** | Every run produces insights, not trades. |

### What Evolution IS NOT

| Prohibited | Rationale |
|:-----------|:----------|
| **Execution** | Real execution is permanently forbidden. |
| **Optimization** | Strategies are evaluated, not tuned. |
| **Auto-Selection** | No strategy ranking for deployment. |
| **Performance Forcing** | Poor results are surfaced, not fixed. |

---

## 3. Relationship to Other Planes

```
Decision Plane (D013)
       │
       ▼
Evolution Phase (EV)  ◄── YOU ARE HERE
       │
       ▼
[Future: Optimization Phase] ← BLOCKED until EV closure
       │
       ▼
[Future: Execution Plane (D014)] ← PERMANENTLY BLOCKED
```

Evolution Phase **depends on** Decision Plane outputs:
- DecisionSpec objects
- Shadow execution sink
- HITL approval gate
- Audit integration

Evolution Phase **produces**:
- Paper P&L attribution
- Regime coverage analysis
- Factor alignment diagnostics
- Decision rejection analysis
- Comparative strategy evaluation

---

## 4. Outputs

### 4.1 Paper P&L (Non-Actionable)

Paper P&L is a **diagnostic metric**, not a performance signal.

| Property | Value |
|:---------|:------|
| **Real Capital Impact** | ZERO |
| **Actionability** | NONE (for information only) |
| **Purpose** | Debug strategy logic, not measure returns |

### 4.2 Diagnostic Outputs

| Diagnostic | Purpose |
|:-----------|:--------|
| **Regime Coverage** | Which regimes does this strategy address? |
| **Factor Alignment** | Does factor exposure match strategy intent? |
| **Decision Rejection Reasons** | Why were decisions rejected by HITL? |
| **Undefined State Surfacing** | Where is data missing or ambiguous? |

### 4.3 Failure Signals

| Signal | Treatment |
|:-------|:----------|
| **Regime = UNDEFINED** | First-class log entry, attributed to cause |
| **Missing Macro Data** | Explicit gap flagged |
| **Weak Signal** | Surfaced, not suppressed |
| **Strategy Error** | Captured with full context |

---

## 5. Explicit Prohibitions

The following are **permanently forbidden** in the Evolution Phase:

1. ❌ Real market execution
2. ❌ Broker connectivity
3. ❌ Capital deployment
4. ❌ Strategy optimization
5. ❌ Auto-selection for production
6. ❌ Suppression of failures
7. ❌ Hiding undefined states

---

## 6. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [D013](file:///c:/GIT/TraderFund/docs/impact/2026-01-25__decision__D013_decision_plane_authorization.md) | Prerequisite decision |
| [DWBS.md](file:///c:/GIT/TraderFund/docs/architecture/DWBS.md) | Architectural binding |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | EV-x task definitions |
