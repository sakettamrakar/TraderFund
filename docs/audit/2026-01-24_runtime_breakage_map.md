# Runtime Breakage Map: Trader Fund Pipeline

**Auditor**: System Tester
**Date**: 2026-01-24
**Objective**: Execute pipeline end-to-end and report breaks.

---

## STEP 1: INPUT INGESTION EXECUTION

**Status**: ✅ **PASSED**

| Input | Source | Status | Notes |
| :--- | :--- | :--- | :--- |
| Market Data (India) | Angel SmartAPI | OK | Ran via `pipeline_dry_run.py` |
| US Market Data | Alpha Vantage | OK | `run_us_regime.py` fetched SPY |

**Stale Inputs**: Not tested (would require historical replay).
**Missing Inputs**: RSS/News feeds not tested in this run.

---

## STEP 2: FEATURE GENERATION EXECUTION

**Status**: ✅ **PASSED**

*   Intraday Candle Processing ran successfully.
*   Parquet files confirmed in `data/processed/candles/`.

**Orphaned Features**: Not verified (requires downstream consumer audit).

---

## STEP 3: SIGNAL LAYER EXECUTION

**Status**: ✅ **PASSED**

*   Momentum Engine executed successfully.
*   Signals generated (confirmed via `pipeline_dry_run.py`).

**Unstable Signals**: Not verified (no contradiction audit run).

---

## STEP 4: REGIME CLASSIFICATION EXECUTION

**Status**: ⚠️ **SOFT BREAK**

*   `run_us_regime.py` executed successfully (no crash).
*   **Output**: `[US REGIME] SPY | UNDEFINED | Bias=NEUTRAL | Conf=0.23`
*   **Problem**: Regime is `UNDEFINED` with very low confidence.
*   **Impact**: All downstream logic that depends on "Regime" gets a non-answer.

**Verdict**: Pipeline runs but **lies** (produces output that is effectively meaningless).

---

## STEP 5: NARRATIVE INTEGRATION EXECUTION

**Status**: ❌ **HARD BREAK**

*   Narrative engine code exists (`narratives/genesis/engine.py`).
*   **No CLI entry point** found to run narrative construction against live/fetched data.
*   `scripts/run_market_story_shadow.py` exists but was not tested (requires Kafka).

**Verdict**: Pipeline **STOPS HERE** for unified execution. No runnable Narrative step without manual orchestration.

---

## STEP 6: DECISION ARTIFACT EXECUTION

**Status**: ❌ **HARD BREAK (Cascading)**

*   Cannot test Decision output because Narrative input is unavailable.
*   No `DecisionEngine` or equivalent CLI found.
*   **DO NOTHING**: Cannot confirm if this is a valid output state.

**Verdict**: Pipeline does not reach this stage.

---

## BREAKAGE MAP SUMMARY

| Category | Component | Description |
| :--- | :--- | :--- |
| **A. Hard Breaks** | Narrative Layer | No CLI runner for unified execution. |
| | Decision Artifact | Cannot execute; depends on Narrative. |
| **B. Soft Breaks** | Regime Classifier | Runs but returns `UNDEFINED` / low confidence. |
| **C. Silent Failures** | Orphaned Features | Features may exist but never consumed. |
| | Regime Impact | `UNDEFINED` regime does not halt downstream consumers. |
| **D. Orphaned Components** | `scripts/run_market_story_shadow.py` | Exists but requires Kafka (untested). |

---

## STEP 8: RUN VERDICT

**How far does the pipeline run today?**
*   Ingestion → Features → Signals: **OK**
*   Regime: **Degrades** (Runs but output is garbage)
*   Narrative: **STOPS**
*   Decision: **NEVER REACHED**

**Where does it first break?**
*   **Step 4 (Regime)** is the first **functional break** (output is meaningless).
*   **Step 5 (Narrative)** is the first **structural break** (no executable path).

**Which stages are real vs theatrical?**
| Stage | Real / Theatrical |
| :--- | :--- |
| Ingestion | Real |
| Feature Gen | Real |
| Signals | Real (but unconsumend?) |
| Regime | **Theatrical** (runs but lies) |
| Narrative | **Theatrical** (code exists, no CLI) |
| Decision | **Non-Existent** |

**Is the pipeline trustworthy for...**
| Use Case | Verdict |
| :--- | :--- |
| Observation Only | ⚠️ Partial (Ingestion + Signals OK, Regime unreliable) |
| Paper Decisions | ❌ **NO** - Narrative/Decision path broken |
| Real Capital | ❌ **ABSOLUTELY NOT** |

---

**FINAL STATEMENT**: The pipeline is a **well-constructed body with no functioning brain**. Inputs flow, signals fire, but the system cannot explain the narrative or produce a decision. The Regime layer is a shell that produces output without actually classifying anything useful.

**No improvements suggested. This is runtime truth.**
