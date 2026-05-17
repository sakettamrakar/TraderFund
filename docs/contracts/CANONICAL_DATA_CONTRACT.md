# Canonical Data Contract

**Created:** 2026-05-17
**Source:** `traderfund/pipeline/artifact_contract.py`
**Purpose:** Declares all canonical artifact locations, producers, and schemas.

---

## Market Modes

| Mode | Description | Credentials Required | Notes |
| :--- | :--- | :--- | :--- |
| `fixture` | Committed test data | No | Safe for CI, local dev, dry-run |
| `US` | Alpha Vantage REST | `ALPHA_VANTAGE_API_KEY` | US daily OHLCV |
| `INDIA` | Angel One SmartAPI | `ANGEL_API_KEY`, `ANGEL_CLIENT_ID`, `ANGEL_PASSWORD`, `ANGEL_TOTP_SECRET` | Intraday ticks via WebSocket |

See `traderfund/pipeline/market_modes.py` for programmatic details.

---

## Artifact Registry

### Ingestion — Raw

| Artifact ID | Producer | Path Pattern | Format | Required Columns |
| :--- | :--- | :--- | :--- | :--- |
| `ingestion_raw_india` | `ingestion.angel_smartapi` | `data/raw/api_based/angel/intraday_ohlc/*.jsonl` | JSONL | symbol, exchange, interval, timestamp, open, high, low, close, volume, source, ingestion_ts |
| `ingestion_raw_us` | `ingestion.alpha_vantage` | `data/raw/us/*/*_daily.json` | JSON | timestamp, open, high, low, close, volume |

### Ingestion — Processed

| Artifact ID | Producer | Path Pattern | Format | Required Columns |
| :--- | :--- | :--- | :--- | :--- |
| `ingestion_processed_india` | `processing.intraday_candles_processor` | `data/processed/candles/intraday/*.parquet` | Parquet | symbol, exchange, timestamp, open, high, low, close, volume |

### Fixture

| Artifact ID | Producer | Path Pattern | Format |
| :--- | :--- | :--- | :--- |
| `fixture_raw` | `fixture_generator` | `data/fixtures/raw/*.jsonl` | JSONL |
| `fixture_processed` | `fixture_generator` | `data/fixtures/processed/*.parquet` | Parquet |
| `fixture_us_daily` | `fixture_generator` | `data/fixtures/us/*.json` | JSON |

### Research

| Artifact ID | Producer | Path Pattern | Format |
| :--- | :--- | :--- | :--- |
| `research_intelligence_snapshot` | `intelligence.engine` | `docs/intelligence/intelligence_*_{date}.json` | JSON |
| `research_factor_context` | `evolution.factor_context_builder` | `docs/evolution/context/*.json` | JSON |

### Evaluation

| Artifact ID | Producer | Path Pattern | Format | Required Columns |
| :--- | :--- | :--- | :--- | :--- |
| `evaluation_activation_matrix` | `evolution.pipeline_runner` | `docs/evolution/evaluation/**/strategy_activation_matrix.csv` | CSV | strategy_id, decisions, shadow, failures, regime |
| `evaluation_decision_trace` | `evolution.pipeline_runner` | `docs/evolution/evaluation/**/decision_trace_log.parquet` | Parquet | — |

### Pipeline

| Artifact ID | Producer | Path Pattern | Format |
| :--- | :--- | :--- | :--- |
| `pipeline_manifest` | `traderfund.pipeline.daily` | `logs/validation/pipeline_manifest.json` | JSON |

---

## Pipeline Manifest Schema

The manifest is emitted by `python -m traderfund.pipeline.daily` and contains:

```json
{
  "generated_at": "ISO-8601",
  "market_mode": "fixture | US | INDIA",
  "pipeline_version": "1.0",
  "entries": [
    {
      "artifact_id": "...",
      "producer": "...",
      "path": "relative/to/repo/root",
      "schema_version": "1.0",
      "format": "jsonl | parquet | json | csv",
      "produced_at": "ISO-8601 or empty",
      "market_mode": "...",
      "status": "present | missing | skipped",
      "missing_reason": "actionable message or empty"
    }
  ],
  "validation_summaries": {
    "ingestion": { "phase": "...", "has_failures": false, ... }
  }
}
```

---

## How to Use

1. **Pipeline stages** read the manifest to find their input artifacts.
2. **Validators** resolve artifact paths via `_resolve_artifact()` which checks the manifest first, then falls back to glob patterns.
3. **Dashboard loaders** will read the manifest to determine freshness and provenance.
4. **Missing artifacts** produce actionable errors naming the producer stage and expected path pattern.
