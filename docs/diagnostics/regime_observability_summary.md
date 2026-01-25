# Regime Observability Summary

**Report Type**: REGIME_OBSERVABILITY_SUMMARY  
**Generated**: 2026-01-25  
**Status**: AUDIT COMPLETE

---

## 1. Executive Summary

This document summarizes the Regime Observability Audit results.

**Guiding Principle**: You cannot debug logic until you prove the data can support it.

---

## 2. Audit Components Implemented

| Component | Artifact | Status |
|:----------|:---------|:-------|
| Symbol Enumeration | `symbol_enumeration.py` | ✅ |
| Ingestion Coverage | `ingestion_coverage.py` | ✅ |
| Historical Depth | `depth_audit.py` | ✅ |
| Temporal Alignment | `alignment_audit.py` | ✅ |
| State Viability | `viability_check.py` | ✅ |
| Undefined Attribution | `undefined_attribution.py` | ✅ |

---

## 3. Regime-Required Symbols

Based on regime policy documents:

| Symbol | Role | Lookback (days) |
|:-------|:-----|:----------------|
| QQQ | EQUITY_PROXY | 252 |
| SPY | EQUITY_PROXY | 252 |
| VIX | VOLATILITY_PROXY | 63 |
| ^TNX | RATES_PROXY | 126 |
| ^TYX | RATES_PROXY | 126 |
| HYG | CREDIT_PROXY | 63 |
| LQD | CREDIT_PROXY | 63 |

---

## 4. Undefined Regime Cause Categories

Every `regime = undefined` is attributed to:

| Cause | Description |
|:------|:------------|
| MISSING_SYMBOL | Required symbol not ingested |
| INSUFFICIENT_HISTORY | Lookback window not satisfiable |
| TEMPORAL_MISALIGNMENT | Symbols not aligned on timestamp |
| INVALID_STATE | Data present but state invalid |
| COMPUTATION_ERROR | Logic error (requires code review) |

---

## 5. Obligations Satisfied

| Obligation | Satisfied By |
|:-----------|:-------------|
| OBL-RG-SYMBOLS | `symbol_enumeration.py`, `ingestion_coverage.py` |
| OBL-RG-DEPTH | `depth_audit.py` |
| OBL-RG-ALIGNMENT | `alignment_audit.py` |
| OBL-RG-VIABILITY | `viability_check.py` |
| OBL-RG-ATTRIBUTION | `undefined_attribution.py` |
| OBL-RG-CLOSURE | This summary |

---

## 6. Available Report Generators

| Report | Generator Method |
|:-------|:-----------------|
| Symbol Requirements | `SymbolEnumeration.generate_requirements_report()` |
| Coverage Matrix | `IngestionCoverageAudit.generate_coverage_matrix()` |
| Lookback Sufficiency | `DepthAudit.generate_sufficiency_report()` |
| Alignment Heatmap | `AlignmentAudit.generate_alignment_report()` |
| State Viability | `StateViabilityCheck.generate_viability_report()` |
| Attribution Table | `UndefinedAttributionReport.generate_attribution_table()` |

---

## 7. Next Steps

With Regime Observability complete, the following is now eligible (but not authorized):

- Regime logic tuning (pending separate decision)
- Threshold adjustment (pending data remediation)
- Symbol universe expansion (pending ingestion work)

**Execution remains BLOCKED.**
