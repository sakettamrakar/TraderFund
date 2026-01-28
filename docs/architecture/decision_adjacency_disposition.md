# Decision-Adjacency Disposition Report

**Authority**: `ARCH-1.5`
**Status**: APPROVED
**Date**: 2026-01-30

## 1. Executive Summary
The Decision-Adjacency Audit identified **13 key artifacts** exhibiting decision-like behavior. The system clearly distinguishes between **Research (Truth)** and **Intelligence (Suggestion)**, but several artifacts currently living in shared spaces (`src/core_modules`) or research spaces (`signals/`) exhibit "Intelligence" behavior (symbol selection, ranking, flagging).

These artifacts have been classified for migration to a formal **Ring-3 Intelligence Layer** to ensure Ring-1 remains purely descriptive.

## 2. Disposition Counts

| Disposition | Count | Description |
| :--- | :--- | :--- |
| 🟢 **KEEP** | 5 | Valid Ring-1 Research or Operational Logic. |
| 🔵 **MIGRATE** | 7 | Symbol-level intelligence to be moved to Ring-3. |
| 🟡 **FREEZE** | 1 | Legacy/Dormant logic to be preserved but disabled. |
| 🔴 **DELETE** | 0 | No safe-to-delete artifacts found. |

## 3. Rationale
*   **Migration to Ring-3**: The `Momentum Engine`, `Watchlist Builder`, and `Signal Discovery` components are actively selecting and flagging symbols. This is **Intelligence**, not pure Research. They must be formally encased in the Intelligence Layer.
*   **Operational Logic**: The `Pipeline Controller` makes "decisions" about compute resource allocation. This is a valid operational concern and stays in Ring-1/Ops.
*   **Safety Gates**: `Strategy Gate` and `Universe Hygiene` filters are exclusion mechanisms (safety), not inclusion mechanisms (selection). They remain in Ring-1.

## 4. Disposition Inventory

### 🟢 KEEP (Ring-1 Research / Ops)
*   **Pipeline Controller** (`research_modules/pipeline_controller/`): Operational efficiency logic.
*   **Universe Hygiene** (`research_modules/universe_hygiene/`): Data quality filtration (Exclusion).
*   **Strategy Gate** (`traderfund/regime/gate.py`): Safety/Risk gating (Exclusion).
*   **Dispersion Watcher** (`src/evolution/watchers/dispersion_breakout_watcher.py`): Market state description.
*   **Historical Replay** (`historical_replay/momentum_intraday/`): Research verification tool.

### 🔵 MIGRATE (Future Ring-3 Intelligence)
*   **Momentum Engine** (`src/core_modules/momentum_engine/`): Generates trade signals.
*   **Watchlist Builder** (`src/core_modules/watchlist_management/`): Selects symbols for attention.
*   **Technical Scanner** (`src/pro_modules/strategy_engines/technical_scanner.py`): Scans for technical setups.
*   **Decision Engine Core** (`src/decision/engine.py`): The central decision processor.
*   **Signal Discovery** (`signals/discovery/runner.py`): Generates alpha signals.
*   **Confidence Scorer** (`signals/confidence_engine/scorer.py`): Ranks signals by quality.
*   **Narrative Accumulator** (`narratives/genesis/accumulator.py`): Promotes signals to narratives.

### 🟡 FREEZE (Legacy / Dormant)
*   **Legacy India Logic** (`src/data_ingestion/`): While data ingestion is active, any embedded selection logic in old scripts should be considered frozen in favor of the new `Momentum Engine`.

### 🔴 DELETE (Safe to Remove)
*   *None identified in this pass.*

## 5. Risk Avoidance
By explicitly explicitly labeling `Momentum Engine` and others as **Intelligence** (MIGRATE), we avoid the risk of "Truth Decay" where research modules start subtly recommending trades. Ring-1 remains the "Source of Truth" (What is the regime?), while Ring-3 becomes the "Source of Action" (What should we trade?).
