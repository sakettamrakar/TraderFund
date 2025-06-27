CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_c_stt_ind (
    symbol TEXT,
    series TEXT,
    isin TEXT,
    sec_desc TEXT,
    stt_indicator TEXT
);