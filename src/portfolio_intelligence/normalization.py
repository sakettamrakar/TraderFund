from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List, Tuple

from .models import InstrumentRecord, RawBrokerHolding, RawBrokerPosition


INDIA_SECTOR_MAP: Dict[str, Tuple[str, str]] = {
    "RELIANCE": ("Energy", "Oil and Gas"),
    "TCS": ("Information Technology", "IT Services"),
    "INFY": ("Information Technology", "IT Services"),
    "HDFCBANK": ("Financials", "Banks"),
    "ICICIBANK": ("Financials", "Banks"),
    "SBIN": ("Financials", "Banks"),
    "BHARTIARTL": ("Communication Services", "Telecom"),
    "ITC": ("Consumer Staples", "Diversified Consumer"),
    "KOTAKBANK": ("Financials", "Banks"),
    "LT": ("Industrials", "Engineering"),
}

US_SECTOR_MAP: Dict[str, Tuple[str, str]] = {
    "AAPL": ("Information Technology", "Consumer Electronics"),
    "MSFT": ("Information Technology", "Software"),
    "GOOGL": ("Communication Services", "Interactive Media"),
    "AMZN": ("Consumer Discretionary", "Internet Retail"),
    "META": ("Communication Services", "Interactive Media"),
    "TSLA": ("Consumer Discretionary", "Automobiles"),
    "NVDA": ("Information Technology", "Semiconductors"),
    "IBM": ("Information Technology", "IT Services"),
}


def canonical_ticker(symbol: str, market: str) -> str:
    symbol = symbol.strip().upper()
    return f"{symbol}.NS" if market == "INDIA" and not symbol.endswith(".NS") else symbol


def _sector_for(symbol: str, market: str) -> Tuple[str, str]:
    mapping = INDIA_SECTOR_MAP if market == "INDIA" else US_SECTOR_MAP
    return mapping.get(symbol.upper(), ("UNKNOWN", "UNKNOWN"))


def _instrument_index(instruments: Iterable[InstrumentRecord]) -> Dict[tuple[str, str], InstrumentRecord]:
    return {(instrument.exchange.upper(), instrument.symbol.upper()): instrument for instrument in instruments}


def normalize_portfolio(
    *,
    holdings: List[RawBrokerHolding],
    positions: List[RawBrokerPosition],
    instruments: List[InstrumentRecord],
    portfolio_id: str,
    broker: str,
    market: str,
    account_name: str,
    truth_epoch: str,
    data_as_of: str,
) -> Dict[str, object]:
    instrument_map = _instrument_index(instruments)
    rows: List[Dict[str, object]] = []

    for holding in holdings:
        rows.append(
            _normalize_row(
                symbol=holding.symbol,
                exchange=holding.exchange,
                quantity=holding.quantity,
                average_price=holding.average_price,
                last_price=holding.last_price,
                pnl=holding.pnl,
                product=holding.product,
                portfolio_id=portfolio_id,
                broker=broker,
                market=market,
                account_name=account_name,
                truth_epoch=truth_epoch,
                data_as_of=data_as_of,
                asset_bucket="HOLDING",
                instrument=instrument_map.get((holding.exchange.upper(), holding.symbol.upper())),
                raw=holding.raw,
            )
        )

    for position in positions:
        rows.append(
            _normalize_row(
                symbol=position.symbol,
                exchange=position.exchange,
                quantity=position.quantity,
                average_price=position.average_price,
                last_price=position.last_price,
                pnl=position.pnl,
                product=position.product,
                portfolio_id=portfolio_id,
                broker=broker,
                market=market,
                account_name=account_name,
                truth_epoch=truth_epoch,
                data_as_of=data_as_of,
                asset_bucket="POSITION",
                instrument=instrument_map.get((position.exchange.upper(), position.symbol.upper())),
                raw=position.raw,
            )
        )

    total_market_value = sum(float(row["market_value"]) for row in rows) or 1.0
    for row in rows:
        row["weight_pct"] = round((float(row["market_value"]) / total_market_value) * 100.0, 4)

    return {
        "portfolio_id": portfolio_id,
        "broker": broker,
        "market": market,
        "account_name": account_name,
        "data_as_of": data_as_of,
        "truth_epoch": truth_epoch,
        "total_market_value": round(total_market_value, 2),
        "holding_count": len(rows),
        "holdings": rows,
    }


def _normalize_row(
    *,
    symbol: str,
    exchange: str,
    quantity: float,
    average_price: float,
    last_price: float,
    pnl: float,
    product: str,
    portfolio_id: str,
    broker: str,
    market: str,
    account_name: str,
    truth_epoch: str,
    data_as_of: str,
    asset_bucket: str,
    instrument: InstrumentRecord | None,
    raw: Dict[str, object],
) -> Dict[str, object]:
    market_price = float(last_price or average_price or 0.0)
    cost_basis = float(quantity or 0.0) * float(average_price or 0.0)
    market_value = float(quantity or 0.0) * market_price
    pnl_pct = (float(pnl or 0.0) / cost_basis * 100.0) if cost_basis else 0.0
    sector, industry = _sector_for(symbol, market)
    canonical = canonical_ticker(symbol, market)
    return {
        "portfolio_id": portfolio_id,
        "broker": broker,
        "account_name": account_name,
        "market": market,
        "asset_bucket": asset_bucket,
        "ticker": symbol.upper(),
        "canonical_ticker": canonical,
        "exchange": exchange.upper(),
        "quantity": float(quantity or 0.0),
        "cost_basis": round(cost_basis, 2),
        "market_price": round(market_price, 4),
        "market_value": round(market_value, 2),
        "pnl": round(float(pnl or 0.0), 2),
        "pnl_pct": round(pnl_pct, 4),
        "product": product,
        "sector": sector,
        "industry": industry,
        "geography": market,
        "currency": "INR" if market == "INDIA" else "USD",
        "instrument": asdict(instrument) if instrument else None,
        "factor_exposure": {},
        "truth_epoch": truth_epoch,
        "data_as_of": data_as_of,
        "trace": {
            "source": f"{broker.lower()}_api",
            "normalization": "portfolio_intelligence.normalization",
            "raw_fields": sorted(raw.keys()),
        },
    }
