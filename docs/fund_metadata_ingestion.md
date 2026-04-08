# Fund Metadata Ingestion

## Objective
Replace blind category assumptions with metadata-backed fund enrichment inside the existing ingestion flow.

## Metadata fields now supported
- `fund_symbol`
- `security_type`
- `fund_family`
- `benchmark_reference`
- `benchmark_provider`
- `underlying_holdings`
- `lookthrough_mode`
- `lookthrough_status`
- `lookthrough_provenance`
- `metadata_source`

## Data resolution order
1. Broker payload metadata if already present
2. Local security master metadata from `data/input/daily/Equities/sec_list_*.csv`
3. Cached fund disclosure artifact from `data/portfolio_intelligence/fund_metadata`
4. Provider-backed ETF profile fetch via Alpha Vantage when configured
5. Cached benchmark composition artifact from `data/portfolio_intelligence/benchmark_metadata`
6. Honest stagnation state when real look-through is unavailable

## Output semantics
- `UNDERLYING_DISCLOSURE`: real underlying holdings available
- `BENCHMARK_COMPOSITION`: benchmark-backed look-through available
- `HEURISTIC_FALLBACK`: analytical continuity preserved with explicit fallback labeling
- `REAL_LOOKTHROUGH_UNAVAILABLE`: no real metadata path available

## Storage
Fund metadata is persisted in the existing portfolio intelligence base directory:
- `data/portfolio_intelligence/fund_metadata`
- `data/portfolio_intelligence/benchmark_metadata`
