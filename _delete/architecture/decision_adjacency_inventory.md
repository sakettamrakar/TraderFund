# Decision-Adjacency Inventory

**Authority**: `ARCH-1.5`
**Status**: DRAFT
**Date**: 2026-01-30

## 1. Inventory Table

| Artifact Name | File / Path | Original Intent | Observed Behavior | Ring (Current) | Decision-Adjacency Type | Risk Level | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Momentum Engine** | `src/core_modules/momentum_engine/` | Generate trade-ready signals. | Emits `MomentumSignal` objects with direction/confidence. | 3 | Flag / Signal | High | Core signal generator. |
| **Watchlist Builder** | `src/core_modules/watchlist_management/` | Filter universe to manageable list. | Selects/Excludes symbols based on criteria. | 3 | Filter / Select | Medium | Narrows the funnel. |
| **Technical Scanner** | `src/pro_modules/strategy_engines/technical_scanner.py` | Generate technical analysis signals. | Returns JSON with "bullish"/"bearish" verdicts. | 3 | Flag | Medium | "Pro" module, likely legacy/demo. |
| **Pipeline Controller** | `research_modules/pipeline_controller/` | Optimize compute by selective execution. | Decides which stages to run for which symbols. | 1 | Operational Decision | Low | Compute efficiency, not trading. |
| **Universe Hygiene** | `research_modules/universe_hygiene/` | Filter invalid symbols (data quality). | Removes symbols based on exchange/type. | 1 | Filter | Low | Data quality gate. |
| **Strategy Gate** | `traderfund/regime/gate.py` | Gate strategies based on regime. | Returns `GateDecision` (Allowed/Blocked). | 1 | Filter / Guardrail | Low | Safety mechanism. |
| **Decision Engine Core** | `src/decision/engine.py` | Formulate decisions from narratives. | Creates `Decision` objects. | 3 | Decision | High | The actual decision brain. |
| **Signal Discovery** | `signals/discovery/runner.py` | Detect new signals. | Creates `Signal` objects. | 2 | Flag | Medium | Part of Signal Layer. |
| **Confidence Scorer** | `signals/confidence_engine/scorer.py` | Score signal reliability. | Assigns confidence float. | 2 | Rank | Medium | Implies quality/actionability. |
| **Dispersion Watcher** | `src/evolution/watchers/dispersion_breakout_watcher.py` | Detect factor dispersion. | Emits "BREAKOUT" state. | 1 | Explain / Flag | Low | Describes market state. |
| **Narrative Accumulator** | `narratives/genesis/accumulator.py` | Promote weak signals to narratives. | Groups signals, creates "ACCUMULATED" events. | 3 | Rank / Flag | Medium | Upgrades signal importance. |
| **Historical Replay** | `historical_replay/momentum_intraday/` | Verify logic on past data. | Generates signals (offline). | 1 | Simulation | Zero | Offline tool. |
| **Legacy India Logic** | `src/data_ingestion/` | NSE Data Adapter. | Ingests data for India market. | 2 | Data | Low | Data source only. |

## 2. Analysis
Most "Decision" artifacts are correctly located in Ring 3 (Intelligence) or Ring 1 (Research/Gates). The `TechnicalScanner` in `src/pro_modules` appears to be a legacy or demo artifact. The `Pipeline Controller` uses "Decision" language but applies it to operational compute, which is acceptable.
