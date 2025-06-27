CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_cmvolt (
    "date" DATE,
    symbol TEXT,
    underlying_close_price_a NUMERIC(18,4),
    underlying_previous_day_close_price_b NUMERIC(18,4),
    underlying_log_returns_c_ln_a_b NUMERIC(18,4),
    previous_day_underlying_volatility_d NUMERIC(18,4),
    current_day_underlying_daily_volatility_e_sqrt_0_995_d_d_0_005_ NUMERIC(18,4),
    underlying_annualised_volatility_f_e_sqrt_365 NUMERIC(18,4)
);