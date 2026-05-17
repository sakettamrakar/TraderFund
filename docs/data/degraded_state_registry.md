# Degraded State Registry

## 1. Concept
A **Degraded State** occurs when a Market Proxy Set exists but fails to meet the `CANONICAL` completeness standard.
Rather than blocking execution entirely, the system may operate in a **DEGRADED** mode, provided:
1.  The degradation is explicitly declared.
2.  The limitations are documented.
3.  The "Truth" reported is scoped to the inputs available.

---

## 2. Registry of Active Degraded States

### [DEG-IN-001] India Single-Stock Surrogate
*   **Market**: INDIA
*   **Status**: **DEGRADED**
*   **Missing Core**: Broad Market Index (Nifty 50), Sector Indices (BankNifty).
*   **Substitution**: `NSE_RELIANCE` (Single Stock) represents the "Market".
*   **Epistemic Risk**: Idiosyncratic risk of Reliance Industries is conflated with Systemic Market Risk.
*   **Impact**:
    *   **Regime**: Valid only if Reliance correlates > 0.8 with Nifty (historically true, but not guaranteed).
    *   **Sector Rotation**: Impossible to detect.
    *   **Breadth**: Impossible to detect.
*   **Authorized For**: Phase 10 (Restoration) & 11 (Intelligence).
*   **Prohibited For**: Live Trading (Phase 13+).

### [DEG-US-001] US Gap-Fill Composition
*   **Market**: US
*   **Status**: **CANONICAL (with warnings)**
*   **Missing Secondary**: `IWM` (Small Cap), `DIA` (Industrials).
*   **Substitution**: None. `Benchmark Equity` is composed solely of Large Cap (`SPY`) and Tech (`QQQ`).
*   **Epistemic Risk**: Blindness to "Rotation into Small Caps" (Breadth divergences).
*   **Impact**:
    *   **Breadth**: Under-reported.
    *   **Regime**: Biased towards Large-Cap/Tech.
*   **Authorized For**: All Phases (Acceptable approximation for Core Strategy).

---

## 3. Handling Logic
*   **If Status == DEGRADED**:
    *   UI Header must show "⚠️ PROXY LIMITED" badge.
    *   Regime Confidence is capped at `MEDIUM` (0.5).
    *   Strategy constraints must be tighter (higher margin of safety).
