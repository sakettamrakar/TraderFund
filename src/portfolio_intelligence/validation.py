from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .service import PortfolioIntelligenceService, PortfolioRefreshService


class PortfolioSystemValidator:
    def __init__(
        self,
        service: PortfolioIntelligenceService | None = None,
        refresh_service: PortfolioRefreshService | None = None,
    ) -> None:
        self.service = service or PortfolioIntelligenceService()
        self.refresh_service = refresh_service or PortfolioRefreshService(self.service)

    def run(self) -> Dict[str, Any]:
        config = self.service.config
        probe = self.refresh_service.probe_zerodha_sources()
        overview_india = self.service.load_overview("INDIA")

        connectivity_status = (
            "CONNECTIVITY_OK"
            if probe["mcp"]["connectivity_status"] == "MCP_CONNECTIVITY_OK" or probe["api_auth"]["authenticated"]
            else "CONNECTIVITY_ERROR"
        )
        ingestion_status = "INGESTION_OK" if self.service.store.load_registry().get("portfolios") else "INGESTION_ERROR"
        analytics_status = "ANALYTICS_OK" if overview_india.get("portfolios") else "ANALYTICS_ERROR"
        dashboard_status = "DASHBOARD_OK" if {"market", "portfolios", "aggregated"} <= set(overview_india.keys()) else "DASHBOARD_ERROR"

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "truth_epoch": config.truth_epoch,
            "execution_mode": config.execution_mode,
            "statuses": {
                "connectivity": connectivity_status,
                "ingestion": ingestion_status,
                "analytics": analytics_status,
                "dashboard": dashboard_status,
                "mcp_connectivity": probe["mcp"]["connectivity_status"],
                "mcp_portfolio_fetch": probe["mcp"]["portfolio_fetch_status"],
                "mcp_schema": probe["mcp"]["schema_status"],
                "api_fallback": probe["api_fallback"]["status"],
            },
            "details": {
                "credential_presence": config.credential_presence(),
                "mcp_probe": probe["mcp"],
                "mcp_auth": probe["mcp_auth"],
                "api_auth": probe["api_auth"],
                "portfolio_overview_india": overview_india,
                "combined_view": self.service.load_combined(),
            },
        }

    def to_markdown(self, report: Dict[str, Any]) -> str:
        statuses = report["statuses"]
        mcp_probe = report["details"]["mcp_probe"]
        mcp_auth = report["details"]["mcp_auth"]
        api_auth = report["details"]["api_auth"]
        lines = [
            "# Portfolio Intelligence System Validation Report",
            "",
            f"- Generated at: `{report['generated_at']}`",
            f"- Truth epoch: `{report['truth_epoch']}`",
            f"- Execution mode: `{report['execution_mode']}`",
            "",
            "## Core Status",
            "",
            f"- Connectivity: `{statuses['connectivity']}`",
            f"- Ingestion: `{statuses['ingestion']}`",
            f"- Analytics: `{statuses['analytics']}`",
            f"- Dashboard: `{statuses['dashboard']}`",
            "",
            "## MCP First Validation",
            "",
            f"- MCP connectivity: `{statuses['mcp_connectivity']}`",
            f"- MCP fetch: `{statuses['mcp_portfolio_fetch']}`",
            f"- MCP schema: `{statuses['mcp_schema']}`",
            f"- API fallback: `{statuses['api_fallback']}`",
            "",
            "## Broker Diagnostics",
            "",
            f"- MCP authentication: `{mcp_auth['authenticated']}`",
            f"- MCP auth message: {mcp_auth['message']}",
            f"- MCP login URL available: `{bool(mcp_auth['login_url'])}`",
            f"- MCP validation: `data_complete={mcp_probe['validation']['data_complete']}, positions_detected={mcp_probe['validation']['positions_detected']}, schema_valid={mcp_probe['validation']['schema_valid']}`",
            f"- API fallback authenticated: `{api_auth['authenticated']}`",
            f"- API fallback message: {api_auth['message']}",
            f"- API fallback missing credentials: `{', '.join(api_auth['missing_credentials']) if api_auth['missing_credentials'] else 'NONE'}`",
            "",
            "## Notes",
            "",
        ]
        if statuses["mcp_connectivity"] != "MCP_CONNECTIVITY_OK":
            lines.append("- Kite MCP server was not reachable from this environment, so MCP could not be used as the primary source.")
        elif not mcp_auth["authenticated"]:
            lines.append("- Kite MCP is reachable but requires interactive broker login before holdings and positions can be pulled.")
        elif statuses["mcp_portfolio_fetch"] != "MCP_PORTFOLIO_FETCH_OK":
            lines.append("- Kite MCP authenticated successfully but the portfolio fetch did not pass the current validation gate.")

        if api_auth["authenticated"]:
            lines.append("- Kite Connect API fallback is available if MCP is unavailable or invalid.")
        else:
            lines.append("- Kite Connect API fallback remains blocked until the remaining authentication material is supplied.")

        if statuses["analytics"] == "ANALYTICS_ERROR":
            lines.append("- No imported analytical artifacts were available at validation time, so dashboard metrics remain in an empty state.")

        return "\n".join(lines) + "\n"

    def write_markdown_report(self, path: Path) -> Dict[str, Any]:
        report = self.run()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(report), encoding="utf-8")
        return report
