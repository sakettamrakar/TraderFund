# Stress Visualization Widget Map
**Version**: 1.0.0
**Epoch**: TE-2026-01-30

## 1. Overview
This map defines which widgets visualize specific stress states for the canonical scenarios S1-S4.

## 2. Visualization Logic
Each widget MUST obey the following:
*   **State Binding**: If `inspection_mode = true`, bind to `InspectionStore.scenario[Sn].outcomes`.
*   **Visual Indicator**: Render a clear "SCENARIO" badge or striped background/border.
*   **Suppression Cause**: Explicitly display the "Why" (e.g., `VIX > 35`).

## 3. Scenario Matrix (S1-S4)

### 3.1 S1: Volatility Shock (Flash Crash)
*   **Source Condition**: `VIX > 35` (Hyper-Volatile)
*   **Regime Widget**:
    *   **State**: `BEAR_VOLATILE` / `SYSTEMIC_RISK`
    *   **Color**: Critical Red (#FF4136)
    *   **Annotation**: "Flash Crash Detected"
*   **New Orders (Blocker)**:
    *   **State**: `BLOCKED`
    *   **Reason**: `Regime Gate Triggered: Volatility Exception`
*   **Active Positions**:
    *   **Action**: `FREEZE_NEW_ENTRY`
    *   **Display**: "Halted (High Vol)"

### 3.2 S2: Liquidity Freeze (Bid-Ask Blowout)
*   **Source Condition**: `Spread > 50bps` (Illiquid)
*   **Liquidity Widget**:
    *   **State**: `LIQUIDITY_CRISIS`
    *   **Color**: Amber/Orange (#FF851B)
    *   **Metric**: `Avg Spread: 55bps` (Simulated)
*   **Execution Gate**:
    *   **State**: `THROTTLED`
    *   **Action**: `REDUCE_SIZE_50%`
    *   **Reason**: `Cost of Carry / Slippage Risk`
*   **Market Depth**:
    *   **Visual**: Sparse order book (simulated gaps)

### 3.3 S3: Correlation Breakdown (Hedge Failure)
*   **Source Condition**: `Corr(Equity, Bond) > 0.8` (Risk-On/Risk-Off Failure)
*   **Fragility Matrix**:
    *   **State**: `HEDGE_INEFFECTIVE`
    *   **Cell (Eq-Bond)**: Highlighted Red (0.85)
    *   **Warning**: "Portfolio Unhedged"
*   **Allocation Policy**:
    *   **Action**: `CASH_CONVERSION`
    *   **Reason**: `Diversification Failure`
*   **Performance (Backtest)**:
    *   **Drawdown**: Show projected -15% impact

### 3.4 S4: Yield Spike (Rates Shock)
*   **Source Condition**: `TNX Delta > +20bps/day` (Rate Shock)
*   **Macro Environment**:
    *   **Metric**: `10Y Yield: 4.5% (+0.25%)`
    *   **Trend**: `PARABOLIC_UP`
*   **Sector Rotation**:
    *   **Shift**: `GROWTH -> VALUE`
    *   **Action**: `EXIT_TECH_MOMENTUM`
    *   **Reason**: `Duration Sensitivity`
*   **Leverage Constraints**:
    *   **State**: `DELEVERAGE`
    *   **Target**: `0.5x Notional`

## 4. Widget Implementation Rules
1.  **Strict Read-Only**: Widgets must disable any interactive elements (sliders, inputs) in Inspection Mode.
2.  **Watermark**: Every chart must overlay "SIMULATED DATA" diagonally.
3.  **Tooltip**: Hovering over any metric must explain the stress assumption (e.g., "Assumes VIX spike to 40").
