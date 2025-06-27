CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_sec_list (
    symbol TEXT,
    series TEXT,
    security_name TEXT,
    band NUMERIC(18,4),
    remarks TEXT
);