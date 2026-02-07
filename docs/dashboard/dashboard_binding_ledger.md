# Dashboard Binding Ledger

## 1. Ledger Purpose
This document is the single source of truth for the mapping between frontend dashboard widgets and backend truth artifacts. No widget shall be developed or deployed without an authorized entry in this ledger. This binding ensures that every visual element has a verifiable and governed data lineage.

## 2. Binding Table

| Widget ID | Widget Name | Backend Artifact | Layer | Explanation Allowed | Trace Required | Degradation Rule | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| A0.1 | System Layer Health | system_layer_health.json | META | Yes (mechanical only) | Yes | Loud when stale | KEEP |
| A1.1 | Data Scale / Data Coverage | market_parity_status.json (per market) | DATA / INTELLIGENCE | Yes (traceable only) | Yes | Explicit per missing role | KEEP |
| A1.2 | Execution Gate Status | execution_gate_status.json (REQUIRED) | INTELLIGENCE / GOVERNANCE | Yes (block-only) | Yes | Default CLOSED, loud on missing | KEEP |
| A1.3 | Last Successful Evaluation | last_successful_evaluation.json (REQUIRED) | META | No | Yes | NONE / STALE explicit | KEEP |
| A2.1 | System Stress Posture | system_stress_posture.json | META / INTELLIGENCE | Yes (mechanical only) | Yes | UNKNOWN if any dependency missing | KEEP |
| A2.2 | System Constraint Posture | system_posture.json | INTELLIGENCE (DERIVED) | Yes (referential only) | Yes | UNKNOWN if policy/fragility missing | KEEP |
| A3.1 | Market Scope (Evaluated Markets) | market_evaluation_scope.json | META / INTELLIGENCE | Yes (referential) | Yes | Default UNKNOWN | KEEP |
| A3.2 | Data Coverage (Market-Level) | market_parity_status_{MARKET}.json | DATA / INTELLIGENCE | Yes (referential) | Yes | Explicit per missing role | KEEP |
| A3.3 | Capital Readiness | MISSING | INTELLIGENCE | No | Yes | Default BLOCKED | FIX |
| A3.4 | Strategy Status | MISSING | INTELLIGENCE | No | Yes | Default DISABLED | FIX |
| A3.5 | Universe / Stories Status | MISSING | NARRATIVE | Yes (traceable) | Yes | Default EMPTY | FIX |
| B1 | Market Structure Snapshot | MISSING | FACTOR | Yes (mechanical) | Yes | Loud on missing; summary-only snapshots forbidden | FIX |
| C1 | Macro Context Layer | docs/macro/context/macro_context.json | MACRO | Yes (mechanical) | Yes | Loud on missing | FIX |
| D1 | Decision Policy | docs/intelligence/decision_policy_{MARKET}.json | INTELLIGENCE | Yes (referential) | Yes | Explicit permissions only | FIX |
| D2 | Fragility Policy | docs/intelligence/fragility_context_{MARKET}.json | INTELLIGENCE | Yes (referential) | Yes | Explicit constraints only | FIX |
| E1 | "Why Nothing Is Happening" | MISSING | META | Yes (causal trace) | Yes | Loud on missing | FIX |
| E2 | Capital Narrative | MISSING | NARRATIVE | No | Yes | Default NO_ALLOCATION | FIX |
| F1 | Company Knowledge | MISSING | NARRATIVE | Yes (cite only) | Yes | Explicit trace required | FIX |
| F2 | Sector Exposure | MISSING | FACTOR | Yes (mechanical) | Yes | 0 if missing | FIX |
| F3 | Event Signal Trace | MISSING | INTELLIGENCE | Yes (cite only) | Yes | Loud on missing | FIX |
| G1 | System Invariants | docs/dashboard/dashboard_truth_contract.md | META | Yes (mechanical) | Yes | Hard ban on violation | KEEP |
| G2 | Conditions Enabling Trades | docs/narrative/regime_gating_rules.md | GOVERNANCE | Yes (referential) | Yes | No "soon" language | FIX |

## 3. Ledger Rules
1. **Pre-UI Registration**: New widgets MUST be registered in this ledger before any UI development begins.
2. **Epoch Alignment**: All bindings are assumed to be for the current Truth Epoch (TE-2026-01-30) unless otherwise specified.
3. **Widget Verdicts**:
    - **KEEP**: Widget is fully bound, verified, and adheres to the Truth Contract.
    - **FIX**: Widget has an identified binding or compliance gap and must not be used for decision support.
    - **REMOVE**: Widget is unauthorized or violates a governance invariant and must be purged.
4. **Trust Boundary**: Widgets marked `FIX` or `REMOVE` must be visually flagged as "Degraded/Untrusted" in the UI or disabled entirely.

---
*Authorized by Truth Epoch TE-2026-01-30*
