from __future__ import annotations

import csv
import hashlib
import io
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from ..config import BrokerCredentialSet
from .base import (
    BrokerConnector,
    BrokerConnectorError,
    MissingBrokerCredentialsError,
)
from ..models import (
    BrokerAuthResult,
    InstrumentRecord,
    RawBrokerHolding,
    RawBrokerOrder,
    RawBrokerPosition,
)


class ZerodhaConnector(BrokerConnector):
    broker_name = "ZERODHA"
    market = "INDIA"
    provenance_source = "kite_connect_api"
    base_url = "https://api.kite.trade"
    login_base_url = "https://kite.zerodha.com/connect/login"

    def __init__(
        self,
        credentials: BrokerCredentialSet,
        request_timeout_seconds: int = 20,
        max_requests_per_second: float = 2.0,
    ) -> None:
        super().__init__(request_timeout_seconds=request_timeout_seconds, max_requests_per_second=max_requests_per_second)
        self.credentials = credentials
        self.access_token = credentials.access_token
        self._profile: Optional[Dict[str, Any]] = None

    def login_url(self) -> Optional[str]:
        if not self.credentials.api_key:
            return None
        return f"{self.login_base_url}?v=3&api_key={self.credentials.api_key}"

    def authenticate(self) -> BrokerAuthResult:
        missing = self.credentials.missing()
        if missing:
            return BrokerAuthResult(
                broker=self.broker_name,
                authenticated=False,
                message="Missing Zerodha credentials for read-only portfolio ingestion.",
                login_url=self.login_url(),
                missing_credentials=missing,
            )

        if not self.access_token and self.credentials.request_token:
            self.access_token = self._generate_access_token(
                api_key=self.credentials.api_key,
                api_secret=self.credentials.api_secret,
                request_token=self.credentials.request_token,
            )

        if not self.access_token:
            return BrokerAuthResult(
                broker=self.broker_name,
                authenticated=False,
                message="No access token available after authentication flow.",
                login_url=self.login_url(),
                missing_credentials=["KITE_ACCESS_TOKEN"],
            )

        profile = self._get_json("/user/profile")
        self._profile = profile
        account_name = profile.get("user_name") or profile.get("user_shortname")
        account_id = profile.get("user_id")
        expiry = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=0, minute=30, second=0, microsecond=0)
        return BrokerAuthResult(
            broker=self.broker_name,
            authenticated=True,
            message="Authenticated against Zerodha in read-only mode.",
            login_url=self.login_url(),
            missing_credentials=[],
            access_token_expiry=expiry.isoformat(),
            account_id=account_id,
            account_name=account_name,
        )

    def fetch_holdings(self) -> List[RawBrokerHolding]:
        payload = self._get_json("/portfolio/holdings")
        return [
            RawBrokerHolding(
                symbol=item.get("tradingsymbol", ""),
                exchange=item.get("exchange", "NSE"),
                quantity=float(item.get("quantity") or 0),
                average_price=float(item.get("average_price") or 0),
                last_price=float(item.get("last_price") or 0),
                pnl=float(item.get("pnl") or 0),
                product="CNC",
                instrument_token=item.get("instrument_token"),
                raw=item,
            )
            for item in payload
        ]

    def fetch_positions(self) -> List[RawBrokerPosition]:
        payload = self._get_json("/portfolio/positions")
        positions = payload.get("net", []) if isinstance(payload, dict) else []
        return [
            RawBrokerPosition(
                symbol=item.get("tradingsymbol", ""),
                exchange=item.get("exchange", "NSE"),
                quantity=float(item.get("quantity") or 0),
                average_price=float(item.get("average_price") or 0),
                last_price=float(item.get("last_price") or 0),
                pnl=float(item.get("pnl") or 0),
                product=item.get("product", ""),
                instrument_token=item.get("instrument_token"),
                overnight_quantity=float(item.get("overnight_quantity") or 0),
                intraday_quantity=float(item.get("day_quantity") or 0),
                raw=item,
            )
            for item in positions
        ]

    def fetch_orders(self) -> List[RawBrokerOrder]:
        payload = self._get_json("/orders")
        return [
            RawBrokerOrder(
                order_id=str(item.get("order_id", "")),
                symbol=item.get("tradingsymbol", ""),
                exchange=item.get("exchange", ""),
                transaction_type=item.get("transaction_type", ""),
                quantity=float(item.get("quantity") or 0),
                status=item.get("status", ""),
                product=item.get("product", ""),
                variety=item.get("variety", ""),
                order_timestamp=item.get("order_timestamp"),
                raw=item,
            )
            for item in payload
        ]

    def fetch_instruments(self) -> List[InstrumentRecord]:
        self._ensure_authenticated()
        self._throttle()
        response = self.session.get(
            f"{self.base_url}/instruments",
            headers=self._headers(),
            timeout=self.request_timeout_seconds,
        )
        response.raise_for_status()
        reader = csv.DictReader(io.StringIO(response.text))
        records: List[InstrumentRecord] = []
        for row in reader:
            records.append(
                InstrumentRecord(
                    symbol=row.get("tradingsymbol", ""),
                    exchange=row.get("exchange", ""),
                    instrument_token=int(row["instrument_token"]) if row.get("instrument_token") else None,
                    name=row.get("name", ""),
                    instrument_type=row.get("instrument_type", ""),
                    segment=row.get("segment", ""),
                    tick_size=float(row.get("tick_size") or 0),
                    lot_size=int(float(row.get("lot_size") or 0)),
                    raw=row,
                )
            )
        return records

    def _generate_access_token(self, api_key: str, api_secret: str, request_token: str) -> str:
        checksum = hashlib.sha256(f"{api_key}{request_token}{api_secret}".encode("utf-8")).hexdigest()
        self._throttle()
        response = self.session.post(
            f"{self.base_url}/session/token",
            headers={"X-Kite-Version": "3"},
            data={
                "api_key": api_key,
                "request_token": request_token,
                "checksum": checksum,
            },
            timeout=self.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", {})
        token = data.get("access_token", "")
        if not token:
            raise BrokerConnectorError("Zerodha session token exchange did not return an access token.")
        return token

    def _ensure_authenticated(self) -> None:
        if not self.access_token:
            result = self.authenticate()
            if not result.authenticated:
                raise MissingBrokerCredentialsError(result.message)

    def _headers(self) -> Dict[str, str]:
        self._ensure_authenticated()
        return {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.credentials.api_key}:{self.access_token}",
        }

    def _get_json(self, path: str) -> Any:
        self._throttle()
        response = self.session.get(
            f"{self.base_url}{path}",
            headers=self._headers(),
            timeout=self.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "success":
            raise BrokerConnectorError(f"Zerodha request failed for {path}: {payload}")
        return payload.get("data")
