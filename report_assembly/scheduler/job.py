import argparse
from datetime import datetime
from pathlib import Path
from signals.core.enums import Market
from narratives.repository.parquet_repo import ParquetNarrativeRepository
from presentation.repository.parquet_repo import ParquetSummaryRepository
from research_reports.repository.parquet_repo import ParquetReportRepository
from report_assembly.config.settings import AssemblyConfig
from report_assembly.engine.resolver import InputResolver
from report_assembly.engine.builder import ReportBuilder

def run_job(market_str: str, date_str: str = None):
    # Init Deps
    base_data = Path("data")
    n_repo = ParquetNarrativeRepository(base_data / "narratives")
    s_repo = ParquetSummaryRepository(base_data / "presentation/summaries")
    r_repo = ParquetReportRepository(base_data / "research_reports")
    
    config = AssemblyConfig.default()
    resolver = InputResolver(n_repo, config)
    builder = ReportBuilder(resolver, s_repo, r_repo, config)
    
    # Parse Args
    market = Market(market_str)
    if date_str:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        target_date = datetime.utcnow()
        
    print(f"Starting Report Assembly for {market.value} @ {target_date.date()}...")
    
    report = builder.build_daily_report(market, target_date)
    
    print(f"Report Generated: {report.report_id}")
    print(f"Summary: {report.confidence_overview}")
    print(f"Items: {report.signal_stats['total_items']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", type=str, default="US", help="US or INDIA")
    parser.add_argument("--date", type=str, help="YYYY-MM-DD")
    args = parser.parse_args()
    
    run_job(args.market, args.date)
