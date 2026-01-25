# Architectural Invariants

The following rules are non-negotiable architectural guarantees:

1.  **Event Time Integrity**: All logic must proceed based on `event_time`, not processing/ingestion time. Replays must yield the exact same state as live runs.
2.  **No Lookahead**: Core abstractions (like `CandleCursor`) must physically prevent access to future data during simulation and replay.
3.  **Immutability of Raw Data**: Data once ingested (Bronze/Raw layer) is never mutated. Corrections are applied as new versions or overlays, never in-place edits.
4.  **Separation of Concerns**:
    *   **India vs US**: Market pipelines are physically distinct with no shared state.
    *   **Signal vs Execution**: The Momentum Engine emits independent signals; it does not know about capital or execution constraints.
5.  **Idempotency**: Re-running a processing job on the same input data must result in the precise same output, byte-for-byte where possible.
6.  **Glass-Box Observability**: Every "magic number" or threshold must be configurable and observable. No hard-coded logic hidden deep in classes.
7.  **Cognitive Ordering Invariant**: The evaluation order is strictly frozen: **Regime / Event / Narrative → Strategy → Execution**. It is forbidden for downstream strategy logic to bypass higher-order context. This is a system safety property.
8.  **Layer Bypass Prohibition**: No layer may skip its upstream constraints. Signals must receive regime context from Regime Layer, not infer it directly. Strategies must receive macro context via Regime, not query Macro directly. (See [layer_interaction_contract.md](file:///c:/GIT/TraderFund/docs/contracts/layer_interaction_contract.md))
9.  **Factor Permission Invariant**: When the Factor Layer is implemented, no signal may bypass factor permissions. Factors constrain exposure categories, not asset selection. (See [factor_layer_policy.md](file:///c:/GIT/TraderFund/docs/epistemic/factor_layer_policy.md))

