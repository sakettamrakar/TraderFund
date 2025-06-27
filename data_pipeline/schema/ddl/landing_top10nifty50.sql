CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_top10nifty50 (
    symbol TEXT,
    security TEXT,
    weightage NUMERIC(18,4)
);