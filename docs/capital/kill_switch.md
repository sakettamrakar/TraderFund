# Kill-Switch Semantics

The Kill-Switch is the ultimate safety mechanism, overriding all other logic to sever risk.

## Hierarchy

### 1. Global Kill-Switch
*   **Effect**: Halts **ALL** system activity.
*   **Trigger**:
    *   Manual Operator Command.
    *   Drawdown > 10% (FROZEN state).
    *   Data Integrity Failure (3+ consecutive ticks).

### 2. Family Kill-Switch
*   **Effect**: Disables a specific Strategy Family (e.g., "Kill Momentum").
*   **Trigger**:
    *   Family Drawdown > 3%.
    *   Manual Operator Command.

### 3. Strategy Kill-Switch
*   **Effect**: Disables a specific Strategy ID.
*   **Trigger**:
    *   Strategy Drawdown > 2%.
    *   3 consecutive stop-losses hit (Symbolic).

## Reset Authority

*   **Human Only**: No automated resets are permitted for **ANY** kill-switch activation.
*   **Process**:
    1.  Diagnosis of root cause.
    2.  Manual modification of `kill_switch_state.json`.
    3.  Restart of EV-TICK services.
