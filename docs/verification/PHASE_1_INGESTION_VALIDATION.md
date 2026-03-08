# Phase 1: Ingestion Validation (Live Data Parity)

**Target Layer**: L0 Ingestion (US & India)
**Obligation Focus**: `OBL-MARKET-PARITY`, `INV-PROXY-CANONICAL`

## 1.1 Ingestion Parity Test (Dry-Run)

Validate that both US and India pipelines can ingest the target epoch data without structurally favoring one schema over the other.

- [ ] **Task 1.1.1 (US Ingestion)**: Execute `relay` to fetch daily OHLCV for US Market Proxy (SPY) for `TE-2026-01-30`. Assert response schema conforms exactly to `PROCESSED_SCHEMA`.
- [ ] **Task 1.1.2 (India Ingestion)**: Execute `relay` to fetch daily OHLCV for India Market Proxy (NIFTY 50) for `TE-2026-01-30`. Assert response schema strictly matches the exact same baseline attributes.
- [ ] **Task 1.1.3 (Parity Enforcement)**: Script asserts that no US-specific metadata bleeds into the generalized object, and no India-specific metadata requires a separate code path.

## 1.2 Canonical Proxy Baseline Test

Verify that only canonically approved proxies are utilized during real-data ingestion.

- [ ] **Task 1.2.1**: Fire ingestion triggers for random indices outside the approved `docs/contracts/market_proxy_sets.md`. 
- [ ] **Task 1.2.2**: Assert the pipeline explicitly REJECTS these payloads and surfaces an exception (`INV-PROXY-CANONICAL` violation), rather than silently creating an orphaned record.

## 1.3 Immutable Ingestion Test

Ensure that multiple runs over the same truth epoch yield bitwise identical raw parquet blocks, validating that the ingestion process does not mutate historical data.

- [ ] **Task 1.3.1**: Run ingestion sequence A for TE-2026-01-30. Store hash.
- [ ] **Task 1.3.2**: Run ingestion sequence B for TE-2026-01-30. Store hash.
- [ ] **Task 1.3.3**: Validate `Hash(A) == Hash(B)`. Fail the pipeline if random timestamps or variable headers cause hash drift.
