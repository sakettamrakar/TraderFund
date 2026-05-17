# Audit: India Delta Ingestion Refactor
**Audit ID**: AUD-CODE-2026-02-08-01
**Target**: India Market Ingestion (`india_data_acquisition.py`)
**Author**: Antigravity (Advanced Agentic Coding)

## 1. Intent
Refactor the India market ingestion pipeline from a **Full Overwrite** model to a **Delta-Merge** model to preserve data provenance and auditability.

## 2. Changes Implemented
1.  **Load Existing History**: The script now checks for an existing CSV file for each ticker.
2.  **Incremental Fetch**:
    - If history exists, it determines the last recorded date.
    - Fetches data starting from that date (inclusive) to capture updates/corrections to the last candle and any new candles.
    - If no history exists, it defaults to the full "2y" fetch.
3.  **Merge & Deduplicate**:
    - Existing and new data are concatenated.
    - Deduplication is performed on the `Date` column, keeping the `last` (newest) observation for overlapping dates.
    - Data is sorted by date.
4.  **Logging**: Added explicit console output for:
    - Pre-fetch row count.
    - Fetch start date.
    - Number of rows fetched.
    - Post-merge row count.
    - Delta (rows added).

## 3. Justification
This change aligns the India ingestion pipeline with the US `ingest_daily.py` logic, ensuring that:
-   **Historical Stability**: We don't blindly accept full-history re-statements from the provider unless they overlap with our fetch window.
-   **Efficiency**: We only process the necessary delta (though `yfinance` fetch might still grab a minimum chunk, we handle it logically).
-   **Audit Trail**: The logs now clearly show how much data was added/updated per run.

## 4. Risks & Mitigations
*   **Gap Risk**: If the script isn't run for >2 years (unlikely), the "incremental" fetch from `last_date` might be constrained by provider limits, but `yfinance` generally handles date ranges well.
*   **Schema Drift**: Yahoo Finance occasionally changes column names (e.g., 'Adj Close' vs 'Close'). The script includes column flattening and normalization to handle this.
*   **Duplicate Handling**: By keeping `last`, we accept the latest provider data for the overlap period (usually just the last day or two), which is desired for fixing EOD data quality issues.

## 5. Verification
Run the script twice.
-   Run 1: Should perform a delta update (or full load if first time).
-   Run 2 (Immediate): Should fetch 0-1 days of data, merge, and result in 0 rows added (idempotency).
