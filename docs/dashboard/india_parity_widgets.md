# India Parity Dashboard Widgets

## 1. Widget: `IndiaParityIndicator`
*   **Location**: `DataAnchorPanel` (when market=INDIA).
*   **Display**:
    *   **Traffic Light**: Red (DEGRADED), Yellow (PARTIAL), Green (CANONICAL).
    *   **Gap Count**: "3 of 4 proxies missing".
    *   **Upgrade Blocker**: "Missing: NIFTY50, BANKNIFTY, INDIAVIX".

## 2. Transition Animation
When India achieves CANONICAL status (future):
*   The indicator transitions from Red to Green with a subtle pulse.
*   A "Parity Achieved" banner appears once.
*   `PolicyStateCard` for India unlocks from the forced `OBSERVE_ONLY` display.

## 3. Honest Stagnation Message
While DEGRADED, the India view should display:
> "India market is operating in **Observer-Only** mode due to insufficient proxy coverage. This is intentional governance, not an error. See the [Gap Register] for details."

This message ensures the operator understands this is a *feature*, not a bug.

## 4. Future: Parity Readiness Checklist
A dedicated modal or panel showing:
*   ☐ NIFTY50 Ingested (200+ days)
*   ☐ BANKNIFTY Ingested (200+ days)
*   ☐ INDIAVIX Ingested (50+ days)
*   ☐ IN10Y Ingested (100+ days)

Each item turns ✓ when the corresponding proxy is active and non-stale.
