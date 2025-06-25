"""Fundamental screening utilities."""

from __future__ import annotations

import pandas as pd


def fundamental_screener(
    financial_data: pd.DataFrame,
    sector_medians: pd.DataFrame,
    insider_selling_threshold: float = 1.0,
) -> pd.DataFrame:
    """Screen companies based on fundamental metrics.

    Parameters
    ----------
    financial_data : pd.DataFrame
        Table containing company fundamentals. Expected columns are::

            [
                'ticker', 'sector', 'trailing_pe', 'forward_ev_ebitda',
                'roe', 'debt_to_equity', 'free_cash_flow_yield',
                'earnings_revision_delta', 'operating_cash_flow_q1',
                'operating_cash_flow_q2', 'insider_selling_pct'
            ]

    sector_medians : pd.DataFrame
        Per-sector median metrics with columns ``['sector', 'median_trailing_pe',
        'median_forward_ev_ebitda']`` used for comparisons.

    insider_selling_threshold : float, optional
        Percentage ownership sold that will trigger a high insider selling flag.
        Defaults to ``1.0`` (1%).

    Returns
    -------
    pd.DataFrame
        Subset of ``financial_data`` that meets all screening criteria. The
        returned frame includes two boolean columns:
        ``negative_cash_flow`` and ``high_insider_selling``.
    """

    if financial_data.empty:
        return financial_data

    df = financial_data.merge(sector_medians, on="sector", how="left")

    conditions = (
        (df["trailing_pe"] < df["median_trailing_pe"]) &
        (df["forward_ev_ebitda"] < df["median_forward_ev_ebitda"]) &
        (df["roe"] > 15) &
        (df["debt_to_equity"] < 0.5)
    )

    # Exclude companies with negative operating cash flow in the last two quarters
    positive_cf = (df["operating_cash_flow_q1"] > 0) & (df["operating_cash_flow_q2"] > 0)
    df["negative_cash_flow"] = ~positive_cf

    df["high_insider_selling"] = df["insider_selling_pct"] > insider_selling_threshold

    filtered = df[conditions & positive_cf].copy()

    return filtered[
        [
            "ticker",
            "negative_cash_flow",
            "high_insider_selling",
        ]
    ]

