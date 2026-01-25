# Regime Ingestion Obligations

**Status**: Constitutional — Binding  
**Scope**: Evolution Phase (EV) — Regime Ingestion Subsystem  
**Date**: 2026-01-25

---

## 1. Purpose

This document defines the **blocking obligations** for regime data ingestion. These ensure:

- All required symbols are ingested
- Historical depth is sufficient
- Temporal alignment exists
- Data quality is maintained
- Regime computation is blocked unless satisfied

**Guiding Principle**: A regime that runs on incomplete data is worse than no regime at all.

---

## 2. Obligation Definitions

### OBL-RG-ING-SYMBOLS: Required Symbol Availability

```yaml
obligation_id: OBL-RG-ING-SYMBOLS
scope:
  plane: Evolution
  subsystem: RegimeIngestion
description: |
  All symbols in the Minimal Regime Input Contract MUST be ingested:
  
  - SPY (S&P 500 ETF)
  - QQQ (NASDAQ 100 ETF)
  - VIX (Volatility Index)
  - ^TNX (10-Year Treasury)
  - ^TYX (30-Year Treasury)
  - HYG (High Yield Credit)
  - LQD (Investment Grade Credit)
  
  Missing symbols → regime NOT_VIABLE.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-ING-HISTORY: Historical Depth Sufficiency

```yaml
obligation_id: OBL-RG-ING-HISTORY
scope:
  plane: Evolution
  subsystem: RegimeIngestion
description: |
  All required symbols MUST satisfy the minimum lookback window:
  
  - Minimum: ≥ 756 trading days (3 years)
  - Recommended: ≥ 1260 trading days (5 years)
  
  Insufficient history → regime NOT_VIABLE.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-ING-ALIGNMENT: Temporal Alignment

```yaml
obligation_id: OBL-RG-ING-ALIGNMENT
scope:
  plane: Evolution
  subsystem: RegimeIngestion
description: |
  All required symbols MUST align on timestamps with sufficient overlap:
  
  - Regime computed only on intersection of timestamps.
  - Minimum overlap: ≥ 756 trading days.
  
  Misalignment → excluded from regime computation.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-ING-QUALITY: Data Quality

```yaml
obligation_id: OBL-RG-ING-QUALITY
scope:
  plane: Evolution
  subsystem: RegimeIngestion
description: |
  Regime input data MUST meet quality standards:
  
  - No forward-filled values.
  - No interpolated values.
  - No synthetic gap-bridging.
  - Daily bar data only.
  
  Quality violations → regime NOT_VIABLE.
blocking: true
satisfied_by: []
evidence: []
```

---

### OBL-RG-ING-ENFORCEMENT: Regime Computation Gate

```yaml
obligation_id: OBL-RG-ING-ENFORCEMENT
scope:
  plane: Evolution
  subsystem: RegimeIngestion
description: |
  Regime computation MUST be blocked unless ALL above obligations are satisfied:
  
  - OBL-RG-ING-SYMBOLS: SATISFIED
  - OBL-RG-ING-HISTORY: SATISFIED
  - OBL-RG-ING-ALIGNMENT: SATISFIED
  - OBL-RG-ING-QUALITY: SATISFIED
  
  If ANY obligation is UNSATISFIED:
  - Regime computation is FORBIDDEN.
  - Regime state MUST be NOT_VIABLE or UNDEFINED.
blocking: true
satisfied_by: []
evidence: []
```

---

## 3. Obligation Index

| Obligation ID | Description | Blocking | Status |
|:--------------|:------------|:---------|:-------|
| **OBL-RG-ING-SYMBOLS** | All contract symbols ingested. | TRUE | 🔴 UNMET |
| **OBL-RG-ING-HISTORY** | Minimum lookback satisfied. | TRUE | 🔴 UNMET |
| **OBL-RG-ING-ALIGNMENT** | Temporal alignment verified. | TRUE | 🔴 UNMET |
| **OBL-RG-ING-QUALITY** | Data quality verified. | TRUE | 🔴 UNMET |
| **OBL-RG-ING-ENFORCEMENT** | Regime computation gated. | TRUE | 🔴 UNMET |

---

## 4. Binding Statement

These obligations **bind**:

| Component | Effect |
|:----------|:-------|
| **Regime Computation** | BLOCKED until all satisfied |
| **EV-RG-RUN Audits** | Must verify contract compliance |
| **Decision Plane** | Must not use incomplete regime state |
| **Strategy Evaluation** | Must treat violations as NOT_VIABLE |

---

## 5. Evidence Requirements

Satisfaction MUST be evidenced by:

| Obligation | Evidence Source |
|:-----------|:----------------|
| OBL-RG-ING-SYMBOLS | `EV-RG-RUN-1`, `EV-RG-RUN-2` outputs |
| OBL-RG-ING-HISTORY | `EV-RG-RUN-3` output |
| OBL-RG-ING-ALIGNMENT | `EV-RG-RUN-4` output |
| OBL-RG-ING-QUALITY | Ingestion metadata + validation |
| OBL-RG-ING-ENFORCEMENT | All above SATISFIED |

---

## 6. Failure Semantics

| Failure | Consequence |
|:--------|:------------|
| Any obligation UNMET | Regime computation FORBIDDEN |
| Regime runs anyway | GOVERNANCE VIOLATION |
| Silent fallback | FORBIDDEN |

---

## 7. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [minimal_regime_input_contract.md](file:///c:/GIT/TraderFund/docs/epistemic/contracts/minimal_regime_input_contract.md) | Contract definition |
| [regime_observability_audit.md](file:///c:/GIT/TraderFund/docs/epistemic/governance/regime_observability_audit.md) | Audit definition |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | Task definitions |
