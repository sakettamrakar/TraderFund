from datetime import datetime, timezone
import json
from src.portfolio_intelligence.service import PortfolioIntelligenceService
from src.portfolio_intelligence.validation import PortfolioSystemValidator
from src.portfolio_intelligence.service import PortfolioRefreshService
from pathlib import Path

def run():
    s = PortfolioIntelligenceService()
    c = s.build_kite_mcp_connector()
    c._initialized = True
    c.mcp_session_id = 'kitemcp-bd5aac59-b2e6-4d88-8fb9-8a76cb5a8356'
    
    auth = c.authenticate()
    if not auth.authenticated:
        print("Not authenticated")
        return
        
    print("Authenticated! Fetching portfolio via MCP...")
    analytics = s.ingest_snapshot(
        connector=c,
        auth=auth,
        holdings=c.fetch_holdings(),
        positions=c.fetch_positions(),
        orders=c.fetch_orders(),
        instruments=c.fetch_instruments(),
        portfolio_id="zerodha_primary",
        account_name="cw6760",
        market="INDIA",
        imported_at=datetime.now(timezone.utc).isoformat(),
        data_source="MCP",
        source_provenance="kite_mcp"
    )
    
    print(json.dumps({
        "status": "REFRESH_OK",
        "portfolio_id": analytics["portfolio_id"],
        "data_source": analytics.get("portfolio_data_source"),
    }, indent=2))

    validator = PortfolioSystemValidator(s, PortfolioRefreshService(s))
    report = validator.write_markdown_report(Path("docs") / "system_validation_report.md")
    print(json.dumps(report["statuses"], indent=2))

if __name__ == "__main__":
    run()
