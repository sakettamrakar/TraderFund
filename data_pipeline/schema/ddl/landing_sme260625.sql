CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_sme260625 (
    market TEXT,
    series TEXT,
    symbol TEXT,
    security TEXT,
    prev_cl_pr NUMERIC(18,4),
    open_price NUMERIC(18,4),
    high_price NUMERIC(18,4),
    low_price NUMERIC(18,4),
    close_price NUMERIC(18,4),
    net_trdval NUMERIC(18,4),
    net_trdqty NUMERIC(18,4),
    corp_ind TEXT,
    hi_52_wk NUMERIC(18,4),
    lo_52_wk NUMERIC(18,4)
);