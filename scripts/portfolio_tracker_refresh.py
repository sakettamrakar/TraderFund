from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.portfolio_intelligence.service import PortfolioIntelligenceService, PortfolioRefreshService
from src.portfolio_intelligence.validation import PortfolioSystemValidator


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh read-only portfolio intelligence artifacts.")
    parser.add_argument("--broker", default="zerodha")
    parser.add_argument("--market", default="INDIA")
    parser.add_argument("--portfolio-id", default="zerodha_primary")
    parser.add_argument("--account-name", default="Zerodha Primary")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    service = PortfolioIntelligenceService()
    refresh_service = PortfolioRefreshService(service)

    if not args.validate_only:
        if args.broker.lower() != "zerodha":
            raise SystemExit("Only Zerodha is currently implemented for live read-only refresh.")
        analytics = refresh_service.refresh_zerodha_portfolio(
            portfolio_id=args.portfolio_id,
            account_name=args.account_name,
            market=args.market,
        )
        print(
            json.dumps(
                {
                    "status": "REFRESH_OK",
                    "portfolio_id": analytics["portfolio_id"],
                    "data_source": analytics.get("portfolio_data_source"),
                },
                indent=2,
            )
        )

    validator = PortfolioSystemValidator(service, refresh_service)
    report = validator.write_markdown_report(Path("docs") / "system_validation_report.md")
    print(json.dumps(report["statuses"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
