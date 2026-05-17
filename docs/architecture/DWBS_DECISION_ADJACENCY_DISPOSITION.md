# Decision-Adjacency Assessment

> Consolidated from `decision_adjacency_inventory.md` (DRAFT) and `decision_adjacency_disposition.md` (APPROVED).
> Originals moved to `_delete/architecture/`.

**Authority**: `ARCH-1.5` | **Status**: APPROVED | **Date**: 2026-01-30

---

## 1. Inventory

| Artifact Name | File / Path | Ring | Adjacency Type | Risk | Disposition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Momentum Engine** | `src/core_modules/momentum_engine/` | 3 | Flag / Signal | High | MIGRATE |
| **Watchlist Builder** | `src/core_modules/watchlist_management/` | 3 | Filter / Select | Medium | MIGRATE |
| **Technical Scanner** | `src/pro_modules/strategy_engines/technical_scanner.py` | 3 | Flag | Medium | MIGRATE |
| **Pipeline Controller** | `research_modules/pipeline_controller/` | 1 | Operational Decision | Low | KEEP |
| **Universe Hygiene** | `research_modules/universe_hygiene/` | 1 | Filter | Low | KEEP |
| **Strategy Gate** | `traderfund/regime/gate.py` | 1 | Filter / Guardrail | Low | KEEP |
| **Decision Engine Core** | `src/decision/engine.py` | 3 | Decision | High | MIGRATE |
| **Signal Discovery** | `signals/discovery/runner.py` | 2 | Flag | Medium | MIGRATE |
| **Confidence Scorer** | `signals/confidence_engine/scorer.py` | 2 | Rank | Medium | MIGRATE |
| **Dispersion Watcher** | `src/evolution/watchers/dispersion_breakout_watcher.py` | 1 | Explain / Flag | Low | KEEP |
| **Narrative Accumulator** | `narratives/genesis/accumulator.py` | 3 | Rank / Flag | Medium | MIGRATE |
| **Historical Replay** | `historical_replay/momentum_intraday/` | 1 | Simulation | Zero | KEEP |
| **Legacy India Logic** | `src/data_ingestion/` | 2 | Data | Low | FREEZE |

---

## 2. Disposition Summary

| Disposition | Count | Description |
| :--- | :--- | :--- |
| KEEP | 5 | Valid Ring-1 Research or Operational Logic |
| MIGRATE | 7 | Symbol-level intelligence to be moved to Ring-3 |
| FREEZE | 1 | Legacy/Dormant logic to be preserved but disabled |
| DELETE | 0 | No safe-to-delete artifacts found |

---

## 3. Rationale

### KEEP (Ring-1 Research / Ops)
- **Pipeline Controller**: Operational efficiency logic (compute resource allocation)
- **Universe Hygiene**: Data quality filtration (exclusion mechanism, not selection)
- **Strategy Gate**: Safety/risk gating (exclusion, not inclusion)
- **Dispersion Watcher**: Market state description (purely explanatory)
- **Historical Replay**: Research verification tool (offline)

### MIGRATE (Future Ring-3 Intelligence)
- **Momentum Engine**: Generates trade signals — Intelligence, not Research
- **Watchlist Builder**: Selects symbols for attention — Intelligence
- **Technical Scanner**: Scans for technical setups — likely legacy/demo
- **Decision Engine Core**: The central decision processor
- **Signal Discovery**: Generates alpha signals
- **Confidence Scorer**: Ranks signals by quality
- **Narrative Accumulator**: Promotes signals to narratives

### FREEZE (Legacy / Dormant)
- **Legacy India Logic**: Embedded selection logic in old scripts; frozen in favor of new Momentum Engine

---

## 4. Risk Avoidance

By labeling Momentum Engine and others as Intelligence (MIGRATE), we avoid "Truth Decay" where research modules subtly recommend trades. Ring-1 remains "Source of Truth" (What is the regime?), Ring-3 becomes "Source of Action" (What should we trade?).
