# Regime Observability Obligations

**Status**: Constitutional — Binding  
**Scope**: Evolution Phase (EV) — Regime Subsystem  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the **blocking obligations** for regime observability. These ensure:

- Required symbols are known and present
- Historical depth is sufficient
- Temporal alignment exists
- State construction is viable
- Every undefined regime is attributed

**Guiding Principle**: You cannot debug logic until you prove the data can support it.

---

## 2. Obligation Definitions

### OBL-RG-SYMBOLS: Required Symbol Availability

```yaml
obligation_id: OBL-RG-SYMBOLS
scope:
  plane: Evolution
  subsystem: Regime
description: |
  All symbols required for regime classification MUST be:
  
  1. Enumerated explicitly.
  2. Checked for presence/absence.
  3. Reported with availability status.
  
  Missing symbols are first-class diagnostic outputs.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-DEPTH: Historical Depth Sufficiency

```yaml
obligation_id: OBL-RG-DEPTH
scope:
  plane: Evolution
  subsystem: Regime
description: |
  Required lookback windows MUST be:
  
  1. Defined for each regime input.
  2. Checked against available history.
  3. Reported as satisfiable or insufficient.
  
  Gaps must be identified with start/end timestamps.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-ALIGNMENT: Temporal Alignment

```yaml
obligation_id: OBL-RG-ALIGNMENT
scope:
  plane: Evolution
  subsystem: Regime
description: |
  Symbols MUST align on timestamps:
  
  1. Intersection of available timestamps computed.
  2. Misalignments identified.
  3. Missing intersections surfaced.
  
  Misalignment is a cause of undefined regime.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-VIABILITY: State Construction Viability

```yaml
obligation_id: OBL-RG-VIABILITY
scope:
  plane: Evolution
  subsystem: Regime
description: |
  Regime state construction viability MUST be verified:
  
  1. All required inputs present.
  2. All lookback windows satisfiable.
  3. All temporal alignments valid.
  
  If not viable, explicit failure reason required.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-ATTRIBUTION: Undefined Regime Attribution

```yaml
obligation_id: OBL-RG-ATTRIBUTION
scope:
  plane: Evolution
  subsystem: Regime
description: |
  Every regime = undefined MUST have a cause:
  
  - MISSING_SYMBOL
  - INSUFFICIENT_HISTORY
  - TEMPORAL_MISALIGNMENT
  - INVALID_STATE
  - COMPUTATION_ERROR
  
  Unattributed undefined regimes are INVALID.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-CLOSURE: Regime Observability Closure

```yaml
obligation_id: OBL-RG-CLOSURE
scope:
  plane: Evolution
  subsystem: Regime
description: |
  Regime Observability Audit CANNOT be closed until:
  
  1. All OBL-RG-* obligations are SATISFIED.
  2. All EV-RG-x tasks are SUCCESS.
  3. Regime Observability Summary is generated.
  
  This obligation blocks any regime logic tuning.
blocking: true
satisfied_by: []
evidence: []
```

---

## 3. Obligation Index

| Obligation ID | Description | Blocking | Status |
|:--------------|:------------|:---------|:-------|
| **OBL-RG-SYMBOLS** | Required symbols enumerated and checked. | TRUE | 🔴 UNMET |
| **OBL-RG-DEPTH** | Historical depth sufficiency verified. | TRUE | 🔴 UNMET |
| **OBL-RG-ALIGNMENT** | Temporal alignment verified. | TRUE | 🔴 UNMET |
| **OBL-RG-VIABILITY** | State construction viability checked. | TRUE | 🔴 UNMET |
| **OBL-RG-ATTRIBUTION** | Every undefined attributed. | TRUE | 🔴 UNMET |
| **OBL-RG-CLOSURE** | All above for closure. | TRUE | 🔴 UNMET |

---

## 4. Blocking Statement

These obligations **block**:
- Any regime logic tuning
- Any threshold modification
- Evolution Phase closure (for regime subsystem)

**Regime logic modification is forbidden until data observability is proven.**
