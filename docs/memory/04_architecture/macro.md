# System Architecture (Macro)

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> **Conflict Handling**: Where legacy source docs conflict with Domain Model, mark OPEN_CONFLICT.

---

## System Identity

TraderFund is a **regime-aware market intelligence platform** operating in **Observer Mode**.
It generates research artifacts, not orders. Final authority always remains with the human.

---

## High-Level Component Map

*(Original Diagram: `docs/memory/_appendix/macro_code.md`)*

1. **Ingestion Layer (L0)**: US Pipeline (REST) + India Pipeline (WS)
2. **Cognitive Core (L1-L5)**: Regime · Narrative · Meta · Factor · Strategy
3. **Opportunity Discovery (L6)**: Parallel Lenses (Narrative, Factor, Fundamental, Technical, Strategy)
4. **Convergence Engine (L7)**: Candidate Assessment · Unified Score
5. **Execution Constraints (L8)**: Bounds · Risk Budget
6. **Portfolio Intelligence (L9)**: Diagnostics · Flags · Regime Conflict
7. **Dashboard (UI)**: Glass-Box Observation (Regime, Narrative, Signals)
8. **Human Operator**: Final Authority

---

## Component Definitions

### 1. Ingestion Layer (L0 — Foundation)

| Sub-Component | Market | Mode | Data |
| :--- | :--- | :--- | :--- |
| `US_Pipeline` | US | REST Batch (AlphaVantage) | OHLCV Daily + Intraday |
| `India_Pipeline` | India | WebSocket (SmartAPI) + REST Historic | Tick → 1m Candles |
| `Canonical_Store` | Both | Parquet (symbol/date partitioned) | Time-aligned, UTC |

**Invariants**:
- Pipelines are physically separate with no shared state.
- Raw data is never mutated (corrections are new versions).
- All logic proceeds on `event_time`, not processing time.

### 2. Cognitive Core (L1-L5)

| Engine | Level | Question | Output |
| :--- | :--- | :--- | :--- |
| `Regime_Engine` | L1 | "What game are we playing?" | Risk-On / Risk-Off / Transition / Stress |
| `Narrative_Engine` | L2 | "Why is this happening?" | Structured Narratives (Born → Reinforced → Resolved) |
| `Meta_Engine` | L3 | "Can we trust this signal?" | Validity Scores, Confidence Modifiers |
| `Factor_Engine` | L4 | "What is being rewarded?" | Factor Strength, Direction, Stability |
| `Strategy_Selector` | L5 | "Which playbook fits?" | Active Strategy Set (Regime + Factor gated) |

**Regime Engine Dimensions** *(Source: Regime_Engine_Overview.md)*:
- Trend (directional persistence)
- Volatility (amplitude of variance)
- Liquidity (execution efficiency)
- Event Pressure (external catalysts)

**Layer Interaction Rules** *(Source: layer_interaction_contract.md)*:
- Data flows strictly downward through the hierarchy.
- No layer may skip its upstream constraints.
- No downstream layer may mutate upstream state.
- Signals MUST carry regime context; proposals MUST carry factor permissions.

### 3. Opportunity Discovery (L6 — Parallel Lenses)

| Lens | Input | Scans For |
| :--- | :--- | :--- |
| `Narrative_Lens` | Narratives, Macro Events, Geopolitics | Theme-driven dislocations |
| `Factor_Lens` | Factor Scores | Statistically rewarded patterns |
| `Fundamental_Lens` | Balance Sheet, Valuation | Valuation / solvency anomalies |
| `Technical_Lens` | Price, Volume, Indicators | Breakouts, accumulation, support |
| `Strategy_Lens` | Active Playbooks | Playbook-specific screen criteria |

**Output**: `OpportunityCandidate` objects with source tags.

### 4. Convergence Engine (L7)

- Merges candidates from all lenses into a unified pool.
- Applies regime-dependent weighting to lens scores.
- Produces `HighConvictionIdeas` (≥3 lenses) and `Watchlist` (1-2 lenses).

### 5. Constraints & Portfolio Intelligence (L8-L9)

- **L8 (Constraints)**: Hard risk limits — position sizing, exposure caps, drawdown thresholds.
- **L9 (Portfolio Intelligence)**: Diagnostic + Advisory — regime conflict, narrative decay, factor mismatch, horizon drift, concentration risk.
- **Output**: Flagged watchlist items with Red/Orange/Yellow/Green severity.

### 6. Dashboard (UI — Observation Layer)

- Glass-Box Observer: every output traces to a specific cognitive layer.
- Displays: Regime State, Active Narratives, Opportunity Candidates, Portfolio Flags.
- No execution capability. Diagnostics Over Commands.

---

## Architectural Invariants

*(Source: architectural_invariants.md)*

1.  **Event Time Integrity**: All logic proceeds on `event_time`. Replays yield identical state.
2.  **No Lookahead**: Core abstractions physically prevent access to future data.
3.  **Immutability of Raw Data**: Raw data is never mutated. Corrections are new versions.
4.  **Market Separation**: India vs US pipelines are physically distinct.
5.  **Signal-Execution Separation**: Engines emit signals; they do not know about capital.
6.  **Idempotency**: Re-running on same input produces identical output.
7.  **Glass-Box Observability**: Every threshold is configurable and observable.
8.  **Cognitive Ordering**: Regime → Narrative → Meta → Factor → Strategy → Discovery → Convergence. Strictly enforced.
9.  **Layer Bypass Prohibition**: No layer may skip upstream constraints.

### Global Governance Rules

10. **Layer Authority Rule**: `domain_model.md` numbering and definitions are canonical. Layer numbering in legacy documents is non-authoritative and must not be referenced for reasoning.
11. **No Silent Degradation Rule**: Missing inputs must surface explicit `INSUFFICIENT_DATA` states. No component may silently proceed with partial data without flagging degradation.
12. **No Layer Inflation Rule**: No new cognitive layer may be introduced without displacing an existing one. The 13-Level hierarchy is a closed set.

---

## Legacy Architecture Mapping

| Legacy Concept | Legacy Location | Current 13-Level Mapping | Status |
| :--- | :--- | :--- | :--- |
| Three-Ring Model (Truth/Adapter/Intel) | `system_landscape.md` | Replaced by L0-L9 hierarchy | **SUPERSEDED** |
| 14-Layer Stack (L1-L14) | `structure_stack_vision.md` | Compressed to 13-Level (L0-L12) | **SUPERSEDED** |
| Reality/Time/Object/Feature Layers | Structure Stack L1-L4 | Folded into Ingestion (L0) | **MAPPED** |
| Event Layer (L5 old) | Structure Stack L5 | Folded into Narrative (L2) | **MAPPED** |
| Regime Layer (L6 old) | Structure Stack L6 | Regime (L1) — promoted | **MAPPED** |
| Narrative Layer (L7 old) | Structure Stack L7 | Narrative (L2) — promoted | **MAPPED** |
| Signal Layer (L8 old) | Structure Stack L8 | Folded into Discovery Lenses (L6) | **MAPPED** |
| Belief Layer (L9 old) | Structure Stack L9 | Split: Meta-Analysis (L3) + Convergence (L7) | **MAPPED** |
| Strategy Layer (L10 old) | Structure Stack L10 | Strategy Selection (L5) | **MAPPED** |
| Optimization Layer (L11 old) | Structure Stack L11 | Replaced by Constraints (L8) + Portfolio Intel (L9) | **REPLACED** |
| Execution Layer (L12 old) | Structure Stack L12 | **DEFERRED** — Future (L12) | **OUT OF SCOPE** |
| Settlement/Audit (L13-L14 old) | Structure Stack L13-L14 | **DEFERRED** — Future | **OUT OF SCOPE** |
| Latent Layers (Macro, Flow, Vol Geometry) | `latent_structural_layers.md` | Sub-dimensions of Regime (L1) + Technical Lens (L6). See Resolved Items. | **LATENT_MAPPED** |

---

## Resolved Conflicts

| ID | Description | Resolution | Date |
| :--- | :--- | :--- | :--- |
| **RC-1** (was OC-1) | Legacy `layer_interaction_contract.md` uses L6=Regime, L7=Narrative. | **Domain Model prevails.** Legacy contract is SUPERSEDED. Legacy numbering is non-authoritative (Rule 10). | 2026-02-10 |
| **RC-2** (was OC-2) | Legacy `strategy_layer_policy.md` references "Belief Layer (L9)". | **Domain Model prevails.** Belief → Meta-Analysis (L3). Strategy Selector (L5) consumes Meta-Analysis (L3). | 2026-02-10 |
| **RC-3** (was OC-3) | Regime→Narrative adapter not wired in code. | **Implementation gap, not design flaw.** Architecture is correct (L1→L2 mandatory). Code marked `NOT_WIRED` in `narrative_engine.yaml`. Invariant added: Narrative must never execute without regime context. | 2026-02-10 |
| **RC-4** (was OC-4) | No fundamental data ingestion for Fundamental Lens (L6). | **AlphaVantage FUNDAMENTAL_DATA endpoint** identified (Income Statement, Balance Sheet, Cash Flow). Implementation deferred. Lens returns `INSUFFICIENT_DATA` until wired. | 2026-02-10 |
| **RC-5** (was OC-5) | Indicator Engine described as separate layer. | **CLOSED.** Indicator computation is an internal detail of Technical Lens (L6), not a separate cognitive level. | 2026-02-10 |
| **RC-6** (was OC-6) | Cross-Market Alpha Discovery (Granger causality, lead-lag) unmapped. | **Mapped to Factor Lens (L6).** Cross-market correlation patterns are statistical reward structures, not narratives. | 2026-02-10 |

## Resolved Questions

| ID | Question | Resolution | Date |
| :--- | :--- | :--- | :--- |
| **RQ-1** (was OQ-1) | Latent Layers mapping (Macro, Flow, Vol Geometry). | Sub-dimensions of existing levels (NOT new levels): Macro/Liquidity → Regime (L1), Flow/Microstructure → Technical Lens (L6), Vol Geometry → Regime (L1). Status: `LATENT_MAPPED`, implementation deferred. | 2026-02-10 |
| **RQ-2** (was OQ-2) | Fundamental data source for Fundamental Lens. | **AlphaVantage FUNDAMENTAL_DATA endpoint.** Merged with RC-4. | 2026-02-10 |
| **RQ-3** (was OQ-3) | Convergence weighting algorithm. | **Baseline prior defined** (equal-weight 20% per lens, regime-dependent multipliers). This is a baseline prior, not a learned truth. Requires calibration via research. See `convergence_engine.yaml`. | 2026-02-10 |
| **RQ-4** (was OQ-4) | Cross-Market Alpha Discovery mapping. | Merged with RC-6. → Factor Lens (L6). | 2026-02-10 |
