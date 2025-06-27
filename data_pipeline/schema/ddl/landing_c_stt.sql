CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_c_stt (
    symbol TEXT,
    series TEXT,
    description TEXT,
    isin TEXT
);