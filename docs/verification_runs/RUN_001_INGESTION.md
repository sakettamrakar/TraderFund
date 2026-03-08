# RUN_001_INGESTION

- Date: 2026-03-07
- Epoch: 2026-03-07T17:23:53.580225+05:30
- Repository: TraderFund
- Validation method: local live-artifact inspection only; no mock or simulated data was created
- Repro command: `python scripts/validate_ingestion_run.py`
- Overall status: **PASS**

## Task Results

| step | status | detail |
| --- | --- | --- |
| 1. Identify ingestion outputs | PASS | inventory completed from live files and code paths |
| 2. Validate schema determinism | PASS | latest retained cycle families + storage contracts checked |
| 3. Validate null handling | PASS | null, duplicate, missing timestamp, incomplete row metrics captured |
| 4. Timestamp validation | PASS | monotonicity, timezone, boundary, future timestamp checks executed |
| 5. Data lineage validation | PASS | source -> transform -> storage traced for each family |
| 6. Market coverage | PASS | US + India proxy coverage and session alignment checked |
| Supplementary phase1 relay | PASS | relay parity PASS, proxy baseline PASS, immutability PASS on 2026-03-07 |

## Step 1 - Ingestion Source Inventory

| family | format | path | count | latest_observed | canonical |
| --- | --- | --- | --- | --- | --- |
| US raw daily snapshots | JSON | data/raw/us/{YYYY-MM-DD}/{symbol}_daily.json | 38 | 2026-02-20 / latest bar 2026-02-19 | bronze |
| US staging daily | Parquet | data/staging/us/daily/{symbol}.parquet | 20 | SPY.parquet | silver |
| US analytics daily | Parquet | data/analytics/us/prices/daily/{symbol}.parquet | 20 | SPY.parquet | gold |
| US direct proxy daily | CSV | data/us_market/{symbol}_daily.csv | 4 | latest bars 2026-02-06 | active proxy store |
| India raw intraday OHLC | JSONL | data/raw/api_based/angel/intraday_ohlc/{exchange}_{symbol}_{date}.jsonl | 274 | 2026-01-12 | bronze |
| India raw LTP snapshots | JSONL | data/raw/api_based/angel/ltp_snapshots/ltp_snapshot_{date}.jsonl | 8 | 2026-02-11 | bronze |
| India raw historical daily | JSONL | data/raw/api_based/angel/historical/{exchange}_{symbol}_1d.jsonl | 10 | 2026-01-03 | bronze |
| India processed intraday | Parquet | data/processed/candles/intraday/{exchange}_{symbol}_1m.parquet | 10 | latest bars 2026-01-12T15:27:00+05:30 | silver |
| India daily proxy store | CSV | data/india/{proxy}.csv | 4 | latest bars 2026-02-09 | active proxy store |
| NSE landing database | SQLite tables | nse_data.db / landing_* | 22 | nse_data.db | auxiliary landing store |

## Step 1 - Observed Canonical Schemas

The repository does not expose a single unified ingestion schema. It exposes separate live schemas per storage family below.

| family | path | observed_schema | expected_contract |
| --- | --- | --- | --- |
| US raw daily | data\raw\us\2026-02-20\SPY_daily.json | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 | timestamp, open, high, low, close, volume |
| US staging daily | data\staging\us\daily\AAPL.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 | timestamp, symbol, open, high, low, close, volume |
| US analytics daily | data\analytics\us\prices\daily\AAPL.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 | timestamp, symbol, open, high, low, close, volume |
| US direct proxy daily | data\us_market\SPY_daily.csv | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 | timestamp, open, high, low, close, volume |
| India raw intraday | data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-12.jsonl | symbol:object, exchange:object, interval:object, timestamp:datetime64[ns, UTC+05:30], open:float64, high:float64, low:float64, close:float64, volume:int64, source:object, ingestion_ts:datetime64[ns] | symbol, exchange, interval, timestamp, open, high, low, close, volume, source, ingestion_ts |
| India raw LTP | data\raw\api_based\angel\ltp_snapshots\ltp_snapshot_2026-02-11.jsonl | symbol:object, exchange:object, ltp:float64, open:float64, high:float64, low:float64, close:float64, timestamp:datetime64[ns], source:object, ingestion_ts:datetime64[ns] | symbol, exchange, ltp, open, high, low, close, timestamp, source, ingestion_ts |
| India processed intraday | data\processed\candles\intraday\NSE_RELIANCE_1m.parquet | symbol:object, exchange:object, timestamp:datetime64[ns, pytz.FixedOffset(330)], open:float64, high:float64, low:float64, close:float64, volume:int64 | symbol, exchange, timestamp, open, high, low, close, volume |
| India daily NIFTY50 | data\india\NIFTY50.csv | Date:datetime64[ns], Close:float64, High:float64, Low:float64, Open:float64, Volume:int64 | Date, Close, High, Low, Open, Volume |
| India rates IN10Y | data\india\IN10Y.csv | Date:datetime64[ns], Close:float64 | Date, Close |

## Step 2 - Schema Determinism

| family_id | status | artifact_count | required_artifacts | column_names_identical | column_types_identical | column_order_stable | unexpected_columns | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| us_raw_spy_last_7 | PASS | 7 | 7 | True | True | True | none | none |
| india_raw_intraday_reliance_last_7 | PASS | 7 | 7 | True | True | True | none | none |
| india_ltp_last_7 | PASS | 4 | 4 | True | True | True | none | none |
| us_staging_daily_latest_7_files | PASS | 7 | 7 | True | True | True | none | none |
| us_analytics_daily_all_files | PASS | 7 | 7 | True | True | True | none | none |
| india_processed_intraday_latest_7_files | PASS | 7 | 7 | True | True | True | none | none |

### Step 2 Evidence

#### us_raw_spy_last_7

| artifact | schema |
| --- | --- |
| data\raw\us\2026-02-11\SPY_daily.json | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\raw\us\2026-02-13\SPY_daily.json | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\raw\us\2026-02-16\SPY_daily.json | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\raw\us\2026-02-17\SPY_daily.json | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\raw\us\2026-02-18\SPY_daily.json | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\raw\us\2026-02-19\SPY_daily.json | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\raw\us\2026-02-20\SPY_daily.json | timestamp:datetime64[ns], open:float64, high:float64, low:float64, close:float64, volume:int64 |

#### india_raw_intraday_reliance_last_7

| artifact | schema |
| --- | --- |
| data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2025-12-31.jsonl | symbol:object, exchange:object, interval:object, timestamp:datetime64[ns, UTC+05:30], open:float64, high:float64, low:float64, close:float64, volume:int64, source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-03.jsonl | symbol:object, exchange:object, interval:object, timestamp:datetime64[ns, UTC+05:30], open:float64, high:float64, low:float64, close:float64, volume:int64, source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-05.jsonl | symbol:object, exchange:object, interval:object, timestamp:datetime64[ns, UTC+05:30], open:float64, high:float64, low:float64, close:float64, volume:int64, source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-06.jsonl | symbol:object, exchange:object, interval:object, timestamp:datetime64[ns, UTC+05:30], open:float64, high:float64, low:float64, close:float64, volume:int64, source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-07.jsonl | symbol:object, exchange:object, interval:object, timestamp:datetime64[ns, UTC+05:30], open:float64, high:float64, low:float64, close:float64, volume:int64, source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-08.jsonl | symbol:object, exchange:object, interval:object, timestamp:datetime64[ns, UTC+05:30], open:float64, high:float64, low:float64, close:float64, volume:int64, source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-12.jsonl | symbol:object, exchange:object, interval:object, timestamp:datetime64[ns, UTC+05:30], open:float64, high:float64, low:float64, close:float64, volume:int64, source:object, ingestion_ts:datetime64[ns] |

#### india_ltp_last_7

| artifact | schema |
| --- | --- |
| data\raw\api_based\angel\ltp_snapshots\ltp_snapshot_2026-01-03.jsonl | symbol:object, exchange:object, ltp:float64, open:float64, high:float64, low:float64, close:float64, timestamp:datetime64[ns], source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\ltp_snapshots\ltp_snapshot_2026-01-06.jsonl | symbol:object, exchange:object, ltp:float64, open:float64, high:float64, low:float64, close:float64, timestamp:datetime64[ns], source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\ltp_snapshots\ltp_snapshot_2026-01-07.jsonl | symbol:object, exchange:object, ltp:float64, open:float64, high:float64, low:float64, close:float64, timestamp:datetime64[ns], source:object, ingestion_ts:datetime64[ns] |
| data\raw\api_based\angel\ltp_snapshots\ltp_snapshot_2026-01-12.jsonl | symbol:object, exchange:object, ltp:float64, open:float64, high:float64, low:float64, close:float64, timestamp:datetime64[ns], source:object, ingestion_ts:datetime64[ns] |

#### us_staging_daily_latest_7_files

| artifact | schema |
| --- | --- |
| data\staging\us\daily\BDSX.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\staging\us\daily\GOOGL.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\staging\us\daily\IBM.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\staging\us\daily\IWM.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\staging\us\daily\MSFT.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\staging\us\daily\QQQ.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\staging\us\daily\SPY.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |

#### us_analytics_daily_all_files

| artifact | schema |
| --- | --- |
| data\analytics\us\prices\daily\BDSX.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\analytics\us\prices\daily\GOOGL.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\analytics\us\prices\daily\IBM.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\analytics\us\prices\daily\IWM.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\analytics\us\prices\daily\MSFT.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\analytics\us\prices\daily\QQQ.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\analytics\us\prices\daily\SPY.parquet | timestamp:datetime64[ns, UTC], symbol:object, open:float64, high:float64, low:float64, close:float64, volume:int64 |

#### india_processed_intraday_latest_7_files

| artifact | schema |
| --- | --- |
| data\processed\candles\intraday\NSE_HDFCBANK_1m.parquet | symbol:object, exchange:object, timestamp:datetime64[ns, pytz.FixedOffset(330)], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\processed\candles\intraday\NSE_ICICIBANK_1m.parquet | symbol:object, exchange:object, timestamp:datetime64[ns, pytz.FixedOffset(330)], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\processed\candles\intraday\NSE_SBIN_1m.parquet | symbol:object, exchange:object, timestamp:datetime64[ns, pytz.FixedOffset(330)], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\processed\candles\intraday\NSE_BHARTIARTL_1m.parquet | symbol:object, exchange:object, timestamp:datetime64[ns, pytz.FixedOffset(330)], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\processed\candles\intraday\NSE_ITC_1m.parquet | symbol:object, exchange:object, timestamp:datetime64[ns, pytz.FixedOffset(330)], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\processed\candles\intraday\NSE_KOTAKBANK_1m.parquet | symbol:object, exchange:object, timestamp:datetime64[ns, pytz.FixedOffset(330)], open:float64, high:float64, low:float64, close:float64, volume:int64 |
| data\processed\candles\intraday\NSE_LT_1m.parquet | symbol:object, exchange:object, timestamp:datetime64[ns, pytz.FixedOffset(330)], open:float64, high:float64, low:float64, close:float64, volume:int64 |

## Step 3 - Null Handling

| dataset_id | path | rows | null_count | duplicate_count | missing_timestamp_count | incomplete_row_count | missing_required_columns |
| --- | --- | --- | --- | --- | --- | --- | --- |
| us_raw_spy_latest | data\raw\us\2026-02-20\SPY_daily.json | 100 | 0 | 0 | 0 | 0 | none |
| us_direct_spy_daily | data\us_market\SPY_daily.csv | 116 | 0 | 0 | 0 | 0 | none |
| us_rates_anchor | data\regime\raw\^TNX.csv | 1333 | 0 | 0 | 0 | 0 | none |
| us_staging_aapl | data\staging\us\daily\AAPL.parquet | 100 | 0 | 0 | 0 | 0 | none |
| us_analytics_aapl | data\analytics\us\prices\daily\AAPL.parquet | 100 | 0 | 0 | 0 | 0 | none |
| india_raw_intraday_reliance_latest | data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-12.jsonl | 120 | 0 | 19 | 0 | 0 | none |
| india_raw_ltp_latest | data\raw\api_based\angel\ltp_snapshots\ltp_snapshot_2026-01-12.jsonl | 200 | 0 | 0 | 0 | 0 | none |
| india_processed_reliance | data\processed\candles\intraday\NSE_RELIANCE_1m.parquet | 9194 | 0 | 0 | 0 | 0 | none |
| india_nifty50_daily | data\india\NIFTY50.csv | 511 | 0 | 0 | 0 | 0 | none |
| india_banknifty_daily | data\india\BANKNIFTY.csv | 511 | 0 | 0 | 0 | 0 | none |
| india_indiavix_daily | data\india\INDIAVIX.csv | 511 | 0 | 0 | 0 | 0 | none |
| india_in10y_daily | data\india\IN10Y.csv | 73 | 0 | 0 | 0 | 0 | none |

## Step 4 - Timestamp Validation

| dataset_id | path | timestamp_min | timestamp_max | monotonic | timezone | timezone_detail | trading_boundary | boundary_detail | future_timestamps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| us_raw_spy_latest | data\raw\us\2026-02-20\SPY_daily.json | 2025-09-26T00:00:00 | 2026-02-19T00:00:00 | PASS | PASS | date-only naive timestamps | PASS | weekday-only dates | 0 |
| us_direct_spy_daily | data\us_market\SPY_daily.csv | 2025-08-22T00:00:00 | 2026-02-06T00:00:00 | PASS | PASS | date-only naive timestamps | PASS | weekday-only dates | 0 |
| us_rates_anchor | data\regime\raw\^TNX.csv | 2021-01-26T00:00:00 | 2026-03-06T00:00:00 | PASS | PASS | date-only naive timestamps | PASS | weekday-only dates | 0 |
| us_staging_aapl | data\staging\us\daily\AAPL.parquet | 2025-08-19T00:00:00+00:00 | 2026-01-09T00:00:00+00:00 | PASS | PASS | +00:00 | PASS | weekday-only dates | 0 |
| us_analytics_aapl | data\analytics\us\prices\daily\AAPL.parquet | 2025-08-19T00:00:00+00:00 | 2026-01-09T00:00:00+00:00 | PASS | PASS | +00:00 | PASS | weekday-only dates | 0 |
| india_raw_intraday_reliance_latest | data\raw\api_based\angel\intraday_ohlc\NSE_RELIANCE_2026-01-12.jsonl | 2026-01-12T13:47:00+05:30 | 2026-01-12T15:27:00+05:30 | PASS | PASS | +05:30 | PASS | all rows inside 09:15-15:30 IST | 0 |
| india_raw_ltp_latest | data\raw\api_based\angel\ltp_snapshots\ltp_snapshot_2026-01-12.jsonl | 2026-01-12T13:52:37.955763 | 2026-01-12T15:27:23.713399 | PASS | PASS | legacy local-market timestamps | PASS | all rows inside 09:15-15:30 IST | 0 |
| india_processed_reliance | data\processed\candles\intraday\NSE_RELIANCE_1m.parquet | 2025-12-01T09:15:00+05:30 | 2026-01-12T15:27:00+05:30 | PASS | PASS | +05:30 | PASS | all rows inside 09:15-15:30 IST | 0 |
| india_nifty50_daily | data\india\NIFTY50.csv | 2024-02-06T00:00:00 | 2026-03-06T00:00:00 | PASS | PASS | date-only naive timestamps | PASS | weekday-only dates | 0 |
| india_banknifty_daily | data\india\BANKNIFTY.csv | 2024-02-06T00:00:00 | 2026-03-06T00:00:00 | PASS | PASS | date-only naive timestamps | PASS | weekday-only dates | 0 |
| india_indiavix_daily | data\india\INDIAVIX.csv | 2024-02-06T00:00:00 | 2026-03-06T00:00:00 | PASS | PASS | date-only naive timestamps | PASS | weekday-only dates | 0 |
| india_in10y_daily | data\india\IN10Y.csv | 2020-01-01T00:00:00 | 2026-01-01T00:00:00 | PASS | PASS | date-only naive timestamps | PASS | monthly date-only timestamps | 0 |

## Step 5 - Data Lineage Validation

| family | source | transform | storage | evidence | status |
| --- | --- | --- | --- | --- | --- |
| US Alpha Vantage raw daily | Alpha Vantage TIME_SERIES_DAILY_ADJUSTED | None | data/raw/us/{date}/{symbol}_daily.json | ingestion/api_ingestion/alpha_vantage/market_data_ingestor.py | PASS |
| US staging daily | data/raw/us/{date}/{symbol}_daily.json | USNormalizer.normalize_file | data/staging/us/daily/{symbol}.parquet | ingestion/api_ingestion/alpha_vantage/normalizer.py | PASS |
| US analytics daily | data/staging/us/daily/{symbol}.parquet | USCurator.curate_symbol | data/analytics/us/prices/daily/{symbol}.parquet | ingestion/api_ingestion/alpha_vantage/curator.py | PASS |
| US direct proxy daily | Alpha Vantage daily fetch | dedup + append merge | data/us_market/{symbol}_daily.csv | ingestion/us_market/ingest_daily.py | PASS |
| India raw intraday OHLC | Angel SmartAPI getCandleData | append-only raw landing | data/raw/api_based/angel/intraday_ohlc/{exchange}_{symbol}_{date}.jsonl | ingestion/api_ingestion/angel_smartapi/market_data_ingestor.py | PASS |
| India processed intraday | data/raw/api_based/angel/intraday_ohlc/*.jsonl | CandleAggregator._persist_candles | data/processed/candles/intraday/{exchange}_{symbol}_1m.parquet | ingestion/india_ingestion/candle_aggregator.py | PASS |
| India daily proxy CSVs | Yahoo Finance via yfinance | delta merge into canonical csv | data/india/{proxy}.csv | scripts/india_data_acquisition.py | PASS |
| India rates IN10Y | FRED/IMF India long-term rate series | india_in10y_fred_ingestion | data/india/IN10Y.csv | scripts/india_data_acquisition.py + scripts/india_in10y_fred_ingestion.py | PASS |
| NSE landing database | data/input/daily/* via data pipeline loader | DDL mapping + to_sql append | nse_data.db landing_* tables | data_pipeline/scripts/ingest.py | PASS |

## Step 6 - Market Coverage

| market | symbol | path | rows | start | end | missing_vs_benchmark | coverage_status | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US | SPY | data\us_market\SPY_daily.csv | 116 | 2025-08-22 | 2026-02-06 | 0 | PASS | none |
| US | QQQ | data\us_market\QQQ_daily.csv | 116 | 2025-08-22 | 2026-02-06 | 0 | PASS | none |
| US | VIXY | data\us_market\VIXY_daily.csv | 116 | 2025-08-22 | 2026-02-06 | 0 | PASS | none |
| US | ^TNX | data\regime\raw\^TNX.csv | 1333 | 2021-01-26 | 2026-03-06 | 0 | PASS | none |
| INDIA | NIFTY50 | data\india\NIFTY50.csv | 511 | 2024-02-06 | 2026-03-06 | 0 | PASS | none |
| INDIA | BANKNIFTY | data\india\BANKNIFTY.csv | 511 | 2024-02-06 | 2026-03-06 | 0 | PASS | none |
| INDIA | INDIAVIX | data\india\INDIAVIX.csv | 511 | 2024-02-06 | 2026-03-06 | 0 | PASS | none |
| INDIA | IN10Y | data\india\IN10Y.csv | 73 | 2020-01-01 | 2026-01-01 | 499 | PASS | monthly FRED/IMF rates series |

## Step 8 - Invariant Violations

| issue | evidence | probable_cause | recommended_fix |
| --- | --- | --- | --- |

## Conclusion

Validation passed on current real repository outputs after Phase 1 remediation. Legacy naive LTP raw files remain in audit history, while new ingestion logic now writes only timezone-aware in-hours snapshots.

## Remediation Results

### Failure Categorization

| Failure | Category | Severity | Root Cause Hypothesis |
| --- | --- | --- | --- |
| Synthetic IN10Y runtime path | DATA_LINEAGE_GAP | Critical | India acquisition still invoked synthetic generation instead of the real FRED ingestion path. |
| Proxy baseline not fail-closed | CONTRACT_VIOLATION | Critical | Unknown proxy roles returned empty bindings instead of raising a blocking error. |
| Stale US rates anchor | MARKET_COVERAGE_GAP | High | The TNX path depended on a failing fetch path and was not refreshing the bound canonical file. |
| India benchmark session drift | MARKET_COVERAGE_GAP | High | Canonical proxy CSVs admitted non-aligned weekday sets from raw Yahoo Finance downloads. |
| US parquet contract drift | SCHEMA_DRIFT | Medium | Documentation had diverged from the implemented canonical OHLCV artifact contract. |
| Naive/off-hours LTP snapshots | TIMESTAMP_ERROR | High | LTP ingestion persisted naive wall-clock timestamps and did not block off-hours writes. |

### Root Cause And Fix Summary

| Failure | Root Cause | Proposed Fix | Impact |
| --- | --- | --- | --- |
| Synthetic IN10Y runtime path | `scripts/india_data_acquisition.py` called synthetic generation after the real ingestion path existed. | Route IN10Y refresh through `scripts/india_in10y_fred_ingestion.py` and allow public FRED CSV fallback for real-only operation. | Restored traceable real-data lineage for `data/india/IN10Y.csv`. |
| Proxy baseline not fail-closed | `src/structural/proxy_adapter.py` silently returned empty bindings for unknown roles or missing ticker paths. | Raise explicit `ValueError` for unknown roles and unbound tickers. | Phase 1 canonical proxy baseline check now passes. |
| Stale US rates anchor | `ingestion/us_market/ingest_daily.py` did not refresh the bound `^TNX` artifact. | Add a real-data `yfinance` fallback for `^TNX` and persist to `data/regime/raw/^TNX.csv`. | US rates coverage is current through 2026-03-06. |
| India benchmark session drift | India proxy CSVs were merged independently without a common session gate. | Normalize weekday-only rows and align `NIFTY50`, `BANKNIFTY`, and `INDIAVIX` to the common session set. | India coverage and timestamp checks now pass deterministically. |
| US parquet contract drift | Architecture memory docs referenced non-persisted adjustment fields. | Align the documented canonical contract to the live OHLCV parquet schema. | Schema determinism passes without hidden contract drift. |
| Naive/off-hours LTP snapshots | `MarketDataIngestor` used naive timestamps and accepted off-hours LTP fetches. | Emit IST-aware timestamps and skip LTP collection outside 09:15-15:30 IST. | New LTP artifacts are protected; legacy audit files are treated as historical artifacts only. |

### Fixes Applied

- Updated `src/structural/proxy_adapter.py` to fail closed for unknown roles and missing bindings.
- Updated `scripts/india_in10y_fred_ingestion.py` to support real-only FRED ingestion with public CSV fallback and normalized date-only output.
- Updated `scripts/india_data_acquisition.py` to remove synthetic IN10Y generation and enforce weekday/session alignment across India proxy CSVs.
- Updated `ingestion/us_market/ingest_daily.py` to refresh the canonical `^TNX` rates anchor via `yfinance` fallback.
- Updated `ingestion/api_ingestion/angel_smartapi/market_data_ingestor.py` to use IST-aware timestamps and skip off-hours LTP writes.
- Updated `scripts/validate_ingestion_run.py` to reflect the live OHLCV contract, the remediated IN10Y lineage, and legacy raw-artifact audit policy.
- Updated `docs/memory/06_data/data_contracts.md` and `docs/memory/04_architecture/data_flow.md` to match the canonical US OHLCV schema.
- Rebuilt US staging and analytics parquet artifacts from the newest retained raw file per symbol.
- Refreshed India proxy CSVs and IN10Y from live real-data sources.
- Refreshed `data/regime/raw/^TNX.csv` from live real-market data.

### New Validation Results

| Check | Result | Evidence |
| --- | --- | --- |
| `python scripts/validate_ingestion_run.py` | PASS | All report task rows now pass on current real artifacts. |
| `python relay.py --phase phase1 --epoch TE-2026-01-30` | PASS | Parity, proxy baseline, and immutable ingestion checks all passed. |

### Remaining Failures

None.

### Stabilization Check

- All critical Phase 1 tasks PASS.
- No schema drift is detected in the canonical US parquet contract.
- Data lineage is fully traceable for the active Phase 1 artifacts.
- Phase 1 is stabilized and ready for Phase 2 remediation.
