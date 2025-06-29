CREATE SCHEMA IF NOT EXISTS nse_raw;
CREATE TABLE IF NOT EXISTS nse_raw.landing_reg_ind260625 (
    scripcode NUMERIC(18,4),
    symbol TEXT,
    nse_exclusive TEXT,
    status TEXT,
    series TEXT,
    gsm NUMERIC(18,4),
    long_term_additional_surveillance_measure_long_term_asm NUMERIC(18,4),
    unsolicited_sms NUMERIC(18,4),
    insolvency_resolution_process_irp NUMERIC(18,4),
    short_term_additional_surveillance_measure_short_term_asm NUMERIC(18,4),
    "default" NUMERIC(18,4),
    ica NUMERIC(18,4),
    filler4 NUMERIC(18,4),
    filler5 NUMERIC(18,4),
    pledge NUMERIC(18,4),
    add_on_pb NUMERIC(18,4),
    total_pledge NUMERIC(18,4),
    social_media_platforms NUMERIC(18,4),
    esm NUMERIC(18,4),
    loss_making NUMERIC(18,4),
    the_overall_encumbered_share_in_the_scrip_is_more_than_50_perce NUMERIC(18,4),
    under_bz_sz_series NUMERIC(18,4),
    company_has_failed_to_pay_annual_listing_fee NUMERIC(18,4),
    filler12 NUMERIC(18,4),
    derivative_contracts_in_the_scrip_to_be_moved_out_of_f_and_o NUMERIC(18,4),
    filler13 NUMERIC(18,4),
    filler14 NUMERIC(18,4),
    filler15 NUMERIC(18,4),
    filler16 NUMERIC(18,4)
);