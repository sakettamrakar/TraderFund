# DWBS: Intelligence Layer Architecture

**Type**: Structural / Design-Only
**Plane**: Intelligence / Decision Support
**Execution Rights**: NONE
**Depends On**:
- `DWBS_SYSTEM_LANDSCAPE.md`
- `DWBS_DECISION_ADJACENCY_AUDIT.md`

---

## 1. Intelligence Layer Canonical Definition

**The Intelligence Layer** is a read-only, heuristic, human-facing layer that suggests where to look, while explicitly deferring judgment and action to humans.

### Clarifications
- **Research** = Truth (Descriptive)
- **Intelligence** = Attention (Suggestive)
- **Execution** = Forbidden

This definition is **binding**.

---

## 2. Intelligence Input Contracts

The Intelligence Layer accepts explicit, read-only inputs. It can observe but never reinterpret research outputs.

### 2.1 From Research (Ring-1)
- **Macro Context**: The global market state.
- **Regime State**: The current market regime (e.g., Bull, Bear, Sideways).
- **Factor Context**: Factor performance and exposure.
- **Strategy Eligibility**: Explicit YES/NO/WHY for symbols.
- **Watcher States**: Monitoring status of specific entities.
- **Evolution Diagnostics**: Health and performance metrics of the system.

### 2.2 From Market Data
- **Symbol OHLCV**: Price history (Open, High, Low, Close, Volume).
- **Volatility**: Metrics indicating price fluctuation.
- **Volume**: Trading activity levels.
- **Corporate Actions**: Dividends, splits, etc. (if present).
- **News Metadata**: Headlines only (optional).

---

## 3. Intelligence Output Types

### 3.1 Attention Signals
Signals indicating "something interesting" without prediction or recommendation.
- "Unusual volatility"
- "Volume expansion"
- "Gap behavior"
- "Breakout-like movement"

### 3.2 Watchlists
Groupings of symbols based on specific criteria. Must include the *why*, *block status*, and *research state*.
- **Thematic**: e.g., "High Volatility Movers"
- **Structural**: e.g., "Blocked by Research"
- **Narrative-driven**: (Optional)

### 3.3 Readiness Views
Views that show potential opportunities pending state changes.
- "These symbols would qualify if factor X flips"
- "Momentum candidates currently blocked by regime"

### 3.4 Comparative Views
Purely observational comparisons.
- US vs India
- Sector vs Market
- Today vs Last Regime

---

## 4. Symbol Universe & Narrowing

### Symbol Universe Contract
```
SymbolUniverse {
  market
  universe_definition
  inclusion_rules
  exclusion_rules
  refresh_frequency
}
```

### Rules
1.  Narrowing is heuristic.
2.  Must be explainable.
3.  Must reference research blocks explicitly.
4.  Must never auto-promote symbols.

---

## 5. Market-Specific Intelligence Adapters

Adapters share the same Intelligence schema but differ in data sources. They must **never** embed research logic.

### 5.1 US Intelligence Adapter
- **Consumes**: US symbols, US data feeds, US research instantiation.

### 5.2 India Intelligence Adapter
- **Consumes**: India symbols, India WebSocket/daily data, (Future) India research instantiation.

---

## 6. Dashboard Conceptual Views

### A. System Truth (from Research)
"Why nothing is happening"
- Macro + Regime + Factor summary.

### B. Intelligence Panel
"What is interesting today"
- Explicit labels:
    - **ATTENTION**
    - **BLOCKED BY RESEARCH**
    - **OBSERVATION ONLY**

### C. Symbol Deep-Dive (Optional)
For any symbol:
- Price / volume context.
- Intelligence flags.
- Research state overlay.
- Explicit "No Action" disclaimer.

---

## 7. Governance & Safety Rules

1.  **Intelligence cannot write to research.**
2.  **Intelligence cannot mutate eligibility.**
3.  **Intelligence cannot infer execution.**
4.  **All outputs must carry:**
    - Reason
    - Source
    - Limitation disclaimer

### Obligations
- **OBL-INTELLIGENCE-NON-EXECUTING**: Intelligence components must never execute trades.
- **OBL-INTELLIGENCE-RESEARCH-RESPECT**: Intelligence must verify research state before suggesting attention.

---

**GUIDING PRINCIPLE**
> Intelligence may attract attention,
> but it must never attract capital.
