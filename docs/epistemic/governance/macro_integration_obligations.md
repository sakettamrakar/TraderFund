# Macro Integration Obligations

**Status**: BINDING  
**Scope**: Macro Context Layer  
**Date**: 2026-01-29

## 1. Non-Gating Obligation (OBL-MACRO-1)
> **The Macro Context Layer MUST NOT block or allow any strategy directly.**

- **Rationale**: Macro signals are too slow and broad. Gating logic belongs in Strategy Resolution.
- **Enforcement**: `strategy_eligibility_resolver.py` must NOT import or read `macro_context.json`.

## 2. Read-Only Obligation (OBL-MACRO-2)
> **The Macro Context Builder MUST NOT execute trades or side effects.**

- **Rationale**: This layer is for explanation, not action.
- **Enforcement**: The builder class must not import `execution` or `broker` modules.

## 3. Interpretability Obligation (OBL-MACRO-3)
> **Macro states MUST be human-readable strings, not raw numbers.**

- **Rationale**: The goal is narrative trust.
- **Correct**: `Liquidity: CONTRACTING`
- **Incorrect**: `Liquidity: -0.42`

## 4. Frozen Schema Obligation (OBL-MACRO-4)
> **The `macro_context.json` schema is FROZEN.**

- Additions require a D-Series Decision.
- Removals are forbidden to preserve history.
