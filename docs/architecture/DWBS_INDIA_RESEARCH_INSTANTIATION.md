# DWBS: India Research Instantiation

**Type**: Market Adapter / Research
**Plane**: Research (Ring-2)
**Execution Rights**: NONE
**Depends On**:
- `DWBS_SYSTEM_LANDSCAPE.md`
- `DWBS_INTELLIGENCE_LAYER.md`

---

## 1. Context & Purpose

This document defines the instantiation of the **India Research Adapter**, a market-specific implementation of the Core Research Engine.

The purpose is to answer the question:
> “If Intelligence asks the same question of India as of the US, the system can answer with the same vocabulary and semantics.”

### Hard Constraints (Strict)
- ❌ **NO New Strategy Logic**: Must reuse US strategy definitions.
- ❌ **NO Independent Tuning**: Thresholds must remain structurally consistent (proxies may differ, logic does not).
- ❌ **NO Execution**: This adapter is strictly read-only and explanatory.
- ❌ **NO Semantic Divergence**: "High Volatility" must mean the same thing in India as in the US (structurally).

---

## 2. Structural Components

The India Research Instantiation consists of four core artifacts that mirror the US Research Engine.

### 2.1 India Macro Context (`IndiaMacroContextBuilder`)
- **Role**: Explains the "weather" (Rates, Liquidity, Growth, Risk).
- **Proxies**: Uses India-specific equivalents (e.g., India 10Y G-Sec, NIFTY50).
- **Update**: Daily (via EV-TICK).
- **Output**: `docs/research/india/context/macro_context.json`

### 2.2 India Regime Engine (`IndiaRegimeEngine`)
- **Role**: Determines the market state (Bull, Bear, Sideways, Volatile).
- **Taxonomy**: Identical to US (e.g., `BULL_VOL`, `NEUTRAL`, `BEAR_QUIET`).
- **Inputs**: India Price/Vol series.
- **Output**: `docs/research/india/context/regime_context.json`

### 2.3 India Factor Context (`IndiaFactorContextBuilder`)
- **Role**: Measures factor premiums and conditions (Momentum, Value, Quality, Volatility).
- **Vocabulary**: Identical to US (e.g., Momentum `EMERGING`, `CONFIRMED`).
- **Output**: `docs/research/india/context/factor_context.json`

### 2.4 India Strategy Eligibility (`IndiaStrategyEligibility`)
- **Role**: Applies the **universal** strategy contracts to the **India** context.
- **Logic**: Reuses `src/strategy/registry.py`.
- **Output**: `docs/research/india/strategy_eligibility.json`

---

## 3. Integration & Orchestration

### 3.1 EV-TICK Integration
India Research runs as a **non-blocking** phase within the `EV-TICK` cycle.
- **Fail-Safe**: If India data ingestion fails, US research proceeds unaffected.
- **Artifacts**: India outputs are persisted alongside US artifacts but in dedicated `docs/research/india/` paths.

### 3.2 Dashboard Integration
The dashboard provides a **Market Selector** (US | India).
- **View Parity**: India view displays the same widgets (Macro, Regime, Factors) as the US view.
- **Data Source**: Fetches from `docs/research/india/context/` when India is selected.

---

## 4. Governance

### Obligations
- **OBL-MARKET-PARITY**: Research structures must be identical across markets.
- **OBL-NO-MARKET-SPECIFIC-LOGIC**: Logic (e.g., "Buy if momentum > X") resides in Core, not Adapters. Adapters only provide the inputs.

### Validation
The instantiation is valid if and only if:
1.  All 4 contexts (Macro, Regime, Factor, Eligibility) are produced.
2.  The schema of these contexts is identical to US.
3.  No execution code is reachable.
