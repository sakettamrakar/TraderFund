# India Market Proxies

**Type**: Research Contract
**Scope**: India Research Instantiation

This document defines the exact counterparts to US proxies used in the Core Research Engine.

---

## Mandatory Mappings

| Research Concept | US Proxy | India Proxy | Rationale | Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **Broad Market** | QQQ / SPY | **NIFTY50 / NIFTY100** | The standard liquid benchmark for Indian equities. | Heavy weighting on financials/IT compared to QQQ. |
| **Volatility** | VIX | **INDIA VIX** | Direct equivalent, measures implied volatility of NIFTY options. | History is shorter than US VIX. |
| **Liquidity** | HYG / LQD | **AAA/AA Bond Yield Spread** | Measures credit stress. (Proxy: 10Y G-Sec vs AAA Corp Bond). | Corporate bond market is less liquid; data may be sparse. |
| **Rates** | US 10Y | **India 10Y G-Sec** | Benchmark risk-free rate. | Managed/intervened more actively than US 10Y. |
| **Breadth** | NYSE Adv/Dec | **NSE Adv/Dec** | Standard breadth metric. | - |
| **Dispersion** | Sector Returns | **NSE Sectoral Dispersion** | Standard deviation of NIFTY Sector indices. | Fewer sectors, concentration risks. |

---

## Data Sources & Implementation Details

### 1. Broad Market (NIFTY50)
- **Source**: Daily Fetch / WebSocket.
- **Symbol**: `^NSEI` (Yahoo/Generic) or `NIFTY 50` (NSE).

### 2. Volatility (INDIA VIX)
- **Source**: Daily Fetch.
- **Symbol**: `^INDIAVIX`.

### 3. Rates (India 10Y)
- **Source**: Daily Fetch.
- **Symbol**: `^IGSC` (or similar proxy).
- **Fallback**: Fixed rate (e.g., 7.0%) if live feed fails, with "Estimated" flag.

### 4. Liquidity (Credit Spreads)
- **Implementation**: Due to data access constraints on live corporate bond spreads, we may use **Banking Liquidity Proxy**: `Bank Nifty / Nifty 50` ratio trend or `USD/INR` implied volatility as a secondary stress indicator.
- **Structural Decision**: For the initial instantiation, if direct spread data is unavailable, Liquidity will default to **NEUTRAL** (read-only safe mode).

### 5. Dispersion
- **Implementation**: Calculated from available major sector indices (Bank, IT, Auto, Pharma).

---

## Guiding Principle
> "Proxies need not be perfect, but they must be consistent in what they measure."
