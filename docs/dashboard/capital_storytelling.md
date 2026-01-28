# Capital Storytelling Philosophy

The TraderFund system adheres to a strict principle: **Capital should be the quietest part of the system until the market forces it to speak.**

## Objectives

1.  **Explain Inertia**: Explicitly state *why* capital is not moving (e.g., "No strategies eligible").
2.  **Build Trust**: Display hard invariants (No Leverage, No Execution) prominently.
3.  **Traceability**: Maintain an immutable history of capital states for every tick.

## Components

### 1. Capital Narrative Panel
- **Posture**: High-level state (IDLE, READY, RESTRICTED).
- **Checklist**: Explicit blockers (Volatility, Dispersion, Authorization).
- **Timeline**: Recent history of state changes.
- **Counterfactuals**: "Even if X happened, Y would still block execution."

### 2. Invariants Panel
- Fixed display of non-negotiable constraints (e.g., No Leverage).

## Data Flow
`EV-TICK` -> Step 7 Record -> `capital_state_timeline.json` -> API -> Dashboard

Measurements are **symbolic** (Paper Capital = 100). No real P&L is tracked.
