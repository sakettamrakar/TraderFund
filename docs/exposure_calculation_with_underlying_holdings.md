# Exposure Calculation With Underlying Holdings

## Calculation order
For each portfolio position:

1. Direct equity holding
- exposure uses direct holding weight

2. Fund or ETF holding with real underlying disclosures
- exposure uses weighted aggregation of underlying securities

3. Fund or ETF holding with benchmark composition cache
- exposure uses weighted aggregation of benchmark constituents

4. No real path available
- exposure remains explicitly marked as fallback or unavailable

## Exposure outputs impacted
- sector exposure
- industry exposure
- geography exposure
- factor exposure
- macro regime exposure
- hidden concentrations
- composite exposure metrics
- exposure insights

## Explainability
Each exposure insight now includes a trace block with:
- threshold
- observed metric
- source path

The exposure payload also includes `lookthrough_summary`, which reports:
- mutual fund input count
- synthetic look-through row count
- real disclosure fund count
- benchmark-linked fund count
- fallback fund count
- blocked fund count
