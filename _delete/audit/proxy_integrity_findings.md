# Proxy Integrity Audit Findings

## 1. Audit Scope
**Date**: 2026-01-30
**Target**: `src/ingestion/market_loader.py` vs `docs/contracts/market_proxy_sets.json` via `src/structural/market_proxy_instance.json`.

---

## 2. Findings

### [P-INT-001] US Benchmark Composition Logic
*   **Contract**: `US Composite` = Weighted Aggregation of `SPY` (60%) + `QQQ` (30%).
*   **Implementation**: `MarketLoader.load_benchmark("US")` explicitly loads **SPY Only**.
*   **Evidence**:
    ```python
    # Just load SPY for now as the core anchor, QQQ later
    primary_path = paths[0]
    ```
*   **Severity**: **MEDIUM**.
*   **Impact**: Tech sector influence is underweight compared to spec. Epistemic alignment is partial (Primary Proxy is valid, but Composite is missing).
*   **Recommendation**: Implement Multi-Ticker loading and Weighted Average logic in Phase 10.1.

### [P-INT-002] Rates Anchor Missing
*   **Contract**: `Rates Anchor` = `^TNX` (10Y Yield).
*   **Implementation**: `MarketLoader` has no method to load Rates/Yields. `RegimeContextBuilder` and `FactorContextBuilder` do not request Rates data.
*   **Evidence**: No `load_rates` method in `MarketLoader`.
*   **Severity**: **HIGH**.
*   **Impact**: "Macro" and "Liquidity" factors cannot be calculated authentically.
*   **Recommendation**: Add `load_rates(market)` to `MarketLoader` immediately.

### [P-INT-003] India Surrogate Binding
*   **Contract**: `INDIA` = `NSE_RELIANCE` (Degraded Surrogate).
*   **Implementation**: Correctly implemented.
*   **Status**: **COMPLIANT**.

---

## 3. Conclusion
Ingestion wiring is functional but **incomplete** relative to the full Multi-Factor Proxy specification. It operates in a "Core-Only" mode (Benchmark + Volatility), missing Rates and Secondary Indices.
