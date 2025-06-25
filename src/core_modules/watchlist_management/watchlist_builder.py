from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, Iterable, Generator, List, Optional


def simulate_data_stream(data: Iterable[Dict]) -> Generator[Dict, None, None]:
    """Yield items from ``data`` simulating a real-time stream."""
    for item in data:
        yield item


def _price_change_percentage(prices: List[float]) -> float:
    """Return the percentage price change over the provided series."""
    if len(prices) < 2:
        return 0.0
    start = prices[0]
    end = prices[-1]
    if start == 0:
        return 0.0
    return (end - start) / start * 100


def _volume_spike_ratio(volumes: List[float]) -> float:
    """Return the ratio of the last day's volume to the average of the prior days."""
    if len(volumes) < 2:
        return 0.0
    *prior, last = volumes
    avg_prior = sum(prior) / len(prior)
    if avg_prior == 0:
        return 0.0
    return last / avg_prior


def build_watchlist(
    data_stream: Iterable[Dict],
    manual_overrides: Optional[Iterable[str]] = None,
    current_date: Optional[date] = None,
) -> List[str]:
    """Filter stocks from ``data_stream`` based on multiple criteria.

    Parameters
    ----------
    data_stream:
        Iterable of dictionaries representing stock data. Expected keys:
        ``symbol`` (str), ``market_cap`` (float in Cr), ``price_history`` (list
        of floats with at least 5 entries), ``volume_history`` (list of floats
        with at least 10 entries), ``average_daily_value`` (float in Cr), and
        ``ex_dividend_date`` (``datetime.date`` or ``datetime``).
    manual_overrides:
        Iterable of symbols that should always be included.
    current_date:
        Date used for ex-dividend filtering. Defaults to today.

    Returns
    -------
    List[str]
        Symbols that satisfy all filters or are manually overridden.
    """
    current_date = current_date or datetime.utcnow().date()
    overrides = set(manual_overrides or [])

    eligible = []
    for stock in data_stream:
        symbol = stock.get("symbol")
        if symbol in overrides:
            eligible.append(symbol)
            continue

        if stock.get("market_cap", 0) < 10000:
            continue

        if stock.get("average_daily_value", 0) < 5:
            continue

        ex_date = stock.get("ex_dividend_date")
        if ex_date is not None:
            ex_date = ex_date.date() if isinstance(ex_date, datetime) else ex_date
            days_to_ex = (ex_date - current_date).days
            if 0 <= days_to_ex <= 2:
                continue

        price_history = stock.get("price_history", [])[-6:]
        if _price_change_percentage(price_history) <= 3 and _price_change_percentage(price_history) >= -3:
            continue

        volume_history = stock.get("volume_history", [])[-10:]
        if _volume_spike_ratio(volume_history) <= 2:
            continue

        eligible.append(symbol)

    return eligible

