# Dashboard Work Specification (DWS): Trust & Scope

**Version:** 1.0.0
**Date:** 2026-01-30
**Status:** AUTHORITATIVE
**Epoch:** TRUTH_EPOCH_2026-01-30_01

---

## 1. Purpose & Scope

The TraderFund Dashboard serves as the primary **Epistemic Surface** of the system. It is not merely a visualization tool but the authoritative interface for observing the system's "belief state."

### Core Principles
1.  **Research-First:** The dashboard prioritizes the depth, provenance, and validity of research data over execution speed.
2.  **Execution-Sealed:** The dashboard reflects a system that is currently sealed from execution. It must clearly communicate *why* specific actions are blocked or allowed.
3.  **Trust & Provenance:** Every metric must have a traceable origin. "Magic numbers" are strictly prohibited. Users must be able to distinguish between authentic data, derived signals, and system artifacts.

## 2. Observed Issues (Audit Findings)

The following structural deficiencies have been identified in the current dashboard implementation:

1.  **Market Scope Applied Too Late:** The `market` parameter often filters data at the *component* level rather than the *root* level, leading to potential "leakage" or confusion (e.g., US macro displayed in India context).
2.  **Regime Semantic Ambiguity:** The term "Regime" is overloaded. It conflates the *Detected Regime* (what the data says) with the *Actionable Regime Gate* (what the system is allowed to do).
3.  **Macro Context Parity:** Macro indicators (VIX, Yields) are sometimes treated as global when they should be market-specific, or vice-versa, without clear explanation.
4.  **System Health NA:** The `SystemStatus` component frequently shows "N/A" or "Unknown" for health metrics that should be deterministically calculable, even if "Healthy."
5.  **Strategy State Hanging:** Strategies often appear in ambiguous states like "calculating" or "filtering" instead of distinct, terminal states (e.g., `ELIGIBLE`, `REJECTED`, `PENDING_DATA`).
6.  **Capital Readiness:** Capital allocation logic does not explicitly respect the market scope, implying capital might be deployed to a market that is not actually active.
7.  **Data Source Conflation:** The system previously obscured the difference between the *Proxy* (e.g., "US Market") and the *Source* (e.g., "SPY.csv"), leading to confusion when proxies were imperfect (e.g., Reliance representing India).

## 3. Market Proxy Sets

To resolve source conflation, we define explicit **Market Proxy Sets**. This separates the *concept* of the market from the *implementation* of its data.

### 3.1 US Market Proxy Set
*   **Primary Proxy:** S&P 500 (Broad Market)
*   **Data Source Implementation:** `data/regime/raw/SPY.csv`
*   **Usage:**
    *   **Regime Layer:** Determines Bull/Bear/Neutral state.
    *   **Factor Layer:** Momentum, Volatility baseline.
    *   **Liquidity Layer:** Volume baseline.
*   **Macro Proxies:** VIX (Volatility), TNX (Rates), HYG (Credit) [Implementation: Zero/Purged until wired].

### 3.2 India Market Proxy Set
*   **Primary Proxy:** NIFTY 50 (Broad Market)
*   **Temporary Data Source Implementation:** `data/raw/api_based/angel/historical/NSE_RELIANCE_1d.jsonl` (Explicitly noted as *Single-Stock Proxy* until Index data is available).
*   **Usage:**
    *   **Regime Layer:** Determines Bull/Bear/Neutral state.
    *   **Factor Layer:** Momentum (Single-stock proxy).
    *   **Liquidity Layer:** Volume (Single-stock proxy).
*   **Macro Proxies:** INDIA VIX, 10Y BOND [Implementation: None/Unknown].

### 3.3 Declaration Rule
The dashboard must explicitly state: *"Market [M] is observed via Proxy [P] using Source [S]."*

## 4. Data Anchor Panel Specification

The **Data Anchor Panel** (implemented in Phase 10) is the top-level epistemic gauge. It must strictly adhere to this spec:

### 4.1 Visual Hierarchy
It resides **ABOVE** all other content. No regime or strategy data is valid if the Anchor is "Broken" or "Low Confidence."

### 4.2 Display Elements
1.  **Truth Epoch ID:** The immutable identifier of the current logical state.
2.  **Market Scope:** Clearly active market (US vs INDIA).
3.  **Data Provenance:**
    *   **Historical Coverage:** Years/Days available vs Required.
    *   **Recency:** T-minus days from today.
    *   **Source File:** Filename/Path validation.
4.  **Sufficiency Status:** FAIL-CLOSED status (SUFFICIENT / INSUFFICIENT) for Regime, Factor, Liquidity layers.
5.  **Mock Status:** Must be explicitly "NONE" or "PURGED."
6.  **Confidence Level:**
    *   **HIGH:** Full Integrity + Sufficient History + Recent Data.
    *   **MEDIUM:** Full Integrity + Sufficient History + Stale Data (>7 days).
    *   **LOW:** Insufficient History OR Missing Data.

## 5. Regime Semantics

The dashboard must distinguish between two definitions of "regime":

1.  **Detected Regime (The Signal):**
    *   *Definition:* What the math says about the price action (e.g., "Strong Bullish", "Volatile Neutral").
    *   *Source:* `regime_context.eveluation_window`.
    *   *Display:* "Market Condition."

2.  **Actionable Regime Gate (The Permission):**
    *   *Definition:* Whether the system allows entries based on the signal AND governance rules (e.g., "Restricted", "Open", "Observer Only").
    *   *Source:* `system_status.expansion_transition` + Governance Overrides.
    *   *Display:* "Execution Gate."

**Requirement:** Never display "Bullish" as "Go". Display it as "Condition: Bullish" / "Status: Locked."

## 6. Macro Context Scope Rules

1.  **Global Macro:** Elements that affect ALL markets (e.g., US Dollar Index DXY, Oil, Geopolitics). displayed in a shared context or explicitly marked `[GLOBAL]`.
2.  **Local Macro:** Elements specific to the selected market (e.g., VIX for US, India VIX for India).
3.  **Scope Labeling:** Every Macro tile must have a `scope` tag: `[US]`, `[IN]`, or `[GL]`.

## 7. Strategy & Capital Narratives

### 7.1 Terminal Strategy States
Strategies must always resolve to one of:
*   `ELIGIBLE`: Passes all filters.
*   `REJECTED`: Failed specific filter (reason required).
*   `HIBERNATING`: Voluntarily inactive (e.g., wrong season/regime).
*   `PENDING_DATA`: Insufficient data to decide.
*   *Legacy "Calculating" states are effectively software loading states, not business states.*

### 7.2 Market-Specific Capital
Capital Narrative must frame "Readiness" per market.
*   *Example:* "Capital is DEPLOYABLE in US (Regime Support) but RESTRICTED in INDIA (Low Confidence)."
*   Deployment gauges must reset when Market Scope changes.

## 8. Non-Goals

1.  **No Execution:** The dashboard does NOT trigger trades. It only shows *proposed* or *hypothetical* trades.
2.  **No Optimization:** The dashboard is not a backtesting lab. It does not allow parameter tuning.
3.  **No Prediction:** The dashboard does not show "Future Price". It shows "Current Probability Surface."

---
End of Specification
