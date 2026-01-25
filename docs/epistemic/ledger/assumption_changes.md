# Assumption Changes Log

**Status**: Critical Memory. Append-Only.

### Epistemic Authority

The global hierarchy of truth is strictly defined as:

1.  **Decision Ledger** (Authoritative)
2.  **Architectural Invariants**
3.  **Active Constraints**
4.  **Current Phase Rules**
5.  **Assumption Changes**
6.  **Evolution Log** (Informational)

Lower layers cannot override higher layers. Conflicts must be resolved upward, never downward.

---

### [2026-01-14] Polling vs WebSocket for India Data

**Old Assumption**: REST API polling would be sufficient for India market live data (similar to US/Alpha Vantage).
**New Understanding**: WebSocket streaming is strictly required.
**Trigger**: Rate limits and latency on REST endpoints were practically unusable for 1-minute candle construction for 200+ symbols.

#### Permanent Outcome
REST API polling is permanently invalidated for intraday tick/candle ingestion. Streaming architecture is now the mandatory design standard for this market.

---

### [2026-01-10] Single Data Source Sufficiency

**Old Assumption**: A single data provider (Alpha Vantage) is sufficient for all research.
**New Understanding**: Secondary sources (News/RSS) are required for context.
**Trigger**: Price action alone was insufficient to explain sudden momentum bursts; narrative context was missing.

#### Permanent Outcome
Single-source price action analysis is permanently invalidated as a complete research strategy. Multi-modal context (News + Price) is now a mandatory invariant.
