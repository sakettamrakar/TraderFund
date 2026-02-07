# Dashboard Provenance Matrix

## 1. Purpose
This matrix ensures every displayed data point has a clear, auditable provenance chain.
Provenance must answer: **Where did this data come from? When was it computed? Is it still valid?**

---

## 2. Provenance Chain Definition
```
[Original Source] → [Ingestion Layer] → [Computation Layer] → [Artifact] → [Dashboard]
```

---

## 3. US Market Provenance

### 3.1. Price Data
| Proxy | Original Source | Ingestion | Artifact | Dashboard Component |
| :--- | :--- | :--- | :--- | :--- |
| SPY | Yahoo Finance | `market_loader.py` | `data/regime/raw/SPY.csv` | Market Snapshot |
| QQQ | Yahoo Finance | `market_loader.py` | `data/regime/raw/QQQ.csv` | Market Snapshot |
| ^TNX | Yahoo Finance | `market_loader.py` | `data/regime/raw/^TNX.csv` | Factor Context |
| VIX | Yahoo Finance | `market_loader.py` | `data/regime/raw/VIX.csv` | Fragility (Vol) |

### 3.2. Computed Layers
| Layer | Input Artifacts | Output Artifact | Dashboard Component |
| :--- | :--- | :--- | :--- |
| Regime | SPY, QQQ | `regime_context_US.json` | Policy Card |
| Factor | Regime + Proxies | `factor_context_US.json` | Intelligence Panel |
| Decision | Factor + Regime | `decision_policy_US.json` | Policy Card |
| Fragility | Decision + Factor | `fragility_context_US.json` | Fragility Card |

---

## 4. India Market Provenance

### 4.1. Price Data
| Proxy | Original Source | Ingestion | Artifact | Dashboard Component |
| :--- | :--- | :--- | :--- | :--- |
| NIFTY50 | Yahoo Finance (^NSEI) | `india_data_acquisition.py` | `data/india/NIFTY50.csv` | Market Snapshot |
| BANKNIFTY | Yahoo Finance (^NSEBANK) | `india_data_acquisition.py` | `data/india/BANKNIFTY.csv` | Factor Context |
| INDIAVIX | Yahoo Finance (^INDIAVIX) | `india_data_acquisition.py` | `data/india/INDIAVIX.csv` | Fragility (Vol) |
| IN10Y | FRED/IMF (INDIRLTLT01STM) | `india_in10y_fred_ingestion.py` | `data/india/IN10Y.csv` | Factor Context |

### 4.2. Computed Layers
| Layer | Input Artifacts | Output Artifact | Dashboard Component |
| :--- | :--- | :--- | :--- |
| Regime | NIFTY50 | `regime_context_INDIA.json` | Policy Card |
| Factor | All 4 Proxies | `factor_context_INDIA.json` | Intelligence Panel |
| Decision | Factor + Regime | `decision_policy_INDIA.json` | Policy Card |
| Fragility | Decision + Factor | `fragility_context_INDIA.json` | Fragility Card |
| Parity | All Proxies | `india_parity_status.json` | Data Anchor |

---

## 5. Provenance Display Requirements
1.  **Timestamp**: Each artifact contains `computed_at`. Display this on dashboard.
2.  **Source**: Each proxy has an original source. Display when hovering.
3.  **Version**: Each artifact has a `version`. Use for cache invalidation.

---

## 6. Provenance Violations
If any of the following occur, the dashboard MUST display a warning:
*   Artifact missing (`OFFLINE` state)
*   Artifact stale (> 24 hours for daily data)
*   Provenance marked `SYNTHETIC` (should never happen in REAL_ONLY mode)
