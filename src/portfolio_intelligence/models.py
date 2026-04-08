from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


JsonDict = Dict[str, Any]


@dataclass(frozen=True)
class DataProvenance:
    source: str
    source_artifact: str
    data_as_of: str
    truth_epoch: str
    stale: bool = False
    notes: str = ""


@dataclass(frozen=True)
class BrokerAuthResult:
    broker: str
    authenticated: bool
    message: str
    login_url: Optional[str]
    missing_credentials: List[str]
    access_token_expiry: Optional[str] = None
    account_id: Optional[str] = None
    account_name: Optional[str] = None


@dataclass(frozen=True)
class RawBrokerHolding:
    symbol: str
    exchange: str
    quantity: float
    average_price: float
    last_price: float
    pnl: float
    product: str
    instrument_token: Optional[int]
    asset_bucket: str = "HOLDING"
    security_name: Optional[str] = None
    scheme_type: Optional[str] = None
    benchmark_reference: Optional[str] = None
    benchmark_provider: Optional[str] = None
    underlying_holdings: List[JsonDict] = field(default_factory=list)
    metadata_source: Optional[str] = None
    raw: JsonDict = field(default_factory=dict)


@dataclass(frozen=True)
class RawBrokerPosition:
    symbol: str
    exchange: str
    quantity: float
    average_price: float
    last_price: float
    pnl: float
    product: str
    instrument_token: Optional[int]
    overnight_quantity: float = 0.0
    intraday_quantity: float = 0.0
    raw: JsonDict = field(default_factory=dict)


@dataclass(frozen=True)
class RawBrokerOrder:
    order_id: str
    symbol: str
    exchange: str
    transaction_type: str
    quantity: float
    status: str
    product: str
    variety: str
    order_timestamp: Optional[str]
    raw: JsonDict = field(default_factory=dict)


@dataclass(frozen=True)
class InstrumentRecord:
    symbol: str
    exchange: str
    instrument_token: Optional[int]
    name: str
    instrument_type: str
    segment: str
    tick_size: float
    lot_size: int
    raw: JsonDict = field(default_factory=dict)
