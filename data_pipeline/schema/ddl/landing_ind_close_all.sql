CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_ind_close_all (
    index_name TEXT,
    index_date DATE,
    open_index_value NUMERIC(18,4),
    high_index_value NUMERIC(18,4),
    low_index_value NUMERIC(18,4),
    closing_index_value NUMERIC(18,4),
    points_change NUMERIC(18,4),
    change NUMERIC(18,4),
    volume NUMERIC(18,4),
    turnover_rs_cr NUMERIC(18,4),
    p_e NUMERIC(18,4),
    p_b NUMERIC(18,4),
    div_yield NUMERIC(18,4)
);