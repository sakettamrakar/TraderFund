CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_series_change (
    symbol TEXT,
    security TEXT,
    from_series TEXT,
    to_series TEXT,
    change_date DATE,
    remarks TEXT
);