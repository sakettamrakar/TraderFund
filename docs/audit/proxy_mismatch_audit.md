# Proxy Mismatch Audit (Dry Run)

## 1. Audit Target
**Goal**: Verify alignment between the *Declared* Proxy Sets (in docs) and the *Implemented* logic (in code/UI).

---

## 2. Methodology
*   **Docs Source**: `market_proxy_sets.md`, `data_source_governance.md`
*   **Code Source**: `regime.py`, `market_snapshot.py`, `App.jsx`, `SystemStatus.jsx`

---

## 3. Findings

### US Market
| Component | Claimed Input | Actual Input | Verdict |
| :--- | :--- | :--- | :--- |
| `market_proxy_sets.md` | SPY + QQQ + IWM + VIX | - | **Reference** |
| `regime.py` (Current) | SPY Only | SPY.csv | **MISMATCH** (Missing QQQ/VIX) |
| `Dashboard / Context` | "S&P 500" | SPY | **ALIGNED** (but incomplete) |
| `Factor Engine` | Multi-Factor | Single-File | **MISMATCH** |

### INDIA Market
| Component | Claimed Input | Actual Input | Verdict |
| :--- | :--- | :--- | :--- |
| `market_proxy_sets.md` | NIFTY 50 (Surrogate: Reliance) | - | **Reference** |
| `regime.py` (Current) | RELIANCE | RELIANCE.jsonl | **ALIGNED** (Degraded) |
| `Dashboard / Context` | "Nifty 50" | RELIANCE | **MISMATCH** (UI lies about source) |
| `Factor Engine` | N/A | RELIANCE | **ALIGNED** |

---

## 4. Corrective Actions Required (Phase 11 Implementation)
1.  **US**: Update `regime.py` to ingest `VIX` and `QQQ`. Use `Composite` logic defined in `ingestion_proxy_wiring.md`.
2.  **INDIA**: Update Dashboard UI to explicitly label "Proxy: Reliance" instead of "Nifty 50".
3.  **Global**: Implement `ProxyAdapter` class in `src/structural/` to enforce the `ProxySet` schema.
