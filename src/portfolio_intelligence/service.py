from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from .analytics import analyze_portfolio
from .broker_mcp_connectors.kite_mcp import KiteMCPConnector
from .config import PortfolioIntelligenceConfig
from .connectors.base import BrokerConnector
from .connectors.zerodha import ZerodhaConnector
from .enrichment import enrich_portfolio
from .normalization import normalize_portfolio
from .storage import PortfolioArtifactStore


class PortfolioIntelligenceService:
    def __init__(
        self,
        config: PortfolioIntelligenceConfig | None = None,
        store: PortfolioArtifactStore | None = None,
    ) -> None:
        self.config = config or PortfolioIntelligenceConfig()
        self.store = store or PortfolioArtifactStore(self.config)

    def build_kite_mcp_connector(self) -> KiteMCPConnector:
        return KiteMCPConnector(
            server_url=self.config.kite_mcp_url,
            protocol_version=self.config.kite_mcp_protocol_version,
            request_timeout_seconds=self.config.request_timeout_seconds,
            max_requests_per_second=self.config.max_requests_per_second,
        )

    def build_zerodha_connector(self) -> ZerodhaConnector:
        return ZerodhaConnector(
            credentials=self.config.zerodha_credentials(),
            request_timeout_seconds=self.config.request_timeout_seconds,
            max_requests_per_second=self.config.max_requests_per_second,
        )

    def ingest_snapshot(
        self,
        *,
        connector: BrokerConnector,
        auth: Any,
        holdings: List[Any],
        positions: List[Any],
        orders: List[Any],
        instruments: List[Any],
        portfolio_id: str,
        account_name: str | None,
        market: str,
        imported_at: str | None = None,
        data_source: str | None = None,
        source_provenance: str | None = None,
        refresh_diagnostics: Dict[str, Any] | None = None,
        portfolio_summary: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        imported_at = imported_at or datetime.now(timezone.utc).isoformat()
        connector_mode = (data_source or getattr(connector, "connector_mode", "API")).upper()
        provenance_source = source_provenance or getattr(connector, "provenance_source", connector.broker_name.lower())
        diagnostics = _merge_refresh_diagnostics(refresh_diagnostics, imported_at, connector_mode)
        resolved_account_name = account_name or auth.account_name or auth.account_id or portfolio_id

        raw_snapshot = {
            "portfolio_id": portfolio_id,
            "broker": connector.broker_name,
            "market": market,
            "account_name": resolved_account_name,
            "imported_at": imported_at,
            "truth_epoch": self.config.truth_epoch,
            "data_mode": self.config.data_mode,
            "data_source": connector_mode,
            "source_provenance": provenance_source,
            "refresh_diagnostics": diagnostics,
            "portfolio_summary": portfolio_summary or {},
            "auth": asdict(auth),
            "holdings": [asdict(item) for item in holdings],
            "positions": [asdict(item) for item in positions],
            "orders": [asdict(item) for item in orders],
            "instrument_count": len(instruments),
            "trace": {
                "source": provenance_source,
                "connector": connector.__class__.__name__,
                "timestamp": imported_at,
                "truth_epoch": self.config.truth_epoch,
            },
        }
        self.store.write_raw_snapshot(market, portfolio_id, raw_snapshot)

        normalized = normalize_portfolio(
            holdings=holdings,
            positions=positions,
            instruments=instruments,
            portfolio_id=portfolio_id,
            broker=connector.broker_name,
            market=market,
            account_name=resolved_account_name,
            truth_epoch=self.config.truth_epoch,
            data_as_of=imported_at,
        )
        normalized["portfolio_data_source"] = connector_mode
        normalized["source_provenance"] = provenance_source
        normalized["refresh_diagnostics"] = diagnostics
        normalized["portfolio_refresh_timestamp"] = imported_at
        normalized["portfolio_summary"] = portfolio_summary or {}
        self.store.write_normalized(market, portfolio_id, normalized)

        enriched = enrich_portfolio(normalized, config=self.config)
        analytics = analyze_portfolio(enriched, usd_inr_rate=self.config.usd_inr_manual_rate)
        analytics["portfolio_data_source"] = connector_mode
        analytics["source_provenance"] = provenance_source
        analytics["refresh_diagnostics"] = diagnostics
        analytics["portfolio_refresh_timestamp"] = imported_at
        analytics["portfolio_summary"] = portfolio_summary or {}
        analytics["trace"]["data_source"] = connector_mode
        analytics["trace"]["source_provenance"] = provenance_source
        self.store.write_analytics(market, portfolio_id, analytics)
        self.store.update_registry(
            {
                "portfolio_id": portfolio_id,
                "broker": connector.broker_name,
                "market": market,
                "account_name": resolved_account_name,
                "portfolio_data_source": connector_mode,
                "last_updated": imported_at,
                "refresh_diagnostics": diagnostics,
            }
        )
        return analytics

    def refresh_from_connector(
        self,
        *,
        connector: BrokerConnector,
        portfolio_id: str,
        account_name: str | None = None,
        market: str,
        data_source: str | None = None,
        source_provenance: str | None = None,
        refresh_diagnostics: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        auth = connector.authenticate()
        if not auth.authenticated:
            raise RuntimeError(auth.message)

        imported_at = datetime.now(timezone.utc).isoformat()
        holdings = connector.fetch_holdings()
        positions = connector.fetch_positions()
        orders = connector.fetch_orders()
        instruments = connector.fetch_instruments()
        portfolio_summary = _best_effort_portfolio_summary(connector)
        return self.ingest_snapshot(
            connector=connector,
            auth=auth,
            holdings=holdings,
            positions=positions,
            orders=orders,
            instruments=instruments,
            portfolio_id=portfolio_id,
            account_name=account_name,
            market=market,
            imported_at=imported_at,
            data_source=data_source,
            source_provenance=source_provenance,
            refresh_diagnostics=refresh_diagnostics,
            portfolio_summary=portfolio_summary,
        )

    def refresh_zerodha_portfolio(
        self,
        *,
        portfolio_id: str,
        account_name: str | None = None,
        market: str = "INDIA",
    ) -> Dict[str, Any]:
        return PortfolioRefreshService(self).refresh_zerodha_portfolio(
            portfolio_id=portfolio_id,
            account_name=account_name,
            market=market,
        )

    def load_overview(self, market: str) -> Dict[str, Any]:
        payloads = self.store.list_market_analytics(market)
        if not payloads:
            return {
                "market": market,
                "portfolios": [],
                "aggregated": {
                    "total_value": 0.0,
                    "total_pnl": 0.0,
                    "total_positions": 0,
                    "resilience_score": 0.0,
                    "resilience_classification": "UNAVAILABLE",
                },
                "allocation_breakdown": {},
                "data_source_breakdown": {},
                "truth_epoch": self.config.truth_epoch,
                "data_as_of": None,
                "trace": {"source": f"data/portfolio_intelligence/analytics/{market}"},
            }

        portfolios = []
        sector_totals: Dict[str, float] = {}
        data_source_breakdown: Dict[str, int] = {}
        total_value = 0.0
        total_pnl = 0.0
        total_positions = 0
        resilience_total = 0.0
        latest_data_as_of = None
        for payload in payloads:
            data_source = payload.get("portfolio_data_source", "UNAVAILABLE")
            data_source_breakdown[data_source] = data_source_breakdown.get(data_source, 0) + 1
            portfolios.append(
                {
                    "portfolio_id": payload["portfolio_id"],
                    "display_name": payload["account_name"],
                    "broker": payload["broker"],
                    "market": payload["market"],
                    "portfolio_data_source": data_source,
                    "portfolio_refresh_timestamp": payload.get("portfolio_refresh_timestamp"),
                    "refresh_diagnostics": payload.get("refresh_diagnostics", _empty_refresh_diagnostics()),
                    **payload["overview"],
                    "resilience_score": payload["resilience"]["overall_score"],
                    "resilience_classification": payload["resilience"]["classification"],
                    "last_updated": payload["data_as_of"],
                }
            )
            total_value += payload["overview"]["total_value"]
            total_pnl += payload["overview"]["total_pnl"]
            total_positions += payload["overview"]["holding_count"]
            resilience_total += payload["resilience"]["overall_score"]
            latest_data_as_of = max(latest_data_as_of or payload["data_as_of"], payload["data_as_of"])
            for sector, weight in payload["diversification"]["sector_allocation"].items():
                sector_totals[sector] = sector_totals.get(sector, 0.0) + (
                    payload["overview"]["total_value"] * weight / 100.0
                )

        allocation_breakdown = (
            {sector: round((value / total_value) * 100.0, 4) for sector, value in sector_totals.items()}
            if total_value
            else {}
        )
        resilience_score = resilience_total / len(payloads)
        return {
            "market": market,
            "portfolios": portfolios,
            "aggregated": {
                "total_value": round(total_value, 2),
                "total_pnl": round(total_pnl, 2),
                "total_pnl_pct": round((total_pnl / max(total_value - total_pnl, 1.0)) * 100.0, 4) if total_value else 0.0,
                "total_positions": total_positions,
                "resilience_score": round(resilience_score, 4),
                "resilience_classification": _resilience_bucket(resilience_score),
            },
            "allocation_breakdown": allocation_breakdown,
            "data_source_breakdown": data_source_breakdown,
            "truth_epoch": self.config.truth_epoch,
            "data_as_of": latest_data_as_of,
            "trace": {"source": f"data/portfolio_intelligence/analytics/{market}"},
        }

    def load_portfolio(self, market: str, portfolio_id: str) -> Dict[str, Any]:
        payload = self.store.load_latest_analytics(market, portfolio_id)
        if payload:
            return payload
        return {
            "portfolio_id": portfolio_id,
            "market": market,
            "truth_epoch": self.config.truth_epoch,
            "data_as_of": None,
            "portfolio_data_source": "UNAVAILABLE",
            "portfolio_refresh_timestamp": None,
            "refresh_diagnostics": _empty_refresh_diagnostics(),
            "regime_gate_state": "BLOCKED",
            "overview": {"total_value": 0.0, "total_pnl": 0.0, "holding_count": 0},
            "holdings": [],
            "diversification": {"sector_allocation": {}, "geography_allocation": {}, "factor_distribution": {}},
            "risk": {},
            "performance": {"winners": [], "laggards": [], "top_contributors": [], "bottom_contributors": []},
            "insights": [],
            "resilience": {"overall_score": 0.0, "classification": "UNAVAILABLE", "components": {}},
            "trace": {"source": f"data/portfolio_intelligence/analytics/{market}/{portfolio_id}/latest.json"},
        }

    def load_combined(self) -> Dict[str, Any]:
        us = self.store.list_market_analytics("US")
        india = self.store.list_market_analytics("INDIA")
        us_value = sum(item["overview"]["total_value"] for item in us)
        india_value = sum(item["overview"]["total_value"] for item in india)
        combined_usd = us_value
        warning = None
        fx_source = "NATIVE_USD"
        if india_value:
            if self.config.usd_inr_manual_rate > 0:
                combined_usd += india_value / self.config.usd_inr_manual_rate
                fx_source = "PORTFOLIO_USDINR_RATE"
            else:
                warning = "USDINR rate unavailable; combined USD normalization is partial."
                fx_source = "UNAVAILABLE"
                combined_usd = None
        return {
            "us_portfolio_value": round(us_value, 2),
            "india_portfolio_value": round(india_value, 2),
            "combined_value_usd": round(combined_usd, 2) if combined_usd is not None else None,
            "us_weight_pct": round((us_value / (us_value + india_value)) * 100.0, 4) if (us_value + india_value) else 0.0,
            "india_weight_pct": round((india_value / (us_value + india_value)) * 100.0, 4) if (us_value + india_value) else 0.0,
            "fx_source": fx_source,
            "warning": warning,
            "truth_epoch": self.config.truth_epoch,
            "trace": {"source": "data/portfolio_intelligence/analytics"},
        }


class PortfolioRefreshService:
    def __init__(self, service: PortfolioIntelligenceService | None = None) -> None:
        self.service = service or PortfolioIntelligenceService()

    def probe_zerodha_sources(self) -> Dict[str, Any]:
        mcp_probe = self._probe_mcp()
        api_probe = self._probe_api(standby=bool(mcp_probe["can_ingest"]))
        diagnostics = self._compose_diagnostics(mcp_probe, api_probe)
        return {
            "candidate_data_source": diagnostics["data_source"],
            "broker_connectivity": diagnostics["broker_connectivity"],
            "mcp": diagnostics["mcp"],
            "api_fallback": diagnostics["api_fallback"],
            "mcp_auth": _auth_to_dict(mcp_probe["auth"]),
            "api_auth": _auth_to_dict(api_probe["auth"]),
        }

    def refresh_zerodha_portfolio(
        self,
        *,
        portfolio_id: str,
        account_name: str | None = None,
        market: str = "INDIA",
    ) -> Dict[str, Any]:
        mcp_probe = self._probe_mcp()
        api_probe = self._probe_api(standby=bool(mcp_probe["can_ingest"]))
        diagnostics = self._compose_diagnostics(mcp_probe, api_probe)

        if mcp_probe["can_ingest"]:
            diagnostics["data_source"] = "MCP"
            diagnostics["api_fallback"]["status"] = "API_FALLBACK_NOT_REQUIRED"
            diagnostics["portfolio_refresh_timestamp"] = mcp_probe["imported_at"]
            return self.service.ingest_snapshot(
                connector=mcp_probe["connector"],
                auth=mcp_probe["auth"],
                holdings=mcp_probe["holdings"],
                positions=mcp_probe["positions"],
                orders=mcp_probe["orders"],
                instruments=mcp_probe["instruments"],
                portfolio_id=portfolio_id,
                account_name=account_name,
                market=market,
                imported_at=mcp_probe["imported_at"],
                data_source="MCP",
                source_provenance="kite_mcp",
                refresh_diagnostics=diagnostics,
                portfolio_summary=mcp_probe["portfolio_summary"],
            )

        if api_probe["auth"].authenticated:
            diagnostics["data_source"] = "API"
            diagnostics["broker_connectivity"] = "READ_ONLY_OK"
            diagnostics["api_fallback"]["status"] = "API_FALLBACK_IN_USE"
            return self.service.refresh_from_connector(
                connector=api_probe["connector"],
                portfolio_id=portfolio_id,
                account_name=account_name,
                market=market,
                data_source="API",
                source_provenance="kite_connect_api",
                refresh_diagnostics=diagnostics,
            )

        raise RuntimeError(_build_refresh_failure(diagnostics, mcp_probe["auth"], api_probe["auth"]))

    def _probe_mcp(self) -> Dict[str, Any]:
        connector = self.service.build_kite_mcp_connector()
        imported_at = datetime.now(timezone.utc).isoformat()
        probe = {
            "connector": connector,
            "auth": None,
            "imported_at": imported_at,
            "can_ingest": False,
            "holdings": [],
            "positions": [],
            "orders": [],
            "instruments": [],
            "portfolio_summary": {},
            "connectivity_status": "MCP_CONNECTIVITY_ERROR",
            "authentication_status": "MCP_AUTH_ERROR",
            "portfolio_fetch_status": "MCP_PORTFOLIO_FETCH_ERROR",
            "schema_status": "MCP_SCHEMA_INVALID",
            "message": "",
            "login_url": None,
            "validation": {"data_complete": False, "positions_detected": False, "schema_valid": False},
        }
        try:
            connector.connect_to_mcp()
            probe["connectivity_status"] = "MCP_CONNECTIVITY_OK"
        except Exception as exc:
            probe["auth"] = connector.authenticate()
            probe["message"] = f"Kite MCP initialize failed: {exc}"
            return probe

        auth = connector.authenticate()
        probe["auth"] = auth
        probe["login_url"] = auth.login_url
        if not auth.authenticated:
            probe["authentication_status"] = (
                "MCP_AUTH_REQUIRED" if auth.login_url or auth.missing_credentials else "MCP_AUTH_ERROR"
            )
            probe["message"] = auth.message
            return probe

        probe["authentication_status"] = "MCP_AUTH_VALID"
        try:
            holdings = connector.fetch_holdings()
            positions = connector.fetch_positions()
            validation = _validate_mcp_snapshot(holdings, positions)
            probe["holdings"] = holdings
            probe["positions"] = positions
            probe["validation"] = validation
            probe["portfolio_fetch_status"] = "MCP_PORTFOLIO_FETCH_OK" if validation["data_complete"] else "MCP_PORTFOLIO_FETCH_ERROR"
            probe["schema_status"] = "MCP_SCHEMA_VALID" if validation["schema_valid"] else "MCP_SCHEMA_INVALID"
            if validation["data_complete"] and validation["positions_detected"] and validation["schema_valid"]:
                probe["orders"] = _best_effort_fetch(connector.fetch_orders)
                probe["instruments"] = _best_effort_fetch(connector.fetch_instruments)
                probe["portfolio_summary"] = _best_effort_portfolio_summary(connector)
                probe["can_ingest"] = True
            else:
                probe["message"] = _describe_mcp_validation_failure(validation)
        except Exception as exc:
            probe["message"] = f"Kite MCP fetch failed: {exc}"
        return probe

    def _probe_api(self, *, standby: bool) -> Dict[str, Any]:
        connector = self.service.build_zerodha_connector()
        auth = connector.authenticate()
        if auth.authenticated:
            status = "API_FALLBACK_STANDBY" if standby else "API_FALLBACK_READY"
            message = "Kite Connect API fallback is authenticated and ready."
        elif auth.missing_credentials:
            status = "API_FALLBACK_AUTH_REQUIRED"
            message = auth.message
        else:
            status = "API_FALLBACK_ERROR"
            message = auth.message
        return {"connector": connector, "auth": auth, "status": status, "message": message}

    def _compose_diagnostics(self, mcp_probe: Dict[str, Any], api_probe: Dict[str, Any]) -> Dict[str, Any]:
        if mcp_probe["can_ingest"]:
            broker_connectivity = "READ_ONLY_OK"
            data_source = "MCP"
        elif api_probe["auth"].authenticated:
            broker_connectivity = "READ_ONLY_DEGRADED"
            data_source = "API"
        elif mcp_probe["connectivity_status"] == "MCP_CONNECTIVITY_OK":
            broker_connectivity = "AUTH_REQUIRED"
            data_source = "NONE"
        else:
            broker_connectivity = "CONNECTIVITY_BLOCKED"
            data_source = "NONE"

        return {
            "broker_connectivity": broker_connectivity,
            "data_source": data_source,
            "portfolio_refresh_timestamp": mcp_probe["imported_at"] if mcp_probe["can_ingest"] else None,
            "mcp": {
                "server_url": self.service.config.kite_mcp_url,
                "connectivity_status": mcp_probe["connectivity_status"],
                "authentication_status": mcp_probe["authentication_status"],
                "portfolio_fetch_status": mcp_probe["portfolio_fetch_status"],
                "schema_status": mcp_probe["schema_status"],
                "validation": mcp_probe["validation"],
                "message": mcp_probe["message"],
                "login_url": mcp_probe["login_url"],
            },
            "api_fallback": {
                "status": api_probe["status"],
                "message": api_probe["message"],
            },
        }


class PortfolioTrackerService:
    def __init__(self, service: PortfolioIntelligenceService | None = None) -> None:
        self.service = service or PortfolioIntelligenceService()
        self._registrations: List[Dict[str, str]] = []

    def register_zerodha_portfolio(self, portfolio_id: str, account_name: str) -> None:
        self._registrations.append(
            {
                "broker": "ZERODHA",
                "market": "INDIA",
                "portfolio_id": portfolio_id,
                "account_name": account_name,
            }
        )

    def refresh_all(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for registration in self._registrations:
            if registration["broker"] == "ZERODHA":
                results.append(
                    self.service.refresh_zerodha_portfolio(
                        portfolio_id=registration["portfolio_id"],
                        account_name=registration["account_name"],
                        market=registration["market"],
                    )
                )
        return results


def _validate_mcp_snapshot(holdings: List[Any], positions: List[Any]) -> Dict[str, bool]:
    return {
        "data_complete": isinstance(holdings, list) and isinstance(positions, list),
        "positions_detected": isinstance(positions, list),
        "schema_valid": _rows_have_required_fields(holdings) and _rows_have_required_fields(positions),
    }


def _rows_have_required_fields(rows: List[Any]) -> bool:
    for row in rows:
        if not getattr(row, "symbol", ""):
            return False
        if getattr(row, "quantity", None) is None:
            return False
    return True


def _describe_mcp_validation_failure(validation: Dict[str, bool]) -> str:
    failed = [key for key, value in validation.items() if not value]
    return "MCP response failed validation: " + ", ".join(failed)


def _best_effort_fetch(fn: Any) -> List[Any]:
    try:
        return fn()
    except Exception:
        return []


def _best_effort_portfolio_summary(connector: BrokerConnector) -> Dict[str, Any]:
    try:
        summary = getattr(connector, "fetch_portfolio_summary", None)
        if callable(summary):
            payload = summary()
            if isinstance(payload, dict):
                return payload
    except Exception:
        return {}
    return {}


def _merge_refresh_diagnostics(refresh_diagnostics: Dict[str, Any] | None, imported_at: str, data_source: str) -> Dict[str, Any]:
    diagnostics = _empty_refresh_diagnostics()
    if refresh_diagnostics:
        diagnostics.update(refresh_diagnostics)
        if isinstance(refresh_diagnostics.get("mcp"), dict):
            diagnostics["mcp"].update(refresh_diagnostics["mcp"])
        if isinstance(refresh_diagnostics.get("api_fallback"), dict):
            diagnostics["api_fallback"].update(refresh_diagnostics["api_fallback"])
    diagnostics["data_source"] = data_source
    diagnostics["portfolio_refresh_timestamp"] = imported_at
    return diagnostics


def _empty_refresh_diagnostics() -> Dict[str, Any]:
    return {
        "broker_connectivity": "CONNECTIVITY_BLOCKED",
        "data_source": "UNAVAILABLE",
        "portfolio_refresh_timestamp": None,
        "mcp": {
            "server_url": None,
            "connectivity_status": "MCP_NOT_ATTEMPTED",
            "authentication_status": "MCP_NOT_ATTEMPTED",
            "portfolio_fetch_status": "MCP_NOT_ATTEMPTED",
            "schema_status": "MCP_NOT_ATTEMPTED",
            "validation": {
                "data_complete": False,
                "positions_detected": False,
                "schema_valid": False,
            },
            "message": "",
            "login_url": None,
        },
        "api_fallback": {
            "status": "API_FALLBACK_NOT_ATTEMPTED",
            "message": "",
        },
    }


def _auth_to_dict(auth: Any) -> Dict[str, Any]:
    if auth is None:
        return {
            "authenticated": False,
            "message": "NOT_ATTEMPTED",
            "missing_credentials": [],
            "account_id": None,
            "account_name": None,
            "login_url": None,
        }
    return {
        "authenticated": auth.authenticated,
        "message": auth.message,
        "missing_credentials": auth.missing_credentials,
        "account_id": auth.account_id,
        "account_name": auth.account_name,
        "login_url": auth.login_url,
    }


def _build_refresh_failure(diagnostics: Dict[str, Any], mcp_auth: Any, api_auth: Any) -> str:
    return (
        "Zerodha refresh failed after MCP-first routing. "
        f"MCP: {getattr(mcp_auth, 'message', 'UNAVAILABLE')}. "
        f"API fallback: {getattr(api_auth, 'message', 'UNAVAILABLE')}. "
        f"Diagnostics: broker_connectivity={diagnostics['broker_connectivity']}, "
        f"mcp_status={diagnostics['mcp']['portfolio_fetch_status']}, "
        f"api_fallback={diagnostics['api_fallback']['status']}."
    )


def _resilience_bucket(score: float) -> str:
    if score >= 0.75:
        return "ROBUST"
    if score >= 0.5:
        return "ADEQUATE"
    if score > 0:
        return "VULNERABLE"
    return "UNAVAILABLE"
