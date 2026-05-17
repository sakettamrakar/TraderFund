# Coverage Gap Register

## 1. Overview
This register tracks legitimate gaps in data coverage where a defined Proxy exists in `market_proxy_sets.md` but no corresponding data file exists in `data_source_governance.md`.

**Gap Policy:**
*   Gaps are "Known Knowns".
*   System components must Handle Gaps Gracefully (HGG).
*   Mocking data to fill gaps is **STRICTLY PROHIBITED**.

---

## 2. United States (US) Gaps

| Symbol | Priority | Impact | Remediation Plan |
| :--- | :--- | :--- | :--- |
| **IWM** | P2 | Cannot validate "Breadth" / Domestic Economy strength. | Ingest via AlphaVantage/Yahoo in Phase 12. |
| **DIA** | P3 | Blind spot for industrial/cyclical rotation. | Ingest in Phase 12. |
| **US02Y**| P2 | Lower fidelity on Fed Rate expectations. | Ingest 2Y Yield series. |
| **DXY** | P2 | No direct signal for FX Headwinds. | Ingest DXY or UUP ETF. |
| **USOIL**| P2 | No inflation/energy input. | Ingest WTI/USO. |

---

## 3. India (IN) Gaps (CRITICAL)

| Symbol | Priority | Impact | Remediation Plan |
| :--- | :--- | :--- | :--- |
| **NIFTY** | **P0** | **CRITICAL**. Using Reliance as proxy is mathematically unsound for Beta/Correlation. | Connect to NSE Index Data feed immediately. |
| **BANKNIFTY**| **P1** | Blind to Banking Sector (35% of market). | Ingest Bank Nifty Index. |
| **INDIAVIX** | **P1** | No authentic "Fear" metric for India. | Ingest India VIX. |
| **USDINR** | P2 | Currency risk unmodelled. | Ingest USDINR pair. |
| **SMLCAP** | P2 | Retail sentiment invisible. | Ingest Nifty Smallcap 100. |

---

## 4. Derived Impact
*   **Regime Confidence**:
    *   **US**: HIGH (SPY/QQQ/VIX/10Y cover 80% of signal variance).
    *   **INDIA**: LOW (Reliance != Nifty). Regime signals for India should be treated as "Stock Specific" until Index data is live.
