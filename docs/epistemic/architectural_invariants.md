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
