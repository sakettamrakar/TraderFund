CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_shortselling (
    security_name TEXT,
    symbol_name TEXT,
    trade_date DATE,
    quantity NUMERIC(18,4)
);