from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, List

from requests import Session

from ..models import (
    BrokerAuthResult,
    InstrumentRecord,
    RawBrokerHolding,
    RawBrokerOrder,
    RawBrokerPosition,
)


class BrokerConnectorError(RuntimeError):
    pass


class MissingBrokerCredentialsError(BrokerConnectorError):
    pass


class BrokerConnector(ABC):
    broker_name: str
    market: str
    connector_mode = "API"
    provenance_source = "broker_api"

    def __init__(self, request_timeout_seconds: int = 20, max_requests_per_second: float = 2.0) -> None:
        self.request_timeout_seconds = request_timeout_seconds
        self.max_requests_per_second = max_requests_per_second
        self.session = Session()
        self._last_request_at = 0.0

    def _throttle(self) -> None:
        if self.max_requests_per_second <= 0:
            return
        min_gap = 1.0 / self.max_requests_per_second
        now = time.monotonic()
        wait = min_gap - (now - self._last_request_at)
        if wait > 0:
            time.sleep(wait)
        self._last_request_at = time.monotonic()

    @abstractmethod
    def authenticate(self) -> BrokerAuthResult:
        raise NotImplementedError

    @abstractmethod
    def fetch_holdings(self) -> List[RawBrokerHolding]:
        raise NotImplementedError

    @abstractmethod
    def fetch_positions(self) -> List[RawBrokerPosition]:
        raise NotImplementedError

    @abstractmethod
    def fetch_orders(self) -> List[RawBrokerOrder]:
        raise NotImplementedError

    @abstractmethod
    def fetch_instruments(self) -> List[InstrumentRecord]:
        raise NotImplementedError

    def fetch_mutual_fund_holdings(self) -> List[Any]:
        return []
