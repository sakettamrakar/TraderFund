# Fragility Policy Dashboard Widgets

## 1. Widget: `FragilityStateCard`
*   **Location**: Below `PolicyStateCard`.
*   **Display**:
    *   **Stress Level**: Meter (Normal [Green] -> Elevated [Yellow] -> Systemic [Red]).
    *   **Active Signals**: List of firing triggers (e.g., "Liquidity Shock").
    *   **Constraints Applied**: "Blocking New Entries due to Volatility".

## 2. Widget: `PermissionsTable`
*   **Concept**: A matrix showing the permission flow.
    *   Row: `ALLOW_LONG_ENTRY`
    *   Col 1: Decision Policy (`YES`)
    *   Col 2: Fragility Policy (`BLOCK`)
    *   Col 3: Final Authorization (`NO`)
*   **Value**: Provides complete traceability of "Why can't I trade?".

## 3. Integration with PolicyCard
Alternatively, merge into `PolicyStateCard` as a "System Stability" subsection.
But sticking to "Separation of Concerns", a separate card is preferred initially for clarity.
