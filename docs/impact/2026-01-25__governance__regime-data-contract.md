# Documentation Impact Declaration

**Change Summary**: Formalized the Minimal Regime Input Contract and Regime Ingestion Obligations.
**Change Type**: Governance / Data Contract
**Triggered By**: EV-RG-RUN Audit Findings (Data Gaps Identified)

## Impact Analysis

### Minimal Regime Input Contract
*   **Artifact Created**: `docs/epistemic/contracts/minimal_regime_input_contract.md`
*   **Purpose**: Defines the exhaustive list of 7 required symbols and hard constraints on history (3+ years), frequency (daily), and alignment.
*   **Impact**: Blocks any regime computation that does not meet the specified data integrity standards.

### Regime Ingestion Obligations
*   **Artifact Created**: `docs/epistemic/governance/regime_ingestion_obligations.md`
*   **Purpose**: Converts contract requirements into blocking obligations for the Evolution plane.
*   **Triggered Obligations**:
    - `OBL-RG-ING-SYMBOLS` (🔴 UNMET)
    - `OBL-RG-ING-HISTORY` (🔴 UNMET)
    - `OBL-RG-ING-ALIGNMENT` (🔴 UNMET)
    - `OBL-RG-ING-QUALITY` (🔴 UNMET)
    - `OBL-RG-ING-ENFORCEMENT` (🔴 UNMET)

## Safety & Integrity Guarantees

| Guarantee | Enforcement Mechanism |
|:----------|:----------------------|
| **No Incomplete Computation** | `OBL-RG-ING-ENFORCEMENT` blocks regime logic |
| **No Silent Interpolation** | `OBL-RG-ING-QUALITY` forbids forward-fill |
| **Data Verifiability** | `EV-RG-RUN` audits must confirm contract compliance |

## Guiding Principle
> A regime that runs on incomplete data is worse than no regime at all.

**Status**: Published & Binding
