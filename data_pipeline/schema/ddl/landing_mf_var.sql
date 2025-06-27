CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_mf_var (
    isin TEXT,
    symbol TEXT,
    series TEXT,
    type TEXT,
    haircut NUMERIC(18,4),
    nav NUMERIC(18,4)
);