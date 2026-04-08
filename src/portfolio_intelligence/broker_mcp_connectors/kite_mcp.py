from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional

from ..connectors.base import BrokerConnectorError, MissingBrokerCredentialsError
from ..models import (
    BrokerAuthResult,
    InstrumentRecord,
    RawBrokerHolding,
    RawBrokerOrder,
    RawBrokerPosition,
)
from .base import MCPBrokerConnector


class KiteMCPConnector(MCPBrokerConnector):
    broker_name = "ZERODHA"
    market = "INDIA"
    provenance_source = "kite_mcp"

    def __init__(
        self,
        *,
        server_url: str,
        protocol_version: str,
        request_timeout_seconds: int = 20,
        max_requests_per_second: float = 2.0,
    ) -> None:
        super().__init__(
            request_timeout_seconds=request_timeout_seconds,
            max_requests_per_second=max_requests_per_second,
        )
        self.server_url = server_url
        self.protocol_version = protocol_version
        self.persistence_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            ".runtime",
            "mcp_sessions.json",
        )
        self.mcp_session_id = self._load_persisted_session()
        self.server_info: Dict[str, Any] = {}
        self._initialized = False
        self._profile: Dict[str, Any] | None = None
        self._cached_holdings: List[RawBrokerHolding] | None = None
        self._cached_positions: List[RawBrokerPosition] | None = None

    def connect_to_mcp(self) -> Dict[str, Any]:
        if self._initialized:
            return {
                "reachable": True,
                "session_id": self.mcp_session_id,
                "server_info": self.server_info,
                "url": self.server_url,
            }

        # Try to resume existing session
        if self.mcp_session_id:
            try:
                # Check if session is alive with a minimal call
                resp = self.session.post(
                    self.server_url,
                    headers={"mcp-session-id": self.mcp_session_id},
                    json={"jsonrpc": "2.0", "id": "ping", "method": "ping"},
                    timeout=5,
                )
                if resp.status_code == 200:
                    self._initialized = True
                    return {
                        "reachable": True,
                        "session_id": self.mcp_session_id,
                        "server_info": self.server_info,
                        "url": self.server_url,
                    }
            except Exception:
                pass

        self._throttle()
        response = self.session.post(
            self.server_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": self.protocol_version,
                    "capabilities": {},
                    "clientInfo": {"name": "TraderFund", "version": "0.1"},
                },
            },
            timeout=self.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if "result" not in payload:
            raise BrokerConnectorError(f"Kite MCP initialize failed: {payload}")
        self.mcp_session_id = response.headers.get("mcp-session-id", "")
        if self.mcp_session_id:
            self._save_persisted_session(self.mcp_session_id)
        self.server_info = payload["result"].get("serverInfo", {})
        self._initialized = True
        self._notify_initialized()
        return {
            "reachable": True,
            "session_id": self.mcp_session_id,
            "server_info": self.server_info,
            "url": self.server_url,
        }

    def authenticate(self) -> BrokerAuthResult:
        try:
            self.connect_to_mcp()
        except Exception as exc:
            return BrokerAuthResult(
                broker=self.broker_name,
                authenticated=False,
                message=f"Kite MCP server unreachable: {exc}",
                login_url=None,
                missing_credentials=[],
            )

        result = self._tool_call("get_profile", {})
        if result.get("isError"):
            message = self._tool_message(result) or "Kite MCP profile fetch failed."
            login_result = self._tool_call("login", {})
            login_text = self._tool_message(login_result)
            login_url = _extract_login_url(login_text or "")
            if "log in first" in message.lower():
                return BrokerAuthResult(
                    broker=self.broker_name,
                    authenticated=False,
                    message="Kite MCP login required for read-only portfolio ingestion.",
                    login_url=login_url,
                    missing_credentials=["KITE_MCP_INTERACTIVE_LOGIN"],
                )
            return BrokerAuthResult(
                broker=self.broker_name,
                authenticated=False,
                message=f"Kite MCP authentication failed: {message}",
                login_url=login_url,
                missing_credentials=[],
            )

        payload = self._tool_payload(result)
        if not isinstance(payload, dict):
            return BrokerAuthResult(
                broker=self.broker_name,
                authenticated=False,
                message="Kite MCP returned a non-structured profile payload.",
                login_url=None,
                missing_credentials=[],
            )
        if not any(payload.get(key) for key in ("user_id", "user_name", "user_shortname")):
            return BrokerAuthResult(
                broker=self.broker_name,
                authenticated=False,
                message="Kite MCP profile payload did not contain account identity fields.",
                login_url=None,
                missing_credentials=[],
            )

        self._profile = payload
        return BrokerAuthResult(
            broker=self.broker_name,
            authenticated=True,
            message="Authenticated against Kite MCP in read-only mode.",
            login_url=None,
            missing_credentials=[],
            account_id=str(payload.get("user_id") or ""),
            account_name=payload.get("user_name") or payload.get("user_shortname"),
        )

    def fetch_holdings(self) -> List[RawBrokerHolding]:
        self._ensure_authenticated()
        result = self._tool_call("get_holdings", {})
        rows = _extract_rows(self._tool_payload(result), preferred_keys=("data", "holdings", "items"))
        holdings = [_build_holding(item) for item in rows]
        self._cached_holdings = holdings
        return holdings

    def fetch_positions(self) -> List[RawBrokerPosition]:
        self._ensure_authenticated()
        result = self._tool_call("get_positions", {})
        payload = self._tool_payload(result)
        rows = _extract_rows(payload, preferred_keys=("net", "positions", "data", "items"))
        positions = [_build_position(item) for item in rows]
        self._cached_positions = positions
        return positions

    def fetch_orders(self) -> List[RawBrokerOrder]:
        self._ensure_authenticated()
        result = self._tool_call("get_orders", {})
        rows = _extract_rows(self._tool_payload(result), preferred_keys=("data", "orders", "items"))
        return [_build_order(item) for item in rows]

    def fetch_instruments(self) -> List[InstrumentRecord]:
        self._ensure_authenticated()
        instruments: List[InstrumentRecord] = []
        seen: set[tuple[str, str]] = set()
        for exchange, symbol in self._symbols_for_lookup():
            if (exchange, symbol) in seen:
                continue
            seen.add((exchange, symbol))
            try:
                result = self._tool_call(
                    "search_instruments",
                    {"query": symbol, "filter_on": "tradingsymbol", "limit": 8},
                )
            except Exception:
                continue
            matches = _extract_rows(self._tool_payload(result), preferred_keys=("data", "items", "results"))
            for item in matches:
                item_exchange = str(item.get("exchange") or "").upper()
                item_symbol = str(item.get("tradingsymbol") or item.get("symbol") or "").upper()
                if item_exchange == exchange and item_symbol == symbol:
                    instruments.append(
                        InstrumentRecord(
                            symbol=item_symbol,
                            exchange=item_exchange,
                            instrument_token=_safe_int(item.get("instrument_token")),
                            name=item.get("name", ""),
                            instrument_type=item.get("instrument_type", ""),
                            segment=item.get("segment", ""),
                            tick_size=_safe_float(item.get("tick_size")),
                            lot_size=_safe_int(item.get("lot_size")) or 0,
                            raw=item,
                        )
                    )
                    break
        return instruments

    def fetch_portfolio_summary(self) -> Dict[str, Any]:
        holdings = self._cached_holdings if self._cached_holdings is not None else self.fetch_holdings()
        positions = self._cached_positions if self._cached_positions is not None else self.fetch_positions()
        total_market_value = sum(item.quantity * item.last_price for item in holdings)
        total_positions = len(holdings) + len(positions)
        return {
            "holding_count": len(holdings),
            "position_count": len(positions),
            "total_market_value": round(total_market_value, 2),
            "session_id_present": bool(self.mcp_session_id),
        }

    def _ensure_authenticated(self) -> None:
        if self._profile is not None:
            return
        auth = self.authenticate()
        if not auth.authenticated:
            raise MissingBrokerCredentialsError(auth.message)

    def _notify_initialized(self) -> None:
        if not self.mcp_session_id:
            return
        try:
            self._throttle()
            self.session.post(
                self.server_url,
                headers={"mcp-session-id": self.mcp_session_id},
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                timeout=self.request_timeout_seconds,
            )
        except Exception:
            return

    def _tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        self.connect_to_mcp()
        self._throttle()
        response = self.session.post(
            self.server_url,
            headers={"mcp-session-id": self.mcp_session_id},
            json={
                "jsonrpc": "2.0",
                "id": name,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            },
            timeout=self.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            raise BrokerConnectorError(f"Kite MCP tool call failed for {name}: {payload['error']}")
        return payload.get("result", {})

    def _tool_payload(self, result: Dict[str, Any]) -> Any:
        if "structuredContent" in result:
            return result["structuredContent"]
        text = self._tool_message(result)
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"message": text}

    def _tool_message(self, result: Dict[str, Any]) -> str:
        fragments = [
            item.get("text", "")
            for item in result.get("content", [])
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return "\n".join(fragment for fragment in fragments if fragment).strip()

    def _symbols_for_lookup(self) -> Iterable[tuple[str, str]]:
        holdings = self._cached_holdings or []
        positions = self._cached_positions or []
        for item in holdings:
            yield (item.exchange.upper(), item.symbol.upper())
        for item in positions:
            yield (item.exchange.upper(), item.symbol.upper())

    def _load_persisted_session(self) -> str:
        if not os.path.exists(self.persistence_path):
            return ""
        try:
            with open(self.persistence_path, "r") as f:
                data = json.load(f)
                return data.get(self.server_url, "")
        except Exception:
            return ""

    def _save_persisted_session(self, session_id: str) -> None:
        data = {}
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r") as f:
                    data = json.load(f)
            except Exception:
                pass
        data[self.server_url] = session_id
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, "w") as f:
                json.dump(data, f)
        except Exception:
            pass


def _extract_login_url(text: str) -> Optional[str]:
    match = re.search(r"https://kite\.zerodha\.com/connect/login[^\s\)]+", text)
    return match.group(0) if match else None


def _extract_rows(payload: Any, *, preferred_keys: Iterable[str]) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []

    for key in preferred_keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _extract_rows(value, preferred_keys=preferred_keys)
            if nested:
                return nested

    for value in payload.values():
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return value
        if isinstance(value, dict):
            nested = _extract_rows(value, preferred_keys=preferred_keys)
            if nested:
                return nested
    return []


def _build_holding(item: Dict[str, Any]) -> RawBrokerHolding:
    quantity = _safe_float(item.get("quantity"))
    t1_quantity = _safe_float(item.get("t1_quantity"))
    return RawBrokerHolding(
        symbol=str(item.get("tradingsymbol") or item.get("symbol") or item.get("ticker") or "").upper(),
        exchange=str(item.get("exchange") or item.get("exchange_segment") or "NSE").upper(),
        quantity=quantity + t1_quantity,
        average_price=_safe_float(item.get("average_price") or item.get("price")),
        last_price=_safe_float(item.get("last_price") or item.get("close_price") or item.get("price")),
        pnl=_safe_float(item.get("pnl")),
        product=str(item.get("product") or "CNC"),
        instrument_token=_safe_int(item.get("instrument_token")),
        raw=item,
    )


def _build_position(item: Dict[str, Any]) -> RawBrokerPosition:
    return RawBrokerPosition(
        symbol=str(item.get("tradingsymbol") or item.get("symbol") or item.get("ticker") or "").upper(),
        exchange=str(item.get("exchange") or item.get("exchange_segment") or "NSE").upper(),
        quantity=_safe_float(item.get("quantity")),
        average_price=_safe_float(item.get("average_price") or item.get("price")),
        last_price=_safe_float(item.get("last_price") or item.get("close_price") or item.get("price")),
        pnl=_safe_float(item.get("pnl")),
        product=str(item.get("product") or ""),
        instrument_token=_safe_int(item.get("instrument_token")),
        overnight_quantity=_safe_float(item.get("overnight_quantity")),
        intraday_quantity=_safe_float(item.get("day_quantity") or item.get("intraday_quantity")),
        raw=item,
    )


def _build_order(item: Dict[str, Any]) -> RawBrokerOrder:
    return RawBrokerOrder(
        order_id=str(item.get("order_id") or item.get("id") or ""),
        symbol=str(item.get("tradingsymbol") or item.get("symbol") or "").upper(),
        exchange=str(item.get("exchange") or "").upper(),
        transaction_type=str(item.get("transaction_type") or ""),
        quantity=_safe_float(item.get("quantity")),
        status=str(item.get("status") or ""),
        product=str(item.get("product") or ""),
        variety=str(item.get("variety") or "regular"),
        order_timestamp=item.get("order_timestamp") or item.get("created_at"),
        raw=item,
    )


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None
