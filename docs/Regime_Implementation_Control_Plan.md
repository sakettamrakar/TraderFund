# Regime Engine — Implementation Control Plan

**Version:** 1.0.0
**Project:** Market Regime Detection System
**Blueprint Ref:** v1.1.0
**Tech Spec Ref:** v1.1.0 (Impl Ready)
**Status:** ACTIVE

---

## 1. Purpose of the Control Plan
This document governs the sequential, deterministic implementation of the Market Regime Engine.

**Why Phased Execution Determines Success:**
*   **Isolation of Complexity:** Prevents "Big Ball of Mud" architecture by forcing module separation.
*   **Testability:** Each phase must pass 100% unit tests before the next phase begins.
*   **Dependency Management:** Ensures core abstractions exist before logic is built upon them.

**Risk of Skipping Phases:**
*   Implementing Strategy Gates (Phase 4) without a stable State Machine (Phase 3) guarantees unstable, flickering signals that will cause trading losses.
*   Implementing Logic (Phase 2) without Indicators (Phase 1) guarantees spaghetti code.

---

## 2. Global Constraints
These rules apply to **ALL** implementation phases.

1.  **Architecture:** The `Blueprint v1.1.0` is the Supreme Law. No deviations allowed.
2.  **Interface Frozen:** The `IProvider` interfaces defined in Spec v1.1.0 cannot be changed without a Spec Revision.
3.  **No Strategy Logic:** This engine outputs *State* only. It never outputs *Trades*.
4.  **No External Dependencies:** The engine must not depend on the specific Execution Engine or Broker API. It consumes *Data* and emits *State*.
5.  **Language:** Python 3.10+.
6.  **Libraries:** `numpy` (Core), `pandas` (Dataframes), `pydantic` (Validation).

---

## 3. Repository & Module Structure
The implementation lives in `traderfund/regime`.

```text
traderfund/
  └── regime/                 # ROOT
      ├── __init__.py
      ├── core.py             # Engine & StateManager
      ├── types.py            # Enums & Pydantic Models
      ├── providers/          # PROVIDER IMPLEMENTATIONS
      │   ├── __init__.py
      │   ├── base.py         # Interfaces (ABC)
      │   ├── trend.py
      │   ├── volatility.py
      │   ├── liquidity.py
      │   └── event.py
      ├── config/             # CONFIGURATION
      │   └── schema.py
      └── tests/              # TEST SUITE
          ├── test_providers.py
          ├── test_state_machine.py
          └── test_hysteresis.py
```

---

## 4. Phase Breakdown

### Phase 0: Preconditions & Freeze
**Objective:** Establish the workspace and freeze requirements.
*   **Scope:** 
    *   Create directory structure.
    *   Initialize `types.py` with Enums (BEHAVIOR, BIAS) and Pydantic Schemas.
    *   Create `base.py` Abstract Base Classes for Providers.
*   **Forbidden:** Implementing any actual logic (ADX/ATR).
*   **Inputs:** `Tech Spec v1.1.0` (Data Contracts).
*   **Outputs:** Validated project skeleton, type definitions.
*   **Acceptance:** `pytest` collects 0 tests but no import errors.

### Phase 1: Indicator Providers (Stateless)
**Objective:** Implement the stateless math components.
*   **Scope:**
    *   Implement `TrendProvider` (ADX, EMA).
    *   Implement `VolatilityProvider` (ATR Ratio).
    *   Implement `LiquidityProvider` (RVOL).
    *   Implement `EventProvider` (Calendar Logic).
*   **Forbidden:** State machine, Transition logic, Hysteresis.
*   **Inputs:** `types.py` (Phase 0).
*   **Outputs:** Working Provider classes.
*   **Acceptance:** Unit tests verify math accuracy against known inputs (Array In -> Float Out).

### Phase 2: Market-Level Regime (Calculator)
**Objective:** Implement the pure function that maps Providers -> Raw Regime.
*   **Scope:**
    *   Create `RegimeCalculator`.
    *   Implement logic tree: Data Check -> Event -> Liquidity -> Behavior -> Bias.
    *   Implement Conflict Resolution rules.
*   **Forbidden:** Hysteresis, Temporal Persistence.
*   **Inputs:** Providers (Phase 1).
*   **Outputs:** `RegimeCalculator` class.
*   **Acceptance:** Test cases cover all 7 Regime States + Directional Bias.

### Phase 3: Confidence & Hysteresis (State Machine)
**Objective:** Implement the stateful time-domain logic.
*   **Scope:**
    *   Create `StateManager`.
    *   Implement `update(tick)` loop.
    *   Implement `pending_counter` (Hysteresis).
    *   Implement `cooldown_timer`.
    *   Implement Confidence Composite Score (Confluence/Persistence/Intensity).
*   **Forbidden:** Connecting to Strategy Engine.
*   **Inputs:** Calculator (Phase 2).
*   **Outputs:** `RegimeEngine` main class.
*   **Acceptance:** Historical Replay Mock shows stable regimes (Flicker Rate < 5%).

### Phase 4: Strategy Gate Integration
**Objective:** Connect the Regime Engine to the Strategy logic.
*   **Scope:**
    *   Define `StrategyCompatibilityMap`.
    *   Implement `StrategyGate` class.
    *   Implement throttling logic (`allow`, `block`, `reduce_size`).
*   **Forbidden:** Changing Core Regime Logic.
*   **Inputs:** `RegimeEngine`.
*   **Outputs:** Interface for strategies to query permission.
*   **Acceptance:** Mock Strategy is correctly BLOCKED during `EVENT_LOCK` or `HIGH_VOL`.

### Phase 5: Observability & Dashboard
**Objective:** Visualize the "Hidden State" of the market.
*   **Scope:**
    *   Expose JSON endpoint / Log structure.
    *   Create simple Dashboard Widget (CLI or Web).
*   **Forbidden:** Core Logic Changes.
*   **Inputs:** `RegimeEngine` Output.
*   **Outputs:** Visualization.
*   **Acceptance:** Human can see: Regime, Confidence Breakdown, Event Status in <30 seconds.

---

## 5. Execution Rules for Antigravity

1.  **Single Phase Focus:** You typically execute ONE Phase per prompt. Do not jump ahead.
2.  **No Refactoring:** Unless a bug prevents progress, do not optimize code from previous phases.
3.  **Strict Adherence:** If the User asks for a "Quick Fix" that violates the Blueprint, **REFUSE** and cite this Control Plan.
4.  **Verification First:** Write the test *before* or *simultaneously* with the code.
