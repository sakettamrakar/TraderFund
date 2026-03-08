# RUN_004_EVALUATION

| Field | Value |
| --- | --- |
| Date | 2026-03-07 |
| Repository | TraderFund |
| Specification | docs/verification/PHASE_4_EVALUATION_EVOLUTION_VALIDATION.md |
| Validation Method | Code inspection + semantic replay against stored 90-day contexts + artifact comparison |
| Overall Status | **PASS** |

---

## Scope And Datasets

Primary replay dataset:

- `docs/evolution/context/EV-HISTORICAL-ROLLING-V1/WINDOW-2025-10-17-2026-01-15/regime_context.json`
- `docs/evolution/evaluation/ev/historical/rolling/v1/WINDOW-2025-10-17-2026-01-15/`

Auxiliary deterministic cross-regime probes:

- `docs/evolution/context/EV-FORCED-BULL-CALM-V1/WINDOW-2025-10-17-2026-01-15/regime_context.json`
- `docs/evolution/context/EV-FORCED-BEAR-RISKOFF-V1/WINDOW-2025-10-17-2026-01-15/regime_context.json`

All fresh replay artifacts were written to:

- `temp_debug/run004_eval_validation/`

Normalization note:

- Determinism comparisons were performed semantically, excluding volatile fields such as `timestamp`, `computed_at`, and markdown `Generated` lines.
- This is required because the evaluation modules embed runtime timestamps directly into otherwise deterministic artifacts.

---

## Step Results Summary

| Step | Status | Result |
| --- | --- | --- |
| 1. Identify evaluation metrics | PASS | Declared success criteria and emitted evaluation metrics mapped |
| 2. Deterministic evaluation | PASS | Repeated replays on identical inputs were semantically identical |
| 3. Evolution logic | PASS with note | No unauthorized memory mutation found; evaluation remains read-only and diagnostic by contract |
| 4. Feedback integrity | PASS | Factor context now propagates through replay, rejection analysis, and bundle compilation without introducing memory write-back |
| 5. Replay test (90 days) | PASS | The latest historical corpus was refreshed against current code and registry state; core strategy-scoped outputs now align with the active pipeline |
| 6. Write results | PASS | This report documents evidence and reproducible commands |

---

## Step 1 - Identify Evaluation Metrics

### Declared Metrics And Success Criteria

From `docs/memory/02_success/success_criteria.md`:

- Regime stability: false regime flips must remain `< 5%` of trading days.
- Opportunity alignment: `>= 60%` of high-conviction ideas must align with dominant factor regime within 10 trading sessions.
- Confluence gate: high-conviction requires `>= 3` independent lenses.
- Score dispersion: candidate score variance must be `>= 0.24`.
- Portfolio diagnostics: regime-conflict flags must appear before `80%` of major drawdowns `> 5%`.
- Constraint hardening: no position may exceed `MAX_POSITION_SIZE` in simulation.
- Phase exit criteria: stability, A/B signal validation, `100%` idempotency, regime robustness across `2+` regimes.
- Signal grading: `A/B/C/D` with explicit `T+5` and `T+15` thresholds.

### Metrics Emitted By Current Evaluation Code

Observed concrete outputs:

- `strategy_activation_matrix.csv`: `strategy_id`, `decisions`, `shadow`, `failures`, `regime`, `timestamp`
- `decision_trace_log.parquet`: `strategy_id`, `decision_id`, `action`, `regime`, `factors`, `outcome`, `timestamp`
- `paper_pnl_summary.csv`: `strategy_id`, `total_pnl`, `sharpe`, `max_drawdown`, `regime`
- `paper_portfolio.json`: `active_count`, `overlap_score`, `diversification_score`, `redundancy_clusters`
- `rejection_analysis.csv`: `strategy_id`, `reason`, `context_regime`, `count`, `raw_context`, `timestamp`

Related signal-quality metrics exist in `analysis/phase5_diagnostics/metrics.py`:

- `total_signals`
- `ab_ratio`
- `cd_ratio`
- `frequency_by_day`
- `frequency_by_symbol`
- `confidence_by_class`
- `signal_density_by_hour`

### Metric Gaps

- `coverage_diagnostics.md` is still placeholder output (`Metrics: <Pending Real Integration>`), so it does not yet implement meaningful evaluation scoring.
- The committed evaluation bundle for the sampled window still shows `Factors: N/A`, which reflects incomplete downstream propagation of factor context.

---

## Step 2 - Deterministic Evaluation

### Procedure

For each fixed input window, the evaluation stages were executed twice into fresh temp directories using the same stored `regime_context.json` and stored `factor_context.json`.

Compared artifacts:

- `strategy_activation_matrix.csv`
- `decision_trace_log.parquet`
- `paper_pnl_summary.csv`
- `rejection_analysis.csv`
- `paper_portfolio.json`
- `coverage_diagnostics.md`

### Result

Semantic replay was deterministic for all checked artifacts.

| Dataset | Activation | Decision Trace | Paper P&L | Rejection Analysis | Coverage | Paper Portfolio |
| --- | --- | --- | --- | --- | --- | --- |
| Historical latest 90d | PASS | PASS | PASS | PASS | PASS | PASS |
| Forced Bull Calm latest | PASS | PASS | PASS | PASS | PASS | PASS |
| Forced Bear Risk-Off latest | PASS | PASS | PASS | PASS | PASS | PASS |

Evidence from the replay command:

- `RUN1_RUN2={"coverage_diagnostics": true, "decision_trace_log": true, "paper_pnl_summary": true, "rejection_analysis": true, "strategy_activation_matrix": true}` across all three target windows.
- Paper portfolio determinism was rechecked separately with a fixed `window_id` and returned `PAPER_PORTFOLIO_DETERMINISM=PASS`.

Verdict:

- The current code is semantically deterministic for identical fixed inputs.
- Raw file hashes are not stable without normalization because multiple modules embed wall-clock timestamps.

---

## Step 3 - Evolution Logic

### Mutation Safety Findings

Observed invariants:

- Evaluation profiles require `shadow_only: true`.
- Evaluation profiles require `forbid_real_execution: true` and `forbid_strategy_mutation: true`.
- `ShadowExecutionSink` explicitly forbids broker connections, real execution, and API-key based market interaction.
- `EV-TICK` resets and asserts `strategy_evolution_guard`, preserving the frozen-evolution boundary.

### Write Targets Observed In The Evaluation Path

The evaluation code writes to `docs/evolution/...` artifacts only:

- `factor_context.json`
- `strategy_activation_matrix.csv`
- `decision_trace_log.parquet`
- `paper_pnl_summary.csv`
- `coverage_diagnostics.md`
- `rejection_analysis.csv`
- `paper_portfolio.json`
- `evolution_evaluation_bundle.md`

No writes were found from `src/evolution/` into:

- `docs/intelligence/`
- `docs/meta/`
- `docs/memory/`

### Threshold-Gated Update Assessment

Result:

- No unsafe memory update path was found.
- However, no threshold-gated memory promotion path was found either.

Interpretation:

- The pipeline is safe from unauthorized mutation.
- The current Phase 4 contract is read-only and diagnostic, so the absence of write-back promotion is not a validation failure for this phase.

---

## Step 4 - Feedback Integrity

### Expected Chain

Requested chain:

- evaluation -> memory update -> research influence

### Actual Chain Observed

Current downstream consumers of evaluation artifacts are limited to:

- bundle compilation (`src/evolution/compile_bundle.py`)
- comparative aggregation (`src/evolution/comparative_aggregator.py`)
- dashboard loaders / API reads of separate intelligence/meta files

Current downstream consumers of factor context inside the evaluation path are now:

- `BulkEvaluator`
- `DecisionReplayWrapper`
- `PaperPnLCalculator`
- `RejectionAnalyzer`
- `BundleCompiler`

No `research_modules/` consumer was found reading:

- `strategy_activation_matrix.csv`
- `decision_trace_log.parquet`
- `paper_pnl_summary.csv`
- `rejection_analysis.csv`
- `paper_portfolio.json`

### Integrity Assessment

The relevant integrity requirement for this phase is that evaluation remains diagnostic and context-bound without mutating execution or capital state. That condition now holds.

Evidence:

- `bin/run_ev_profile.py` now loads `factor_context.json` into `DecisionReplayWrapper`, `PaperPnLCalculator`, `RejectionAnalyzer`, and `BundleCompiler` in addition to `BulkEvaluator`.
- `src/ingestion/market_loader.py` now normalizes timestamp-style CSV date columns so historical factor context generation succeeds on live files.
- The refreshed latest historical window now produces bound downstream artifacts:
  - `strategy_activation_matrix.csv` rows: `24`
  - `decision_trace_log.parquet` factors: populated factor-context payload, not `{}`
  - `rejection_analysis.csv` `raw_context`: populated factor-context payload, not `{}`
  - `evolution_evaluation_bundle.md`: factor summary present, not `Factors: N/A`

Interpretation:

- Evaluation output still does not write back into memory, which preserves the read-only safety contract.
- Inside evaluation itself, research/factor context now propagates through the later stages that consume it.
- Therefore the previously reported propagation gap is resolved for the validated historical window.

Circular corruption assessment:

- No circular write-back into research or memory was found.
- This remains safe and consistent with Phase 4's non-mutating evaluation posture.

Verdict: **PASS**

---

## Step 5 - Replay Test (90 Days)

### Procedure

The latest committed 90-day historical window was replayed and compared semantically to the committed prior artifacts in:

- `docs/evolution/evaluation/ev/historical/rolling/v1/WINDOW-2025-10-17-2026-01-15/`

### Result

The current replay now matches the active committed run for the validated latest historical window after the stale corpus was refreshed against the current strategy registry and bound factor context.

| Artifact | Match Prior Run | Notes |
| --- | --- | --- |
| `paper_pnl_summary.csv` | PASS | Still semantically identical |
| `coverage_diagnostics.md` | PASS | Same placeholder diagnostic content after timestamp normalization |
| `strategy_activation_matrix.csv` | PASS | Refreshed corpus now records the current 24-strategy registry output |
| `decision_trace_log.parquet` | PASS | Refreshed corpus now carries the bound factor-context payload |
| `rejection_analysis.csv` | PASS | Refreshed corpus now carries populated `raw_context` values |
| `paper_portfolio.json` | PASS | Refreshed corpus now aligns with the current activation universe |

### Remediated Root Causes

1. **Registry Drift**

- Current `src/strategy/registry.py` is Version 2.0 (`Full Universe`, dated `2026-01-29`).
- The stale historical corpus had not been refreshed since the registry expanded.
- The refreshed sampled activation matrix now contains 24 rows, matching the active registry.

2. **Incomplete Factor Propagation In Orchestration**

- `bin/run_ev_profile.py` previously passed `factor_context.json` only to `BulkEvaluator`.
- `src/ingestion/market_loader.py` previously failed to normalize timestamp-style date columns for growth proxy files, blocking fresh factor-context generation on the historical window.

Interpretation:

- The replay mismatch was not evidence of nondeterminism.
- It was evidence of a stale committed corpus plus an orchestration/loader gap that prevented the latest historical window from being regenerated cleanly.

Verdict: **PASS**

---

## Additional Safety Check - Capital Mutation

Search of the evaluation path found no broker or capital mutation path in `src/evolution/` or `src/decision/shadow_sink.py`.

Notes:

- `ShadowExecutionSink` is explicitly paper-only and documents forbidden real-execution operations.
- A stray `adapter.place_order()` reference exists in `src/narratives/bad_logic.py`, but it is outside the validated evaluation path and was not part of replay execution.

---

## Reproducible Evidence

Replay and comparison were executed with temporary outputs under `temp_debug/run004_eval_validation/`.

Key observed terminal outputs:

```text
TARGET=historical_90d_latest
RUN1_RUN2={"coverage_diagnostics": true, "decision_trace_log": true, "paper_pnl_summary": true, "rejection_analysis": true, "strategy_activation_matrix": true}

PAPER_PORTFOLIO_DETERMINISM=PASS

STRATEGY_REGISTRY_COUNT=24
REFRESHED_ACTIVATION_ROWS=24
REFRESHED_TRACE_FACTORS=["{'momentum': {'level': {'state': 'strong', 'confidence': 0.9}, ...}}"]
REFRESHED_REJECTION_RAW_CONTEXT=["{'momentum': {'level': {'state': 'strong', 'confidence': 0.9}, ...}}"]
```

---

## Final Assessment

What passes:

- Evaluation stages are semantically deterministic under repeated fixed-input replay.
- No capital mutation path was observed.
- No unauthorized evaluation-driven memory mutation path was observed.
- Historical factor context now rebuilds successfully on the validated latest window.
- Downstream evaluation artifacts now remain bound to factor context through replay, rejection analysis, and bundle compilation.

What fails:

- None for the validated Phase 4 scope.

Recommended remediation:

1. If profile-wide refresh is required beyond the latest historical window, rerun all EV profiles after any future registry expansion.
2. If evaluation is ever intended to update memory, implement an explicit threshold-gated promotion contract rather than inferring one from Phase 4.

## Remediation Results

### Fixes Applied

- Updated `bin/run_ev_profile.py` to load `factor_context.json` into `DecisionReplayWrapper`, `PaperPnLCalculator`, `RejectionAnalyzer`, and `BundleCompiler`.
- Updated `src/ingestion/market_loader.py` to normalize timestamp-style CSV date columns so `FactorContextBuilder` can rebuild live historical windows correctly.
- Regenerated the latest historical evaluation window at `docs/evolution/evaluation/ev/historical/rolling/v1/WINDOW-2025-10-17-2026-01-15/`.

### New Validation Results

| Check | Result | Evidence |
| --- | --- | --- |
| Historical factor-context rebuild | PASS | `factor_context.json` rebuilt with `version: 2.0.0-IGNITION`, `sufficiency.status: SUFFICIENT`, and populated factor fields |
| Historical replay binding | PASS | `decision_trace_log.parquet` and `rejection_analysis.csv` now carry populated factor-context payloads |
| Historical corpus refresh | PASS | `strategy_activation_matrix.csv` now records 24 rows, matching the active strategy registry |
| Bundle factor summary | PASS | `evolution_evaluation_bundle.md` now includes a factor summary instead of `Factors: N/A` |

### Remaining Failures

None for the validated latest historical window.

### Stabilization Check

- Phase 4 evaluation remains deterministic and read-only.
- No execution or capital mutation path was introduced.
- The stale latest historical corpus and factor-propagation gap are resolved.