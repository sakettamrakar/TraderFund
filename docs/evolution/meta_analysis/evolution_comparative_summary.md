# Evolution Comparative Summary: EV-RUN Evidence Synthesis

**Date**: 2026-01-25
**Architect**: Principal Research Synthesis & Evidence Evaluation Architect
**Profiles Analyzed**: `EV-HISTORICAL-ROLLING-V1`, `EV-FORCED-BULL-CALM-V1`, `EV-FORCED-BEAR-RISKOFF-V1`
**Total Windows**: 105 (35 Historical, 35 Forced Bull, 35 Forced Bear)
**Context State**: `Factor Context` Bound (Neutral State)

---

## 1. Executive Summary

This meta-analysis synthesizes evidence from 70 window-level evaluation bundles across two distinct Evaluation Profiles. The objective is to identify consistent behavioral patterns, surface latent fragilities, and determine regime dependence across the current strategy portfolio.

### Key Findings (Comparative)
1.  **Regime Sensitivity Confirmed**: `STRATEGY_MOMENTUM_V1` (and `STRICT`) correctly rejected all "Volatile" and "Bear" windows.
2.  **Factor Context v1.1 Resolution**:
    *   **Baseline (`V1`)**: Rejects with `FACTOR_REQ_MOMENTUM_LEVEL_NEUTRAL` (or `WEAK` if fallback).
    *   **Strict (`STRICT`)**: Rejects with `FACTOR_REQ_MOMENTUM_ACCEL_FLAT` (primary constraint violation).
    *   **Accelerating (`ACCELERATING`)**: Rejects with `FACTOR_REQ_MOMENTUM_ACCEL_FLAT` (proving it looked for acceleration).
    *   **Persistent (`PERSISTENT`)**: Rejects with `FACTOR_REQ_MOMENTUM_PERSIST_INTERMITTENT` (proving it looked for persistence).
3.  **Graceful Degredation**: No strategy forced a trade in unsafe regimes. `VALUE_QUALITY` remains robust.

### Momentum Family Evolution (New)
The successful specialization of Momentum strategies demonstrates the power of Factor Context v1.1 resolution.
*   **Differentiation**: Variants failed for *different* reasons, validating their distinct logic.
    *   `STRICT` failed on Acceleration (Flat).
    *   `PERSISTENT` failed on Persistence (Intermittent).
*   **Safety**: Even "looser" intent strategies (`ACCELERATING`) did not fire unsafely because the granular factor (Acceleration) was also negative (Flat).
*   **Conclusion**: We have successfully decoupled "Momentum" into precise, observable behaviors without logic injection.

---

## 2. Strategy-by-Strategy Analysis

### STRATEGY_MOMENTUM_V1
**Status**: 🟡 REGIME-DEPENDENT

- **Observed Patterns**: exhibits high rejection frequency (15.00) specifically attributed to `FACTOR_MOMENTUM_NEUTRAL_FLAT`.
- **Regime Behavior**: Rejection reason has successfully migrated from "Permissibility" (Regime) to "Suitability" (Factor), and now to "Causal Detail" (v1.1). The strategy effectively communicates: "Momentum is Neutral AND Acceleration is Flat".
- **Rationale**: The strategy appears to require more specific momentum conditions than a broad regime label provides. The system now *explains* this gap with high precision.

### STRATEGY_VALUE_QUALITY_V1
**Status**: 🟢 ROBUST

- **Observed Patterns**: 100% activation rate with zero rejections across all 70 windows.
- **Regime Behavior**: Behavior is identical in both Historical (observed) and Forced (BULL_CALM) profiles.
- **Rationale**: The strategy logic appears universally applicable within the evaluated bullish regimes, showing zero friction with the current context.

### STRATEGY_FACTOR_ROTATION_V1
**Status**: 🟢 ROBUST

- **Observed Patterns**: Consistent 1.0 activation rate and zero rejections.
- **Regime Behavior**: Stable across rolling windows with low variance in shadow fill rates.
- **Rationale**: Exhibits high alignment with both observed and forced regime state, suggesting its factor selection logic is well-bound to the authoritative regime context.

---

## 3. Comparative Analysis: Historical vs. Forced

| Analysis Dimension | Findings |
|:-------------------|:---------|
| **Divergence** | In the current evaluation cycle, behavior between Historical and Forced profiles shown unexpected parity. This indicates that for the windows analyzed, the observed `BULL_VOL` historical state produced similar strategy responses to the forced `BULL_CALM` state. |
| **Latent Fragility** | `STRATEGY_MOMENTUM_V1` showed identical rejection rates in both profiles. This suggests the volatility delta between `BULL_VOL` and `BULL_CALM` is not the primary driver of rejections; rather, a deeper factor alignment issue exists. |
| **False Robustness** | Strategies appearing robust in `BULL_VOL` also appeared robust in forced `BULL_CALM`. This cross-profile consistency increases confidence that their robustness isn't merely a byproduct of detection noise. |

---

## 4. Behavior Under Bear / Risk-Off Stress

The introduction of `EV-FORCED-BEAR-RISKOFF-V1` provides the first counterfactual evidence of strategy behavior under significant market stress.

### Graceful Failure vs. Collapse
- **STRATEGY_MOMENTUM_V1**: Maintains its "Fragile" status but fails gracefully. It continues to issue `FACTOR_MOMENTUM_NEUTRAL_FLAT` rejections (15 per window) rather than attempting unsafe execution or inverting logic. The rejection mechanism successfully prevents capital exposure in adverse conditions.
- **STRATEGY_VALUE_QUALITY_V1**: Demonstrates remarkable stability. It remains `ROBUST` with 0 rejections, suggesting its valuation and quality factors are effectively regime-agnostic or correctly identify defensive opportunities even in a Bear context.

### Inversion Analysis
- No strategies inverted their behavior (e.g., switching from Long to Short) implicitly. All behavior remained consistent with their core logic, either rejecting or accepting trades based on factor presence.

---

## 5. Regime × Strategy Observations

- **Bull Volatile (BULL_VOL)**: Serves as the primary operational baseline. Momentum strategies experience significant internal friction here.
- **Bull Calm (BULL_CALM)**: Forced evaluation shows that even in "perfect" conditions, certain strategies (Momentum) still exhibit validation friction.
- **Bear / Risk-Off (BEAR_RISK_OFF)**: Stress testing confirms that defensive interactions are handled via explicit rejection (Momentum) or persistent robustness (Value/Quality), proving that the "Safety Valve" mechanisms function correctly under pressure.

---

## 6. What This Does NOT Mean

> [!IMPORTANT]
> - **No Optimization**: This analysis does not suggest "fixing" or "tuning" parameters to increase activation rates.
> - **No Performance Promises**: `paper_pnl` mean values (0.0000 in this phase) are purely diagnostic and do not represent expected returns.
> - **No Live Readiness**: Robustness in simulation does not equate to market readiness. High activation in shadow mode is a PREREQUISITE for live consideration, not a SUFFICIENT condition.

---

## 7. Momentum Emergence Diagnostics (v1.2)

With the enrichment of Factor Context to v1.2, we now observe granular "textures" of momentum beyond simple levels.

### Diagnostic Signatures
Analyzing 105 windows across all profiles:

1.  **Breadth State**: consistently `NARROW`.
    *   *Interpretation*: Momentum is not broad-based; confirming the "Neutral" top-level assessment.
2.  **Dispersion**: consistently `STABLE`.
    *   *Interpretation*: Returns are not expanding (which would indicate leadership emergence) nor contracting significantly.
3.  **Time-in-State**: consistently `MEDIUM`.
    *   *Interpretation*: The current neutral/flat state is entrenched, not a fleeting transition.

### Meta-Alignment
*   **Quality**: Classified as `NOISY`.
*   **Correlation**:
    *   High correlation between `ACCELERATION: FLAT` and `BREADTH: NARROW`.
    *   This confirms that the absence of momentum is structural (broad market apathy) rather than specific (single sector failure).

**Conclusion**: Momentum is currently **ABSENT/NOISY**. It is not "forming" (which would show `ACCELERATING` + `EXPANDING`). Strategies correctly reject this environment.

## 8. Momentum Emergence Timeline (Watcher)

The `MomentumEmergenceWatcher` (EV-WATCH-MOMENTUM) confirms the above diagnostics with explicit state tracking.

### Emergence States Observed
*   **NONE**: 100% of windows.
*   **EMERGING_ATTEMPT**: 0%
*   **EMERGING_CONFIRMING**: 0%
*   **EMERGING_PERSISTENT**: 0%

### Interpretation
The Watcher detected zero structural attempts at momentum formation in the evaluated historical or forced windows.
*   **Why no Attempts?** `time_in_state` was consistently `MEDIUM`, meaning the "Flat/Neutral" state is entrenched. An "Attempt" requires `acceleration=accelerating` AND `time_in_state=short` (a fresh move).
*   **System Integrity**: The Watcher output (`momentum_emergence.json`) was generated for all 105 windows without interrupting execution.

---

## 9. Alpha Environment & Compression Diagnostics (v1.3)

With the enrichment of Factor Context to v1.3 and the Liquidity Watcher, we can diagnose the *structure* of the current alpha void.

### A. Alpha-Friendly Environment
*   **Observations**:
    *   **Value Dispersion**: `STABLE`. This indicates no widening of valuation spreads, which suppresses the opportunity set for Value strategies.
    *   **Mean Reversion Pressure**: `LOW`. Extreme valuations are not reverting, reducing the efficacy of mean-reversion alpha.
    *   **Quality Defensiveness**: `NEUTRAL`. Quality assets are not decoupling from the broad market, reducing their utility as a hedge.
*   **Conclusion**: The environment is **MIXED**. It is not hostile to Value/Quality (as proven by their robustness), but it lacks the *dispersion* required for outsized alpha generation.

### B. Compression → Expansion Diagnostics
The `LiquidityCompressionWatcher` provides the missing link for Momentum's absence.

*   **Compression State**: `NEUTRAL` (across all windows).
*   **Diagnostic**:
    *   The market is NOT in a `COMPRESSED` state (coiling for a move).
    *   The market is NOT in an `EXPANDING` state (realizing volatility).
    *   It is structurally **stagnant**.
*   **Causal Link**: Momentum requires *expansion* of volatility and dispersion. The persistent `NEUTRAL` liquidity state explains why `MomentumEmergenceWatcher` sees zero attempts. The engine of momentum (expansion) is idling.

---

## 10. Readiness Dashboard (Path 1)
Using the newly integrated `EV-WATCH-EXPANSION` and `EV-WATCH-DISPERSION`.

### A. Expansion Transition
*   **State Observed**: `NONE`.
*   **Significance**: The market remains in the "Stagnation Trap". Volatility is not expanding, meaning transition to a high-opportunity regime is not yet occurring.

### B. Dispersion Breakout
*   **State Observed**: `NONE`.
*   **Significance**: Opportunity sets are not widening. This confirms that attempting to scale alpha capture now would yield diminishing returns.

**Readiness Verdict**: **NOT READY**. The system must remain in "Wait-and-Diagnosis" mode.

---

## 11. Portfolio Interaction Map (Path 2)
Counterfactual analysis using `EV-PORTFOLIO-PAPER`.

### A. Overlap Analysis
*   **Metrics**:
    *   **Average Overlap Score**: `0.0` (Perfect Diversification / Isolation).
    *   **Redundancy Clusters**: None detected.
*   **Interpretation**: Since momentum strategies are largely inactive (rejecting), there is zero overlap with active Value/Quality strategies. The portfolio is currently **Partitioned** by regime.

### B. Structural Validity
The paper portfolio construction confirms that should momentum activate, it would do so in a regime distinct from the current one, minimizing risk correlation.

---

## 12. Governance & Traceability

- **Evidence Source**: [evolution_metrics_table.csv](file:///c:/GIT/TraderFund/docs/evolution/meta_analysis/evolution_metrics_table.csv)
- **Evaluation Profiles**: [EV-HISTORICAL-ROLLING-V1](file:///c:/GIT/TraderFund/docs/evolution/evaluation_profiles/EV-HISTORICAL-ROLLING-V1.yaml), [EV-FORCED-BULL-CALM-V1](file:///c:/GIT/TraderFund/docs/evolution/evaluation_profiles/EV-FORCED-BULL-CALM-V1.yaml), [EV-FORCED-BEAR-RISKOFF-V1](file:///c:/GIT/TraderFund/docs/evolution/evaluation_profiles/EV-FORCED-BEAR-RISKOFF-V1.yaml)
- **Decision Authority**: D013 (Decision Plane Authorization)
- **Audit Hash**: [Calculated per system policy]

---

## 13. Passive Time Progression Log (EV-TICK)

The system now supports passive time advancement via `EV-TICK`. This mechanism runs diagnostic watchers without triggering strategy execution or capital allocation.

*   **Log Location**: [evolution_log.md](file:///c:/GIT/TraderFund/docs/epistemic/ledger/evolution_log.md)
*   **Traceability**: Each tick is logged with timestamp, watcher states, and action (which is strictly NONE).
*   **Artifacts**: Per-tick artifacts are stored in `docs/evolution/ticks/`.
