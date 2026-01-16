# Regime Engine — Improvement & Integration Control Plan
**Version:** 1.0.0
**Status:** DRAFT
**Governs:** Phases 6 through 11 (Post-Core Evolution)

---

## 1. Purpose of the Improvement Plan

The Core Regime Engine (Phases 0–5) provides a deterministic, stateless, and observable classification of market behavior. However, a model is not a production system.

The purpose of this document is to strictly govern the **integration, validation, and enhancement** of the Regime Engine into the live trading ecosystem. Direct, unchecked integration poses significant risks:
1.  **Over-Blocking:** A miscalibrated regime engine can halt profitable strategies unnecessarily.
2.  **Latency:** Inefficient integration can introduce slippage.
3.  **Flickering:** Rapid state changes can churn positions.

This plan enforces a **"Shadow First, Gate Later"** approach, ensuring that the engine proves its value by preventing losses in simulation before it is allowed to block trades in production.

---

## 2. Global Constraints

### 2.1 Immutable Core
The following components are **FROZEN** and must **NEVER** be modified during integration:
*   `traderfund/regime/types.py`: All Enums and Pydantic models.
*   `traderfund/regime/core.py`: The State Machine logic (hysteresis, cooldown).
*   `traderfund/regime/calculator.py`: The Decision Tree logic.

### 2.2 Allowed Evolution
The following components may be tuned or extended:
*   `traderfund/regime/gate.py`: `StrategyCompatibilityMap` may be updated as strategies evolve.
*   `traderfund/regime/providers/*.py`: Provider implementations may be optimized for speed, but their interface contracts are immutable.
*   `traderfund/regime/observability.py`: Logging formats may be enriched.

### 2.3 Safety & Rollback
*   **Kill Switch:** A global mechanism must exist to disable the Regime Engine and revert to "Legacy Mode" (ignoring regimes) instantly.
*   **Shadow Mode:** Every new integration must run in "Shadow Mode" (logging only) for at least 1 trading session before "Enforcement Mode" (blocking).

---

## 3. Integration Surfaces

To maintain modularity, we define strict boundaries:

1.  **Strategy Engines (Consumer)**
    *   **Role:** Request permission to trade.
    *   **Interaction:** Calls `StrategyGate.evaluate(current_regime, strategy_class)`.
    *   **Restriction:** MUST NOT access raw indicators or calculating logic directly.

2.  **Signal Generators (Input)**
    *   **Role:** Provide market data ticks/bars.
    *   **Interaction:** Feeds data to `Provider` instances.
    *   **Restriction:** Providers must remain stateless.

3.  **Dashboards (Observer)**
    *   **Role:** Visualize current state.
    *   **Interaction:** Consumes JSON from `RegimeFormatter`.
    *   **Restriction:** Read-only access.

4.  **Logging & Telemetry (Auditor)**
    *   **Role:** Record decisions for regret analysis.
    *   **Interaction:** Stores structured logs of `(State, Decision, PnL if taken)`.

---

## 4. Phase Breakdown

### Phase 6: Shadow Mode & Telemetry
**Objective:** Deploy the Regime Engine alongside live trading without affecting execution, to validate stability and data flow.
**Scope:**
*   Instantiate `RegimeEngine` in the main trading loop.
*   Feed live data to Providers.
*   Log `RegimeState` to a dedicated `regime.log`.
*   **CRITICAL:** Do NOT use the output to block or size trades.
**Accepted Criteria:**
*   Engine runs for 1 full session without crashing.
*   Logs show rational state transitions (no sub-second flickering).
*   Latency impact is < 5ms per tick.

### Phase 7: India Momentum Integration
**Objective:** Enforce Regime Gating on the `IndiaMomentum` strategy suite.
**Scope:**
*   Modify `MomentumStrategy` execution logic to poll `StrategyGate`.
*   **Action:** If `IS_ALLOWED` is False, skip signal generation.
*   **Action:** If `SIZE_MULTIPLIER` < 1.0, reduce quantity.
**Forbidden:** Modifying the strategy's alpha logic.
**Rollback:** Disable gating if missed profitable trades > prevented losses.

### Phase 8: US Narrative Integration
**Objective:** Integrate Narrative/Event pressure into the Regime Engine.
**Scope:**
*   Connect `CalendarEventProvider` to the real Economic Calendar or News Feed.
*   Map news intensity to `IEventPressureProvider`.
*   Validate `EVENT_LOCK` vs `EVENT_DOMINANT` distinctions.
**Accepted Criteria:**
*   Engine correctly enters `EVENT_LOCK` 15 mins before High Impact news.
*   Engine cooldown releases correctly after news.

### Phase 9: Regime Dashboard (Decision-First)
**Objective:** Visualize the "Why" of the market state.
**Scope:**
*   Create a simple UI (Text or Web).
*   Display: Current Regime, Bias, Confidence, Blocker Status.
*   **Focus:** "Why am I blocked?" (e.g., "Blocked by HIGH_VOL").
**Forbidden:** Complex charting overlays or historical analysis features.

### Phase 10: Regime–Strategy Regret Analysis
**Objective:** Quantify the value of the Regime Engine.
**Scope:**
*   Analyze logs to compare:
    *   **Actual PnL:** Trades taken (or blocked) by Engine.
    *   **Counterfactual PnL:** Trades that *would* have been taken without Engine.
*   Metric: `Net_Losses_Prevented - Net_Profits_Missed`.
**Accepted Criteria:**
*   Positive "Regime Alpha" (Value Added).

### Phase 11: Controlled Enhancements (Optional)
**Objective:** Advanced capabilities (only after operational maturity).
**Scope:**
*   **Market Breadth:** Integrating Advance/Decline lines into Trend Provider.
*   **Correlation:** Using Sector correlation as a Confluence factor.
*   **ML:** *Experimental* replacement of fixed thresholds with dynamic ones (requires new Control Plan).

---

## 5. Execution Rules for Antigravity

1.  **Single Phase Focus:** You typically work on one phase per interaction. Do not jump ahead.
2.  **No Cross-Contamination:** When working on "Phase 7 (Integration)", do not refactor "Phase 2 (Calculator)".
3.  **Strict Adherence:** If a task violates "Forbidden" scopes, reject it.
4.  **Verification:** Every phase ends with a verification step (Test, Log Analysis, or Dry Run).

---

## 6. Success Criteria

The Regime Engine is considered **"Operationally Mature"** when:
1.  It is running live on at least 2 distinct asset classes (e.g., IN Equities, US Tech).
2.  It has prevented at least one major drawdown event (by blocking trades during a Shock/Crash).
3.  It operates with zero manual intervention for 5 consecutive trading days.
