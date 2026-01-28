# Documentation Impact Declaration: Market Intelligence Dashboard (Observer)

**Date**: 2026-01-28
**Component**: Evolution (Dashboard)
**Task ID**: EV-DASHBOARD
**Impact Type**: Infrastructure (Read-Only)

## Change Summary
Implements a **Read-Only, Observer-Only** Market Intelligence Dashboard to visualize system state, diagnostic watchers, and governance artifacts.

## Observer-Only Invariants (Hard Constraints)
This dashboard is strictly prohibited from influencing system state. The following invariants are architecturally enforced:

1.  **No Execution**: The dashboard backend (`src/dashboard/backend`) MUST NOT import `StrategyRunner`, `OrderManager`, or any execution-related modules.
2.  **No Writes**: The dashboard backend MUST NOT expose any POST/PUT/DELETE endpoints that modify system state. All file operations must be read-only (`'r'`).
3.  **No Task Mutation**: The dashboard cannot add, modify, or delete tasks in `task_graph.md`.
4.  **No Ledger Append**: The dashboard cannot write to `evolution_log.md` or `decisions.md`. It only reads them.
5.  **No Triggers**: The dashboard cannot trigger `EV-TICK`. It only reflects the state *after* a tick has occurred.

## Architecture
*   **Backend**: Python FastAPI service serving JSON data from existing `docs/evolution/` artifacts.
*   **Frontend**: React (Vite) Single Page Application in `src/dashboard/frontend`.

## Governance
*   **Obligation**: Satisfies `OBL-DASHBOARD-OBSERVER-ONLY`.
*   **Epistemic Clarity**: The dashboard answers "What is the system state?" and "Why is it in this state?" without actively changing it.

## Verification
*   **Automated**: Static analysis to ensure no forbidden imports.
*   **Manual**: Verification that no UI elements exist to trigger actions (only navigation/view controls).
