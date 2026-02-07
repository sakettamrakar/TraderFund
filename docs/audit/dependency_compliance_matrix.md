# Dependency Compliance Matrix

## 1. Matrix Overview
This matrix maps the defined **Proxy Dependency Contracts** (`docs/contracts/proxy_dependency_contracts.md`) against the actual Runtime Implementation.

---

## 2. Compliance Matrix

| Layer | Contract Requirement | Actual Input | Compliance | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Regime** | `Benchmark` + `Vol Gauge` | `SPY` + `VIX` (US)<br>`RELIANCE` + `CalcVol` (IN) | **PASS** | Core mechanics aligned. |
| **Factor** | `Momentum` (Bench+Growth) | `SPY` only | **PARTIAL** | QQQ missing from input. |
| **Factor** | `Liquidity` (Rates) | None | **FAIL** | Rates data not ingested. |
| **Factor** | `Breadth` (Sector) | None | **FAIL** | Sector proxies not ingested. |
| **Dashboard**| `Provenance` Visible | JSON Metadata | **PASS** | `inputs_used` field populated in Context JSONs. |

---

## 3. Epistemic Gaps
*   **Rates Blindness**: The system currently has zero visibility into Interest Rates, violating the `Liquidity` factor contract. The Factor Builder forces "UNKNOWN" or implicit neutral, but does not use the canonical `^TNX` proxy defined in `market_proxy_instance.json`.

---

## 4. Verdict
**Structurally Complaint**: The Code uses the `ProxyAdapter` and `MarketLoader` abstraction.
**Content Deficient**: The *breadth* of ingestion is narrower than the contract definition.
