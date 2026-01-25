# Documentation Impact Declaration: Evaluation Profile Integration

**Date**: 2026-01-25
**Decision Reference**: D013 (Decision Plane Authorization)
**Impact Type**: Structural Extension (Non-Breaking)

## 1. Change Summary

Introduced **Evaluation Profiles** as a first-class configuration mechanism for the Evolution Execution Phase (EV-RUN). This allows for parameterized, repeatable, and governed execution of the task graph without modifying the graph structure itself.

### Key Components Added

1.  **Schema**: `docs/evolution/evaluation_profiles/schema.md` (Authoritative definition).
2.  **Canonical Profiles**:
    - `EV-HISTORICAL-ROLLING-V1`: Historical rolling-window evaluation.
    - `EV-FORCED-BULL-CALM-V1`: Counterfactual stress test.
3.  **Execution Loader**: `src/evolution/profile_loader.py`.
4.  **Orchestrator**: `bin/run_ev_profile.py`.
5.  **Multi-Window Support**: Parameterized EV-RUN-0 through EV-RUN-6.

## 2. Invariant Preservation

| Invariant | Status | Verification |
|:----------|:-------|:-------------|
| **Task Graph Immutability** | PRESERVED | No new tasks added to `task_graph.md`. |
| **Shadow-Only Execution** | ENFORCED | Schema enforces `execution.shadow_only: true`. |
| **Regime Binding** | PRESERVED | EV-RUN-0 (Context Builder) remains the sole authority for regime state per window. |
| **Governance** | ENFORCED | Profile execution strictly requires Ledger and DID generation. |

## 3. Impact on Existing Artifacts

- **Regime Context Builder**: Extended to support `profile` argument and `build_windowed_contexts()`. Backward compatible with legacy no-arg calls.
- **EV-RUN Modules**: `bulk_evaluator.py`, `decision_replay.py`, etc., updated to accept `context_path` and `output_dir` via CLI/Init, allowing namespaced execution.
- **Ledger**: New event type `EV-RUN Profile Execution` defined.

## 4. Operational Runbook Update

### How to Run an Evaluation Profile

```bash
python bin/run_ev_profile.py --profile docs/evolution/evaluation_profiles/EV-HISTORICAL-ROLLING-V1.yaml
```

### Outputs

Outputs are namespaced to avoid collision:
`docs/evolution/evaluation/{artifact_namespace}/{window_id}/`

## 5. Risk Assessment

- **Complexity**: Moderate increase in orchestration logic. Mitigated by strict schema validation.
- **Data Volume**: Multi-window runs generate significant artifact volume. `persist_intermediate` flag controls cleanup (default true for now).
- **Execution Safety**: High. Hard-coded `shadow_only` enforcement prevents accidental real execution.

## 6. Conclusion

The system is now capable of "What If" analysis (Counterfactuals) and "Backtesting" (Historical) using a governed, unified pipeline.
