# Convergence Map

**Authority**: `ARCH-1.4`
**Status**: ACTIVE
**Date**: 2026-01-30

## 4.1 Purpose
This document defines how "stranded", "legacy", or "future" components converge into the immutable Three-Ring Architecture. It answers "Where does X go?" and "What do we do with Y?".

---

## 4.2 Component Convergence

### India Market Logic
- **Current State**: Data exists (`src/data_ingestion` - NSE EOD), but formal Strategy Eligibility logic is missing. `MomentumEngine` (Ring 3) likely runs on this data ad-hoc.
- **Target State**: **Ring 2 (Market Research Adapters)**.
- **Convergence Path**:
    1.  Create `src/adapters/india_research/` (Future).
    2.  Implement `IndiaMarketProxy` implementing `MarketContextProtocol`.
    3.  Feed NSE data into Ring 1 (Evolution) via this adapter.
    4.  **Do NOT** put India logic in `src/strategy` (which is symbol-free).

### Momentum Engine (`src/core_modules/momentum_engine`)
- **Current State**: Ring 3 (Scanner/Heuristic). Active.
- **Target State**: **Ring 3 (Intelligence)**.
- **Why**: It relies on heuristics (Vol > 2x, Near HOD). It is NOT "Truth". It is a "View".
- **Convergence**:
    - Remains as a "Scanner" for human/observer attention.
    - If a "Momentum Strategy" is desired for Ring 1, it must be defined declaratively in `src/strategy/registry.py` (already done: `STRAT_MOM_TIMESERIES_V1`) and evaluated by `src/evolution` without heuristics.

### Legacy Research Modules (`research_modules/`)
- **Current State**: Root-level folder. Likely legacy notebooks or scripts.
- **Target State**: **Harvest & Archive**.
- **Convergence**:
    - Valuable logic (e.g., Risk Models) moves to `src/layers/factor_layer.py` (Ring 1) or `src/adapters/` (Ring 2).
    - Exploration code moves to `notebooks/`.
    - The `research_modules/` folder should eventually be deleted.

### Root Narratives (`narratives/`) vs `src/decision/`
- **Current State**: `narratives/` contains core models. `src/decision/` contains the engine.
- **Target State**: **Consolidate to `src/intelligence/`** (Future) or keep as Ring 3.
- **Convergence**:
    - `narratives/` (Root) is Ring 3 domain logic.
    - `src/decision/` is Ring 3 application logic.
    - Both belong in the "Intelligence Layer".
    - Future refactor should move `narratives/` into `src/` to clean the root.

---

## 4.3 Why Nothing is Wasted

| Artifact | Fate | Reason |
| :--- | :--- | :--- |
| **Old India Scripts** | Re-enter via **Ring 3** | Used for "Interesting Activity" scanners (Observer Mode). |
| **Legacy Scanners** | Re-enter via **Ring 3** | Scanners are valid Intelligence, even if not Truth. |
| **Duplicate Docs** | Delete / Merge | Confusion reduction. |
| **Unused Data** | Dormant | Data is cheap; keep until provenance is confirmed. |

## 4.4 The "Intelligence Layer" Restriction
**Constraint**: "NOT introduce India research logic yet... NOT implement Intelligence Layer logic."
**Implication**:
- We acknowledge `narratives/` and `src/decision/` exist.
- We do **NOT** expand them or wire them to new India logic yet.
- They remain in **Observer Mode**.
