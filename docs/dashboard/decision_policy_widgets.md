# Decision Policy Dashboard Widgets

## 1. Widget: `PolicyStateCard`
*   **Location**: Header / Overview Panel.
*   **Data Source**: `decision_policy_{market}.json`.
*   **Visuals**:
    *   **Status Badge**: `ACTIVE` (Green), `RESTRICTED` (Yellow), `HALTED` (Red).
    *   **Action List**: Chips for `ALLOW_LONG`, `ALLOW_SHORT`, etc. (Dimmed if blocked).
    *   **Reason Text**: "Restricted due to Tight Liquidity".

## 2. Widget: `EpistemicHealthCheck`
*   **Location**: Sidebar / Footer.
*   **Data Source**: `decision_policy.epistemic_check`.
*   **Visuals**:
    *   **Proxy Integrity**: "Canonical" vs "Degraded".
    *   **Truth Epoch**: Timestamp of last valid policy computation.

## 3. Interaction Design
*   **Drill-Down**: Clicking the "Status Badge" opens a modal showing the "Constraint Evaluation Log" (e.g., "Liquidity Check: Failed", "Regime Check: Passed").
*   **Honesty**: If `decision_policy` is missing or stale > 1 hour, the UI **MUST** display a "System Offline / Stale" overlay.
