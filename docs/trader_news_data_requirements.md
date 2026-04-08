# Data Requirements: External News Service -> TraderFund Intelligence Modules

## Context

TraderFund has multiple modules that consume news, narrative, and event intelligence data from an external service (the `trader_news` project at `c:\GIT\trader_news`). The user needs a detailed compilation of **exactly what data** these modules require as input, so that the `trader_news` service can be built/configured to serve it.

This document compiles every data requirement across all consuming modules.

---

## 1. Primary Data Contract: `MarketStory`

**Consumed by:** `MarketStoryAdapter` ([market_story_adapter.py](../traderfund/narrative/adapters/market_story_adapter.py)), `PortfolioEventIntelligenceBuilder` ([news_event_intelligence.py](../src/portfolio_intelligence/news_event_intelligence.py))

**API Endpoint Expected:** `GET {TRADER_NEWS_API_URL}?market={INDIA|US}`
**Response Format:** JSON array of story objects
**Lookback Window:** Configurable via `TRADER_NEWS_LOOKBACK_HOURS` (default: 72 hours)

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | `str` | Unique story identifier | `"story-2026-03-28-001"` |
| `headline` | `str` | Story headline (used for entity matching & narrative title) | `"ASML shipment timing under review"` |
| `summary` | `str` | Story body/summary (used for entity matching & event context) | `"Reports indicate..."` |
| `published_at` | `str` (ISO-8601) | Publication timestamp with timezone | `"2026-03-28T10:00:00+00:00"` |
| `category` | `str` | Story category | `"MARKET_SUMMARY"`, `"CORPORATE"`, `"ECONOMIC_DATA"` |
| `region` | `str` | Geographic region | `"US"`, `"INDIA"`, `"GLOBAL"` |
| `severity_hint` | `str` | Severity classification | `"LOW"`, `"MEDIUM"`, `"HIGH"` |
| `source` | `str` | Origin attribution | `"TraderNews"`, `"Bloomberg"`, `"Reuters"` |

### Optional (Semantic Enrichment) Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `url` | `str \| null` | Link to original article | `"https://..."` |
| `semantic_tags` | `List[str] \| null` | Classification tags (used for entity matching & accumulation clustering) | `["semiconductor", "export_controls"]` |
| `event_type` | `str \| null` | Event classification | `"ECONOMIC_DATA"`, `"GEOPOLITICAL"`, `"CORPORATE"` |
| `expectedness` | `str \| null` | Whether the event was expected | `"EXPECTED"`, `"UNEXPECTED"` |
| `mentioned_entities` | `List[str] \| null` | Entities mentioned in story (used for ticker matching) | `["Hindustan Aeronautics", "ASML"]` |

---

## 2. How Each Field Is Used (Consumption Map)

### 2.1 Entity Matching (PortfolioEventIntelligenceBuilder)
**File:** [news_event_intelligence.py:176-187](../src/portfolio_intelligence/news_event_intelligence.py)

The builder matches stories to portfolio holdings using these fields:
- **`headline`** — normalized text searched for ticker aliases
- **`summary`** — normalized text searched for ticker aliases
- **`mentioned_entities`** — each entity normalized and searched against holdings
- **`semantic_tags`** — each tag normalized and searched against holdings

Entity matching uses case-insensitive substring matching after normalization (strip punctuation, lowercase, collapse whitespace). The richer the `mentioned_entities` list, the more accurate the matching.

### 2.2 Severity / Risk Assessment
**Files:** [market_story_adapter.py:98-124](../traderfund/narrative/adapters/market_story_adapter.py), [news_event_intelligence.py:209-211](../src/portfolio_intelligence/news_event_intelligence.py)

- **`severity_hint`** maps to:
  - Narrative weight: `LOW=0.4`, `MEDIUM=0.6`, `HIGH=0.8`
  - Narrative engine severity score: `weight * 100.0` (0-100 scale)
  - Portfolio risk level: direct pass-through (`HIGH`, `MEDIUM`, `LOW`)
  - Aggregate sentiment: `LOW=0.2`, `MEDIUM=0.5`, `HIGH=0.8` (averaged per ticker)

### 2.3 Narrative Genesis Engine
**File:** [market_story_adapter.py:219-266](../traderfund/narrative/adapters/market_story_adapter.py)

Stories are bridged to `Event` objects for the narrative engine:
- **`headline`** → `payload.signal_name` (drives narrative title)
- **`summary`** → `payload.summary`
- **`source`** → `source_reference` (prefixed with `ADAPTER:`)
- **`published_at`** → `event.timestamp`
- **`semantic_tags`** → `payload.semantic_tags` (used by AccumulationBuffer for clustering LOW events; 3 events with same tag in 48hrs = synthetic MEDIUM event)
- **`event_type`** → `payload.event_type`
- **`expectedness`** → `payload.expectedness`
- **`region`** → determines scope (`GLOBAL` → global scope, else `ASSETS`)

### 2.4 Stock Research Engine
**File:** [stock_research_engine.py:271-319](../src/portfolio_intelligence/stock_research_engine.py)

Consumes the processed `stock_event_map` (derived from stories):
- `event_risk_flag` (bool) → triggers risk flag on stock profile
- `potential_risk_implications` (str) → risk flag explanation
- `monitoring_status` → `NO_ACTIVE_EVENT` / `ACTIVE_MONITOR` / `ACTIVE_MONITOR_HIGH`
- `narrative_summary` → included in research narrative text

### 2.5 Portfolio Narrative Synthesis
**File:** [synthesis.py:9-35](../src/portfolio_intelligence/synthesis.py)

Consumes `portfolio_event_alerts`:
- `ticker` — which holding
- `event_summary` — headline for material event watch text

### 2.6 Dashboard API Endpoints
**File:** [app.py](../src/dashboard/backend/app.py), [portfolio.py](../src/dashboard/backend/loaders/portfolio.py)

Exposed to frontend:
- `GET /api/portfolio/research/{market}/{portfolio_id}` — returns `news_adapter_status`, `portfolio_event_alerts`, `portfolio_event_timeline`
- `GET /api/portfolio/advisory/{market}/{portfolio_id}` — returns news-driven suggestions
- `GET /api/portfolio/combined` — aggregated cross-market with event intelligence

### 2.7 Deduplication
**File:** [market_story_adapter.py:63-67](../traderfund/narrative/adapters/market_story_adapter.py)

Dedup key = MD5 of `{headline}|{published_at}|{source}`. These three fields MUST be stable across fetches for the same story to avoid re-ingestion.

---

## 3. API Contract Requirements

### 3.1 Endpoint
```
GET {TRADER_NEWS_API_URL}?market={market}
```
- `market` parameter: `"INDIA"` or `"US"`
- Response: JSON array of MarketStory objects
- HTTP 200 on success

### 3.2 Timeout & Retry
- TraderFund retries **3 times** with **5-second timeout** per attempt
- On total failure: falls back to local cache, returns `FETCH_EMPTY_OR_FAILED` status

### 3.3 Response Ordering
- Stories should ideally be sorted by `published_at` (ascending or descending)
- TraderFund re-sorts by `published_at` after fetch regardless

### 3.4 Time Filtering
- TraderFund filters stories by `published_at >= (now - lookback_hours)`
- Default lookback: 72 hours
- Stories older than the lookback window are discarded client-side

### 3.5 Idempotency
- Same story fetched multiple times is fine — TraderFund deduplicates via MD5(headline|timestamp|source)
- `id` field must be stable per story

---

## 4. Data Quality Requirements

### 4.1 Critical for Accuracy
1. **`mentioned_entities`** — The single most impactful field for portfolio-to-news mapping accuracy. Should include:
   - Full company names (e.g., "Hindustan Aeronautics Limited")
   - Common abbreviations (e.g., "HAL")
   - Ticker symbols where applicable
   - Related entities mentioned in the story

2. **`severity_hint`** — Directly drives risk assessment, narrative weight, and alert priority. Must be calibrated:
   - `HIGH`: Earnings miss, regulatory action, material corporate event, geopolitical shock
   - `MEDIUM`: Analyst revision, sector rotation signal, management change, contract review
   - `LOW`: Routine market commentary, scheduled data release matching expectations

3. **`semantic_tags`** — Drives the AccumulationBuffer clustering. Multiple LOW events with the same semantic tag within 48 hours get promoted to a synthetic MEDIUM event. Good tags improve signal detection.

### 4.2 Entity Matching Enhancement Opportunities
Current manual aliases are limited to 3 tickers:
```python
HAL  -> ["hindustan aeronautics", "hindustan aeronautics limited", "hal"]
ASML -> ["asml", "asml holding", "asml holdings"]
LT   -> ["larsen and toubro", "larsen & toubro", "lt"]
```
The `mentioned_entities` field in the API response can supplement this — any entity name that matches a holding's `ticker` or `security_name` (after normalization) will create a link.

---

## 5. Complete Data Flow Summary

```
trader_news service
    |
    | GET {TRADER_NEWS_API_URL}?market=INDIA
    | Returns: [MarketStory, MarketStory, ...]
    v
MarketStoryAdapter (fetch + dedup + convert)
    |
    +--> NarrativeGenesisEngine (shadow mode)
    |     |-> Clustering / Genesis / Accumulation
    |     |-> RegimeEnforcedRepository (weight adjustment)
    |     +-> ParquetNarrativeRepository (persistence)
    |
    +--> PortfolioEventIntelligenceBuilder
          |-> Entity matching (story text -> portfolio tickers)
          |-> Event record creation (risk level, implications)
          |-> Aggregate sentiment per ticker
          |
          +--> EventIntelligenceResult
                |-> stock_event_map      -> StockResearchEngine (risk flags, monitoring)
                |-> portfolio_event_alerts -> PortfolioNarrativeSynthesizer (narrative text)
                |-> portfolio_event_timeline -> Dashboard API (chronological view)
                +-> adapter_status       -> Dashboard API (feed health indicator)
```

---

## 6. Configuration Required

| Environment Variable | Purpose | Default |
|---------------------|---------|---------|
| `TRADER_NEWS_API_URL` | Base URL of the trader_news service API | (empty — disables feed) |
| `TRADER_NEWS_LOOKBACK_HOURS` | Hours of historical stories to fetch | `72` |

---

## 7. Consuming Modules Inventory

| Module | File | What It Consumes | What It Produces |
|--------|------|------------------|------------------|
| MarketStoryAdapter | `traderfund/narrative/adapters/market_story_adapter.py` | Raw MarketStory JSON from API | NarrativeInput, Event objects for genesis engine |
| PortfolioEventIntelligenceBuilder | `src/portfolio_intelligence/news_event_intelligence.py` | MarketStory objects (via adapter or cache) | EventIntelligenceResult (stock_event_map, alerts, timeline) |
| StockResearchEngine | `src/portfolio_intelligence/stock_research_engine.py` | stock_event_map per ticker | Risk flags, monitoring status, research narrative |
| PortfolioNarrativeSynthesizer | `src/portfolio_intelligence/synthesis.py` | portfolio_event_alerts | Human-readable event narrative text |
| PortfolioStrategyEngine | `src/portfolio_intelligence/portfolio_strategy_engine.py` | research_profiles (with embedded event data) | Risk alerts, strategy suggestions |
| NarrativeGenesisEngine | `narratives/genesis/engine.py` | Event objects from adapter bridge | Narrative objects (clustered, accumulated) |
| RegimeEnforcedRepository | `narratives/repository/regime_enforced.py` | Narrative objects | Regime-adjusted narratives with telemetry |
| AccumulationBuffer | `narratives/genesis/accumulator.py` | LOW-severity events grouped by semantic_tag | Synthetic MEDIUM events (3 LOWs in 48hrs) |
| News Sentiment Runner | `research_modules/news_sentiment/runner.py` | NewsArticle objects (separate ingestion path) | SentimentSnapshot per symbol |
| Narrative Evolution | `research_modules/narrative_evolution/generator.py` | StageEvidence scores | NarrativeType classification, state transitions |
| Narrative Diff Detector | `research_modules/narrative_diff/detector.py` | Previous vs current narrative | ChangeType (PROMOTION, DEGRADATION, etc.) |

---

## 8. Verification

To verify the integration end-to-end:

1. **Set environment variable:** `TRADER_NEWS_API_URL=http://localhost:8000/api/stories` (or wherever trader_news serves)
2. **Run portfolio refresh** — `python scripts/portfolio_tracker_refresh.py`
3. **Check adapter status** — Look for `"status": "FETCH_OK"` in the portfolio analytics output
4. **Verify entity matching** — Check `portfolio_event_alerts` contains matched holdings
5. **Check dashboard** — `GET /api/portfolio/research/INDIA/{portfolio_id}` should include `news_adapter_status`, `portfolio_event_alerts`, `portfolio_event_timeline`
6. **Run tests** — `pytest tests/test_portfolio_news_event_intelligence.py`

---

## 9. Summary: What trader_news Must Provide

The `trader_news` service needs a single API endpoint that returns a JSON array where each element conforms to the `MarketStory` schema (Section 1). The minimum viable fields are the 8 required fields. For high-quality intelligence, the 5 optional semantic enrichment fields (especially `mentioned_entities` and `semantic_tags`) should also be populated.
