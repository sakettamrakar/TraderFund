from __future__ import annotations

from datetime import date, datetime
from typing import Dict, Iterable, Generator, List, Optional

import argparse
import csv
import json

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def simulate_data_stream(data: Iterable[Dict]) -> Generator[Dict, None, None]:
    """Yield items from ``data`` simulating a real-time stream."""
    for item in data:
        yield item


def _price_change_percentage(prices: List[float]) -> float:
    """Return the percentage change from first to last price."""
    if len(prices) < 2 or prices[0] == 0:
        return 0.0
    return (prices[-1] - prices[0]) / prices[0] * 100


def _volume_spike_ratio(volumes: List[float]) -> float:
    """Return the ratio of last volume to the average of prior volumes."""
    if len(volumes) < 2:
        return 0.0
    *prior, last = volumes
    avg = sum(prior) / len(prior)
    if avg == 0:
        return 0.0
    return last / avg


# ---------------------------------------------------------------------------
# Core functionality
# ---------------------------------------------------------------------------

def build_watchlist(
    data_stream: Iterable[Dict],
    include: Optional[Iterable[str]] = None,
    exclude: Optional[Iterable[str]] = None,
    current_date: Optional[date] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    """Filter stocks from ``data_stream`` based on multiple criteria.

    Parameters
    ----------
    data_stream:
        Iterable of dictionaries representing stock data. Expected keys:
        ``symbol`` (str), ``sector_strength`` (float), ``market_cap`` (float in Cr),
        ``price_history`` (list of floats with at least 6 entries),
        ``volume_history`` (list of floats with at least 10 entries),
        ``average_daily_value`` (float in Cr), and ``ex_dividend_date``
        (``datetime.date`` or ``datetime``).
    include:
        Symbols that must be included regardless of filters.
    exclude:
        Symbols that must be excluded regardless of filters.
    current_date:
        Date used for ex-dividend filtering. Defaults to today.
    log_file:
        Optional path to log reasons for exclusion.

    Returns
    -------
    List[str]
        Symbols passing all filters and any manually included symbols.
    """
    records = list(data_stream)
    if not records:
        return []

    current_date = current_date or datetime.utcnow().date()
    include_set = set(include or [])
    exclude_set = set(exclude or [])

    strengths = [float(r.get("sector_strength", 0)) for r in records]
    threshold = float(np.percentile(strengths, 75)) if strengths else 0.0

    log_entries: List[str] = []
    eligible: List[str] = []
    for stock in records:
        symbol = stock.get("symbol")
        if not symbol:
            continue
        if symbol in exclude_set:
            log_entries.append(f"{symbol}: manually excluded")
            continue
        if symbol in include_set:
            eligible.append(symbol)
            continue

        if float(stock.get("sector_strength", 0)) <= threshold:
            log_entries.append(f"{symbol}: sector strength below 75th percentile")
            continue
        if float(stock.get("market_cap", 0)) <= 10000:
            log_entries.append(f"{symbol}: market cap below threshold")
            continue
        if float(stock.get("average_daily_value", 0)) < 5:
            log_entries.append(f"{symbol}: ADV below threshold")
            continue
        ex_date = stock.get("ex_dividend_date")
        if ex_date is not None:
            ex_date = ex_date.date() if isinstance(ex_date, datetime) else ex_date
            if 0 <= (ex_date - current_date).days <= 2:
                log_entries.append(f"{symbol}: ex-dividend within 2 days")
                continue
        price_history = stock.get("price_history", [])[-6:]
        change = _price_change_percentage(price_history)
        if abs(change) <= 3:
            log_entries.append(f"{symbol}: price change {change:.2f}% not strong")
            continue
        volume_history = stock.get("volume_history", [])[-10:]
        if _volume_spike_ratio(volume_history) <= 2:
            log_entries.append(f"{symbol}: volume spike not significant")
            continue
        eligible.append(symbol)

    if log_file:
        with open(log_file, "w", encoding="utf-8") as f:
            for entry in log_entries:
                f.write(entry + "\n")

    return eligible


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_stock_data(path: str) -> List[Dict]:
    """Load stock data from a JSON or CSV file."""
    with open(path, "r", encoding="utf-8") as f:
        if path.lower().endswith(".json"):
            return json.load(f)
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if "price_history" in row and isinstance(row["price_history"], str):
                row["price_history"] = json.loads(row["price_history"])
            if "volume_history" in row and isinstance(row["volume_history"], str):
                row["volume_history"] = json.loads(row["volume_history"])
            if row.get("ex_dividend_date"):
                row["ex_dividend_date"] = datetime.fromisoformat(row["ex_dividend_date"]).date()
            rows.append(row)
        return rows

def load_override_list(path: str) -> List[str]:
    """Load a list of symbols from a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Build stock watchlist")
    parser.add_argument("--data", required=True, help="Path to stock data JSON/CSV")
    parser.add_argument("--include", help="File with tickers to include")
    parser.add_argument("--exclude", help="File with tickers to exclude")
    parser.add_argument("--output", help="Where to write resulting watchlist JSON")
    parser.add_argument("--log", help="Optional log file for exclusions")
    args = parser.parse_args(argv)

    data = load_stock_data(args.data)
    include = load_override_list(args.include) if args.include else None
    exclude = load_override_list(args.exclude) if args.exclude else None

    watchlist = build_watchlist(data, include, exclude, log_file=args.log)
    output = json.dumps(watchlist)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI()


class WatchlistRequest(BaseModel):
    stocks: List[Dict]
    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None


@app.post("/build_watchlist")
def build_watchlist_endpoint(req: WatchlistRequest) -> Dict[str, List[str]]:
    tickers = build_watchlist(req.stocks, req.include, req.exclude)
    return {"tickers": tickers}


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
