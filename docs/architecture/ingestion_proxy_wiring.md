# Ingestion Proxy Wiring Specification

## 1. Objective
To transition the TraderFund ingestion layer from a "Single-File Dependency" model to a "Multi-Proxy Aggregation" model. This ensures that downstream consumers (Factor Engine, Regime Gate) receive a holistic view of the market rather than a narrow keyhole view.

---

## 2. United States (US) Wiring Plan

### 2.1. Equity Benchmark Aggregation
*   **Current State**: `Regime = SPY.csv`
*   **Target State**: Computed Market Object.
*   **Inputs**:
    *   `SPY.csv` (Weight: 60%) - Large Cap Core
    *   `QQQ.csv` (Weight: 30%) - Tech/Growth Beta
    *   `IWM.csv` (Weight: 10%) - *Missing (Gap)* -> normalize weights to available (66%/33% for now).
*   **Wiring Action**:
    *   Create `US_Market_Composite` logical loader.
    *   Ingest `SPY` and `QQQ` concurrently.
    *   Align timestamps (Daily Close).
    *   Output: `market_composite_US_{date}.json` containing component returns and weighted aggregate.

### 2.2. Volatility & Stress Wiring
*   **Current State**: `VIX.csv` (often ignored or loosely coupled).
*   **Target State**: Canonical Volatility Input.
*   **Inputs**: `VIX.csv`.
*   **Wiring Action**:
    *   Bind `VIX.csv` directly to `VolatilityFactor`.
    *   **Gate**: If `VIX` is missing/stale > 3 days, flag `DATA_UNCERTAINTY`.

### 2.3. Bond/Rate Wiring
*   **Current State**: `^TNX.csv` (10Y Yield).
*   **Target State**: Curve Slope (Imputed).
*   **Wiring Action**:
    *   Ingest `^TNX.csv`.
    *   Wait for `US02Y` ingestion (Gap).
    *   *Interim*: Use `^TNX` absolute level as "Cost of Capital" proxy.

---

## 3. India (IN) Wiring Plan

### 3.1. Equity Benchmark (Surrogate Mode)
*   **Current State**: `NSE_RELIANCE_1d.jsonl`.
*   **Target State**: Explicit Surrogate wrapper.
*   **Wiring Action**:
    *   Wrap `NSE_RELIANCE` in a `ProxyAdapter`.
    *   expose as `market_composite_INDIA` but tag metadata with `composition: "SINGLE_STOCK_SURROGATE"`.
    *   **Strict Warning**: Do not attempt to average Reliance with HDFCBANK until proper Index data is available. Correlation risk is too high.

### 3.2. Volatility (Synthesized)
*   **Current State**: None.
*   **Target State**: Realized Return Volatility (Parkinson/Garman-Klass if possible, else StdDev).
*   **Wiring Action**:
    *   Calculate `rolling_std_dev(RELIANCE, window=20)` on the fly.
    *   Expose as `volatility_proxy_INDIA`.
    *   Note: This is "Stock Volatility", not "Market Volatility".

---

## 4. Implementation Constraints
1.  **Fail-Closed**: If a primary proxy (SPY for US, Reliance for IN) is missing, the entire market ingestion must fail. Secondary proxies (QQQ) are optional but desired.
2.  **Date Alignment**: All proxies must align to the *primary* proxy's date index.
3.  **Gap Handling**: Gaps defined in `coverage_gap_register.md` must result in `null` fields in the output object, NOT interpolated values.
