from __future__ import annotations

import csv
import os
import sys
from getpass import getpass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from kiteconnect import KiteConnect

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.portfolio_intelligence.zerodha_browser_auth import login_url, obtain_access_token_via_browser


HOLDINGS_CSV = Path("zerodha_holdings.csv")
MF_HOLDINGS_CSV = Path("zerodha_mutual_funds.csv")


def load_env_credentials() -> tuple[str, str]:
    load_dotenv()
    api_key = os.getenv("KITE_API_KEY", "").strip()
    api_secret = os.getenv("KITE_API_SECRET", "").strip()
    return api_key, api_secret


def load_env_access_token() -> str:
    load_dotenv()
    return os.getenv("KITE_ACCESS_TOKEN", "").strip()


def prompt_non_empty(label: str, *, secret: bool = False) -> str:
    while True:
        value = getpass(f"{label}: ") if secret else input(f"{label}: ").strip()
        if value:
            return value
        print(f"{label} is required. Please try again.")


def extract_request_token(raw_input: str) -> str:
    raw_input = raw_input.strip()
    if not raw_input:
        raise ValueError("Empty request token input.")
    if "request_token=" not in raw_input:
        return raw_input

    parsed = urlparse(raw_input)
    values = parse_qs(parsed.query).get("request_token")
    if not values or not values[0]:
        raise ValueError("Could not extract request_token from the pasted URL.")
    return values[0]


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    rows = list(rows)
    if not rows:
        return 0
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def print_holdings(holdings: list[dict[str, Any]]) -> None:
    if not holdings:
        print("No equity holdings returned by Zerodha.")
        return

    print("\nEquity Holdings")
    print("-" * 100)
    print(f"{'tradingsymbol':18s} {'isin':15s} {'quantity':>10s} {'avg_price':>12s} {'last_price':>12s} {'pnl':>14s}")
    print("-" * 100)
    for item in holdings:
        tradingsymbol = str(item.get("tradingsymbol", ""))
        isin = str(item.get("isin", ""))
        quantity = float(item.get("quantity") or 0)
        average_price = float(item.get("average_price") or 0)
        last_price = float(item.get("last_price") or 0)
        pnl = float(item.get("pnl") or 0)
        print(
            f"{tradingsymbol[:18]:18s} {isin[:15]:15s} {quantity:10.2f} {average_price:12.2f} {last_price:12.2f} {pnl:14.2f}"
        )


def print_mutual_funds(mf_holdings: list[dict[str, Any]]) -> None:
    if not mf_holdings:
        print("\nNo mutual fund holdings returned by Zerodha.")
        return

    print("\nMutual Fund Holdings")
    print("-" * 100)
    print(f"{'tradingsymbol':18s} {'isin':15s} {'quantity':>10s} {'avg_price':>12s} {'last_price':>12s} {'pnl':>14s}")
    print("-" * 100)
    for item in mf_holdings:
        tradingsymbol = str(item.get("tradingsymbol") or item.get("fund") or item.get("name") or "")
        isin = str(item.get("isin", ""))
        quantity = float(item.get("quantity") or item.get("units") or 0)
        average_price = float(item.get("average_price") or item.get("average_nav") or 0)
        last_price = float(item.get("last_price") or item.get("last_nav") or item.get("nav") or 0)
        pnl = float(item.get("pnl") or item.get("profit_and_loss") or 0)
        print(
            f"{tradingsymbol[:18]:18s} {isin[:15]:15s} {quantity:10.2f} {average_price:12.2f} {last_price:12.2f} {pnl:14.2f}"
        )


def fetch_mutual_fund_holdings(kite: KiteConnect) -> list[dict[str, Any]]:
    if not hasattr(kite, "mf_holdings"):
        print("\nThis installed kiteconnect version does not expose mf_holdings(); skipping mutual fund fetch.")
        return []
    try:
        data = kite.mf_holdings()
        return data if isinstance(data, list) else []
    except Exception as exc:
        print(f"\nMutual fund holdings fetch skipped: {exc}")
        return []


def main() -> int:
    headless = "--headless" in sys.argv
    print("Zerodha Kite Connect Holdings Fetch")
    print("=" * 40)
    print("This script will:")
    print("1. Load API credentials from .env when available")
    print("2. Open Zerodha login in an automated browser")
    print("3. Wait for authentication and capture request_token automatically")
    print("4. Fetch equity holdings and save them to zerodha_holdings.csv")
    print("5. Attempt mutual fund holdings fetch and save them to zerodha_mutual_funds.csv if available")

    try:
        env_api_key, env_api_secret = load_env_credentials()
        api_key = env_api_key or prompt_non_empty("API_KEY")
        api_secret = env_api_secret or prompt_non_empty("API_SECRET", secret=True)

        if env_api_key and env_api_secret:
            print("Loaded KITE_API_KEY and KITE_API_SECRET from .env")
        elif env_api_key:
            print("Loaded KITE_API_KEY from .env")
        elif env_api_secret:
            print("Loaded KITE_API_SECRET from .env")

        kite = KiteConnect(api_key=api_key)
        access_token = load_env_access_token()
        if access_token:
            print("\nLoaded KITE_ACCESS_TOKEN from .env. Validating existing session...")
            try:
                kite.set_access_token(access_token)
                kite.profile()
                print("Existing access token is valid.")
            except Exception:
                print("Existing access token is invalid or expired. Starting browser auth flow...")
                access_token = obtain_access_token_via_browser(
                    api_key,
                    api_secret,
                    headless=headless,
                    timeout_seconds=300,
                    persist_env=True,
                )
        else:
            print("\nNo KITE_ACCESS_TOKEN found. Starting automated Zerodha auth flow...")
            print(f"Login URL: {login_url(api_key)}")
            access_token = obtain_access_token_via_browser(
                api_key,
                api_secret,
                headless=headless,
                timeout_seconds=300,
                persist_env=True,
            )
        print(f"Access Token: {access_token}")

        kite.set_access_token(access_token)

        print("\nFetching equity holdings...")
        holdings = kite.holdings()
        print_holdings(holdings)
        holdings_count = write_csv(HOLDINGS_CSV, holdings)
        print(f"\nSaved {holdings_count} equity holdings rows to {HOLDINGS_CSV.resolve()}")

        print("\nFetching mutual fund holdings...")
        mf_holdings = fetch_mutual_fund_holdings(kite)
        print_mutual_funds(mf_holdings)
        if mf_holdings:
            mf_count = write_csv(MF_HOLDINGS_CSV, mf_holdings)
            print(f"\nSaved {mf_count} mutual fund holdings rows to {MF_HOLDINGS_CSV.resolve()}")

        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as exc:
        print(f"\nError: {exc}")
        print("Authentication or holdings fetch failed. Check API credentials, request token, and Zerodha session state.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())