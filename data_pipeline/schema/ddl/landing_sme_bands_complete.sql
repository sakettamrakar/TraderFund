CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_sme_bands_complete (
    symbol TEXT,
    series TEXT,
    name TEXT,
    band NUMERIC(18,4),
    remarks TEXT
);