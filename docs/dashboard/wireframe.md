# Dashboard Wireframe (Observer-Only)

**Layout Principle**: Top-down hierarchy from "System Health" to "Detailed Evidence".
**Visual Style**: Dark Mode, High Contrast, Data-Dense.

## 1. System Status Banner (Top, Full Width)
*   **Left**: TraderFund Logo / Title
*   **Center**: `SYSTEM STATE: {IDLE | OBSERVING}` (Color Coded Tag)
    *   *Subtext*: "{Reason}" (e.g. "No expansion detected")
*   **Right**: 
    *   Last Tick: `YYYY-MM-DD HH:mm:ss`
    *   Governance: `CLEAN` (Green)

## 2. Layer Health Grid (Row, below Banner)
*   Grid of small "Signal Lights" for each layer:
    *   Regime Context [OK]
    *   Momentum Watcher [OK]
    *   Liquidity Watcher [OK]
    *   ...etc.
*   Tooltip/Subtext shows `Last Updated`.

## 3. Market Structure Snapshot (Row of Cards)
*   **Card 1: Regime**
    *   Big Text: `BULL VOLATILE`
    *   Muted: `Conf: 82%`
*   **Card 2: Momentum**
    *   Big Text: `ABSENT`
    *   Muted: `Conf: 77%`
*   **Card 3: Liquidity**
    *   Big Text: `NEUTRAL`
*   **Card 4: Dispersion**
    *   Big Text: `STABLE`

## 4. Watcher Timeline (Main Content Area - Left)
*   Table or Stacked Bar Chart showing last 10 ticks.
*   Columns: Time | Momentum | Expansion | Dispersion | Liquidity
*   Purpose: "Is red turning to green?"

## 5. Strategy Eligibility Matrix (Main Content Area - Right)
*   Table:
    *   **Strategy Name**: "Momentum (V1)", "Value"
    *   **Regime Check**: ✅ / ❌
    *   **Factor Check**: ✅ / ❌
    *   **Status**: `BLOCKED` (Red) / `ELIGIBLE` (Green)
    *   **Reason**: "Waiting for Expansion"

## 6. Meta-Analysis & Narrative (Bottom Row)
*   **Meta-Analysis**: Rendered Markdown from `evolution_comparative_summary.md`.
*   **"What Would Change My Mind?"**:
    *   Static text explaining conditions.
    *   e.g., "To activate Momentum, I need Expansion != NONE AND Dispersion != NONE."

## Footer
*   Governance Disclaimer: "Observer Only. No Execution Capability."
