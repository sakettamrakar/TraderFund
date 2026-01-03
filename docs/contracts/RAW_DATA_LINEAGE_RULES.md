# RAW_DATA_LINEAGE_RULES.md

## Overview
This document establishes the lineage and isolation rules for raw data within the TraderFund platform.

## Isolation Rules

### 1. Strategy Code Isolation
- **Rule**: Core strategy and backtesting modules (`src/core_modules/`, `src/pro_modules/`) MUST NOT read directly from `data/raw/`.
- **Reasoning**: Raw data format is unstable and may contain duplicates, gaps, or errors. Strategies must consume processed (cleaned, merged) data from the `data/processed/` layer.
- **Verification**: Periodic scans for hardcoded paths to `data/raw/` in strategy directories.

### 2. Ingestion Path Isolation
- **Rule**: API-based ingestion (`data/raw/api_based/`) and File-based ingestion (`data/raw/file_based/`) must remain in separate directory hierarchies.
- **Reasoning**: Maintains clear lineage of data source for auditability and debugging.
- **Merging**: Any merging of data from different sources must happen in the processing layer, never in the raw layer.

### 3. Immutability
- **Rule**: Once written to `data/raw/`, data is considered immutable.
- **Exceptions**: Append-only growth is allowed. Manual deletion/archival of old raw data is allowed for storage optimization, but modification of existing records is PROHIBITED.

## Data Lake Layers
- **Raw (Bronze)**: Direct output from ingestors. Native format (JSONL, CSV). Contains duplicates.
- **Processed (Silver)**: Cleaned, de-duplicated, and standardized format (Parquet, Database).
- **Features (Gold)**: Enriched data with indicators and signals ready for model consumption.
