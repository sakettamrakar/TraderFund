CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_block (
    "date" DATE,
    symbol TEXT,
    security_name TEXT,
    client_name TEXT,
    buy_sell TEXT,
    quantity_traded NUMERIC(18,4),
    trade_price_wght_avg_price NUMERIC(18,4)
);