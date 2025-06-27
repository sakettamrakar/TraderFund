CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_pe (
    symbol TEXT,
    symbol_p_e NUMERIC(18,4),
    adjusted_p_e NUMERIC(18,4)
);