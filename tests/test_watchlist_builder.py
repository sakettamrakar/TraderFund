import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import datetime
from core_modules.watchlist_management import build_watchlist, simulate_data_stream


def test_build_watchlist_filters_correctly():
    today = datetime.date.today()
    data = [
        {
            "symbol": "AAA",
            "market_cap": 15000,
            "price_history": [100, 102, 103, 104, 105, 108],
            "volume_history": [1, 1, 1, 1, 1, 1, 1, 1, 1, 3],
            "average_daily_value": 6,
            "ex_dividend_date": today + datetime.timedelta(days=5),
        },
        {
            "symbol": "BBB",
            "market_cap": 8000,  # below market cap threshold
            "price_history": [100, 97, 96, 95, 94, 93],
            "volume_history": [1] * 10,
            "average_daily_value": 6,
            "ex_dividend_date": today + datetime.timedelta(days=5),
        },
        {
            "symbol": "CCC",
            "market_cap": 12000,
            "price_history": [100, 100, 100, 100, 100, 100],  # no price change
            "volume_history": [1] * 9 + [5],
            "average_daily_value": 6,
            "ex_dividend_date": today + datetime.timedelta(days=5),
        },
        {
            "symbol": "DDD",
            "market_cap": 12000,
            "price_history": [100, 102, 103, 104, 105, 106],
            "volume_history": [1] * 9 + [3],
            "average_daily_value": 4,  # below ADV threshold
            "ex_dividend_date": today + datetime.timedelta(days=5),
        },
        {
            "symbol": "EEE",
            "market_cap": 15000,
            "price_history": [100, 102, 103, 104, 105, 108],
            "volume_history": [1] * 9 + [3],
            "average_daily_value": 6,
            "ex_dividend_date": today + datetime.timedelta(days=1),  # ex-div soon
        },
    ]
    stream = simulate_data_stream(data)
    result = build_watchlist(stream)
    assert result == ["AAA"]


def test_manual_overrides_always_include():
    today = datetime.date.today()
    data = [
        {
            "symbol": "ZZZ",
            "market_cap": 5000,
            "price_history": [100, 100, 100, 100, 100, 100],
            "volume_history": [1] * 10,
            "average_daily_value": 1,
            "ex_dividend_date": today + datetime.timedelta(days=1),
        }
    ]
    stream = simulate_data_stream(data)
    result = build_watchlist(stream, manual_overrides=["ZZZ"])
    assert result == ["ZZZ"]
