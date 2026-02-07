# Governance Document Manifest

## 1. Purpose
This manifest defines the canonical location, role, and mutability status of all core governance artifacts within the System Documentation.

---

## 2. Document Classification

| Document Name | Role | Location | Phase Lock Status |
| :--- | :--- | :--- | :--- |
| **Market Proxy Sets** | `CONTRACT` | `docs/contracts/market_proxy_sets.md` | **LOCKED** (Requires Governance) |
| **Proxy Dependency Contracts** | `CONTRACT` | `docs/contracts/proxy_dependency_contracts.md` | **LOCKED** (Requires Governance) |
| **Data Source Governance** | `REGISTRY` | `docs/data/data_source_governance.md` | **ACTIVE** (Update on ingestion) |
| **Coverage Gap Register** | `REGISTRY` | `docs/data/coverage_gap_register.md` | **ACTIVE** (Update on ingestion) |
| **Degraded State Registry** | `REGISTRY` | `docs/data/degraded_state_registry.md` | **ACTIVE** (Update on state change) |
| **Ingestion Proxy Wiring** | `MAP` | `docs/architecture/ingestion_proxy_wiring.md` | **OPEN** (Implementation Ref) |
| **Factor Recomputation Map** | `MAP` | `docs/architecture/factor_recomputation_map.md` | **OPEN** (Implementation Ref) |
| **Regime Gate Recalibration** | `MAP` | `docs/architecture/regime_gate_recalibration.md` | **OPEN** (Implementation Ref) |
| **Truth Epoch Scoping** | `EPISTEMIC` | `docs/epistemic/truth_epoch_scoping.md` | **LOCKED** (Fundamental Principle) |
| **System Discontinuity Log** | `EPISTEMIC` | `docs/epistemic/system_discontinuity_log.md` | **APPEND-ONLY** |
| **Proxy Mismatch Audit** | `AUDIT` | `docs/audit/proxy_mismatch_audit.md` | **IMMUTABLE** (Snapshot) |

---

## 3. Role Definitions
*   **CONTRACT**: Binding operational law. Violations are system failures.
*   **REGISTRY**: Dynamic log of system state (gaps, sources, degraded modes).
*   **MAP**: Architectural wiring diagram or logic derivation.
*   **EPISTEMIC**: foundational reasoning or historical continuity record.
*   **AUDIT**: Forensic snapshot of system state at a point in time.

## 4. Verification Check
Running `tree docs/` should reflect this structure.
