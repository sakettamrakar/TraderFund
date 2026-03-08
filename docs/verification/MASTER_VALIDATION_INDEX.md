# Master Validation Index: V3 Real-Data Operational Validation

**Epoch**: TE-2026-01-30
**Mode**: REAL_ONLY, DRY_RUN
**Scope**: US, INDIA
**Purpose**: Sequential operational validation framework to prove V3 convergence, schema determinism, regime gating, and structural invariants without introducing capital interaction or execution capabilities (INV-NO-EXECUTION, INV-NO-CAPITAL).

## Validation Phases

This framework is divided into five strictly sequential phases. A phase cannot begin until its predecessor yields 100% deterministic success on real data.

1.  **[Phase 1: Ingestion Validation](PHASE_1_INGESTION_VALIDATION.md)**
    *   **Focus**: Live data acquisition, pipeline parity (US/India), and temporal structural integrity.
    *   **Invariants Enforced**: `OBL-MARKET-PARITY`, `INV-PROXY-CANONICAL`.
2.  **[Phase 2: Memory Binding Validation](PHASE_2_MEMORY_BINDING_VALIDATION.md)**
    *   **Focus**: Routing ingested data to the canonical memory store, mutation safety, and temporal truth alignment.
    *   **Invariants Enforced**: `OBL-TRUTH-EPOCH-DISCLOSED`, `OBL-HONEST-STAGNATION`.
3.  **[Phase 3: Research Intelligence Validation](PHASE_3_RESEARCH_INTELLIGENCE_VALIDATION.md)**
    *   **Focus**: Regime classification, macro context mapping, and candidate generation logic.
    *   **Invariants Enforced**: `OBL-REGIME-GATE-EXPLICIT`, `INV-NO-SELF-ACTIVATION`.
4.  **[Phase 4: Evaluation & Evolution Validation](PHASE_4_EVALUATION_EVOLUTION_VALIDATION.md)**
    *   **Focus**: Deterministic replay verification, scoring consistency, and execution harness dry-runs.
    *   **Invariants Enforced**: `INV-NO-EXECUTION`, `INV-NO-CAPITAL`.
5.  **[Phase 5: Dashboard Integrity Validation](PHASE_5_DASHBOARD_INTEGRITY_VALIDATION.md)**
    *   **Focus**: Glass-box observability, error surfacing, and provenance mapping.
    *   **Invariants Enforced**: `INV-READ-ONLY-DASHBOARD`, `OBL-DATA-PROVENANCE-VISIBLE`.

## Governance Prerequisites

> **WARNING**: Before running these validation segments, the human operator MUST confirm that the exact epoch ID (`TE-2026-01-30`) is bound and that **Truth is FROZEN** (`frozen: true`). Running these validations with drifting truth invalidates the determinism guarantee and violates `AG-GOV-TRUTH-003`.

## Execution Protocol

1.  Run the tests sequentially.
2.  Tests are executed via `relay` scripts operating purely on the `RESEARCH` and `MACRO` layers.
3.  Any state-modifying action must be written exclusively to temporary validation sinks, ensuring canonical memory is preserved unless structurally authorized.
