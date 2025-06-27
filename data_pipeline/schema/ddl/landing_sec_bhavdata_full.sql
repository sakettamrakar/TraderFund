CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_sec_bhavdata_full (
    symbol TEXT,
    series TEXT,
    date1 DATE,
    prev_close NUMERIC(18,4),
    open_price NUMERIC(18,4),
    high_price NUMERIC(18,4),
    low_price NUMERIC(18,4),
    last_price NUMERIC(18,4),
    close_price NUMERIC(18,4),
    avg_price NUMERIC(18,4),
    ttl_trd_qnty NUMERIC(18,4),
    turnover_lacs NUMERIC(18,4),
    no_of_trades NUMERIC(18,4),
    deliv_qty NUMERIC(18,4),
    deliv_per NUMERIC(18,4)
);