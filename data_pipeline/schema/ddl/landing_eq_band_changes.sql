CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_eq_band_changes (
    sr_no NUMERIC(18,4),
    symbol TEXT,
    series TEXT,
    security_name TEXT,
    "from" NUMERIC(18,4),
    "to" NUMERIC(18,4)
);