import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import datetime
from core_modules.watchlist_management import build_watchlist


def _generate_dataset():
    today = datetime.date.today()
    data = []
    # 10 stocks that meet all filters
    for i in range(10):
        data.append({
            "symbol": f"PASS{i}",
            "sector_strength": 90,
            "market_cap": 12000,
            "price_history": [100, 102, 103, 104, 105, 108],
            "volume_history": [1] * 9 + [3],
            "average_daily_value": 6,
            "ex_dividend_date": today + datetime.timedelta(days=5),
        })
    # 90 stocks failing various filters
    for i in range(90):
        data.append({
            "symbol": f"FAIL{i}",
            "sector_strength": 40,
            "market_cap": 5000,
            "price_history": [100] * 6,
            "volume_history": [1] * 10,
            "average_daily_value": 4,
            "ex_dividend_date": today + datetime.timedelta(days=1),
        })
    return data


def test_build_watchlist_filters_correctly():
    data = _generate_dataset()
    result = build_watchlist(data)
    assert len(result) == 10
    assert set(result) == {f"PASS{i}" for i in range(10)}


def test_empty_input_returns_empty_list():
    assert build_watchlist([]) == []


def test_all_tickers_failing_logged(tmp_path):
    today = datetime.date.today()
    data = [
        {
            "symbol": "AAA",
            "sector_strength": 10,
            "market_cap": 5000,
            "price_history": [100] * 6,
            "volume_history": [1] * 10,
            "average_daily_value": 1,
            "ex_dividend_date": today + datetime.timedelta(days=1),
        },
        {
            "symbol": "BBB",
            "sector_strength": 20,
            "market_cap": 4000,
            "price_history": [100] * 6,
            "volume_history": [1] * 10,
            "average_daily_value": 2,
            "ex_dividend_date": today + datetime.timedelta(days=1),
        },
    ]
    log_path = tmp_path / "log.txt"
    result = build_watchlist(data, log_file=str(log_path))
    assert result == []
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == len(data)
    assert all(line.startswith(("AAA", "BBB")) for line in lines)


def test_manual_overrides_include_and_exclude():
    today = datetime.date.today()
    data = [
        {
            "symbol": "OVR",
            "sector_strength": 10,
            "market_cap": 5000,
            "price_history": [100] * 6,
            "volume_history": [1] * 10,
            "average_daily_value": 1,
            "ex_dividend_date": today + datetime.timedelta(days=1),
        }
    ]
    result = build_watchlist(data, include=["OVR"])
    assert result == ["OVR"]
    result = build_watchlist(data, exclude=["OVR"])
    assert result == []
