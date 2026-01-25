# Regime Observability Audit Definition

**Status**: Constitutional — Binding  
**Scope**: Evolution Phase (EV) — Regime Subsystem  
**Date**: 2026-01-25

---

## 1. Purpose

The Regime Observability Audit exists to **determine whether regime classification is logically invalid or data-starved/misaligned**.

**Guiding Principle**: You cannot debug logic until you prove the data can support it.

---

## 2. Core Definitions

### What This Audit IS

| Aspect | Definition |
|:-------|:-----------|
| **Diagnostic** | Produces reports, not fixes. |
| **Read-Only** | Does not modify data or logic. |
| **Failure-First** | `undefined` regime is a first-class signal. |
| **Attribution-Focused** | Every `undefined` must have a cause. |

### What This Audit IS NOT

| Prohibited | Rationale |
|:-----------|:----------|
| **Regime Tuning** | Logic modification forbidden. |
| **Data Backfill** | Silent gap-filling forbidden. |
| **Threshold Changes** | Parameter modification forbidden. |
| **Symbol Addition** | Universe expansion out of scope. |

---

## 3. Audit Dimensions

### 3.1 Symbol Availability

| Question | Output |
|:---------|:-------|
| What symbols does regime require? | Symbol enumeration |
| Which are present/absent? | Coverage matrix |
| What is the impact of missing symbols? | Gap impact report |

### 3.2 Historical Depth

| Question | Output |
|:---------|:-------|
| What lookback windows does regime need? | Window requirements |
| Are they satisfiable with current data? | Sufficiency report |
| Where are gaps? | Gap location report |

### 3.3 Temporal Alignment

| Question | Output |
|:---------|:-------|
| Do symbols align on timestamps? | Alignment matrix |
| Where are misalignments? | Misalignment report |
| What intersections are missing? | Intersection gaps |

### 3.4 State Construction Viability

| Question | Output |
|:---------|:-------|
| Are inputs sufficient for regime state? | Viability check |
| What prevents state construction? | Failure reasons |

### 3.5 Undefined Attribution

| Question | Output |
|:---------|:-------|
| Why is regime = undefined? | Attribution table |
| What is the root cause? | Cause categorization |

---

## 4. Undefined Regime Causes

Every `regime = undefined` must be attributed to one of:

| Cause Code | Description |
|:-----------|:------------|
| **MISSING_SYMBOL** | Required symbol not ingested. |
| **INSUFFICIENT_HISTORY** | Lookback window not satisfiable. |
| **TEMPORAL_MISALIGNMENT** | Symbols not aligned on timestamp. |
| **INVALID_STATE** | Inputs present but state invalid. |
| **COMPUTATION_ERROR** | Logic error (requires code inspection). |

---

## 5. Explicit Prohibitions

The following are **forbidden** in this audit:

1. ❌ Modifying regime logic
2. ❌ Changing thresholds
3. ❌ Adding symbols to universe
4. ❌ Backfilling data silently
5. ❌ Suppressing undefined states
6. ❌ Auto-fixing gaps

---

## 6. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [evolution_phase_definition.md](file:///c:/GIT/TraderFund/docs/epistemic/governance/evolution_phase_definition.md) | Parent phase |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | EV-RG-x task definitions |
