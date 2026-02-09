# Stress Inspection Mode Contract
**Version**: 1.0.0
**Status**: DRAFT
**Epoch**: TE-2026-01-30

## 1. Intent & Scope
The **Stress Inspection Mode** allows authorized operators to visualize system behavior under hypothetical stress conditions (S1–S4) without altering the system's operational state or persistent data. It is a strictly **read-only, ephemeral** visualization layer.

## 2. Inspection Mode Contract

### 2.1 Activation & State
*   **Explicit Activation**: The mode MUST be activated via an explicit flag `inspection_mode = true` in the frontend application state (e.g., Redux/Context).
*   **Exclusive State**: When `inspection_mode = true`, the dashboard MUST NOT render any data from the `LiveTruth` store. All widgets must re-bind to the `InspectionStore`.
*   **Visual Indication**: The application interface MUST display a persistent, high-contrast banner (e.g., Red/Orange) stating "INSPECTION MODE — SCENARIO VISUALIZATION ONLY".

### 2.2 Data Source Authority
*   **Sole Source**: The ONLY authorized source for stress data is the static audit artifact: `docs/audit/phase_3_stress_scenario_report.md`.
*   **No Simulation**: The dashboard MUST NOT perform live recalculations or simulations. It strictly renders the *verdicts* recorded in the audit report.
*   **No Persistence**: Inspection data MUST NOT be saved to the backend database, local storage, or any persistent cache.

### 2.3 Separation of Concerns
*   **API Isolation**: Inspection data fetched via `/api/inspection/*` endpoints MUST be logically separated from `/api/live/*`.
*   **Leakage Prevention**:
    *   **No Execution**: Trade execution buttons MUST be disabled or hidden.
    *   **No Alerts**: Stress scenarios MUST NOT trigger operational alerts (PagerDuty, Email).

## 3. Scenario Definitions (S1-S4)
The contract governs the visualization of the following canonical scenarios:
*   **S1**: Volatility Shock (Flash Crash)
*   **S2**: Liquidity Freeze (Bid-Ask Spread Blowout)
*   **S3**: Correlation Breakdown (Hedge Failure)
*   **S4**: Yield Spike (Rates Shock)

## 4. Teardown Guarantee
Upon exiting Inspection Mode:
1.  `inspection_mode` flag is explicitly set to `false`.
2.  `InspectionStore` (Scenario State) is immediately cleared/garbage collected.
3.  Dashboard performs a synchronous re-bind to `LiveTruth` without requiring a page refresh, ensuring a seamless return to valid operational state.
4.  No residue (files, logs, artifacts) remains in the system memory or storage.

## 5. Violation Consequences
Any violation of this contract (e.g., persisting stress data, executing trades in inspection mode) constitutes a **Critical Epistemic Failure** and requires an immediate system halt and audit.
