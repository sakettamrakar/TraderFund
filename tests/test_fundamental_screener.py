import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from core_modules.screening.fundamental_screener import fundamental_screener


def test_fundamental_screener_basic():
    financial_data = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB", "CCC"],
            "sector": ["Tech", "Tech", "Health"],
            "trailing_pe": [10, 30, 8],
            "forward_ev_ebitda": [8, 12, 7],
            "roe": [20, 10, 16],
            "debt_to_equity": [0.4, 0.6, 0.3],
            "free_cash_flow_yield": [5, 2, 6],
            "earnings_revision_delta": [0.1, -0.2, 0.05],
            "operating_cash_flow_q1": [10, -5, 8],
            "operating_cash_flow_q2": [12, -3, 9],
            "insider_selling_pct": [1.5, 0.5, 0.2],
        }
    )

    sector_medians = pd.DataFrame(
        {
            "sector": ["Tech", "Health"],
            "median_trailing_pe": [20, 15],
            "median_forward_ev_ebitda": [10, 8],
        }
    )

    result = fundamental_screener(financial_data, sector_medians)
    assert list(result["ticker"]) == ["AAA", "CCC"]
    assert result.loc[result["ticker"] == "AAA", "high_insider_selling"].iloc[0]
    assert not result.loc[result["ticker"] == "CCC", "high_insider_selling"].iloc[0]

