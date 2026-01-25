from typing import List, Dict
from datetime import datetime
from narratives.core.models import Narrative
from research_reports.core.models import ResearchReport, ReportType
from signals.core.enums import Market
from presentation.repository.base import SummaryRepository
from research_reports.repository.parquet_repo import ParquetReportRepository
from report_assembly.engine.resolver import InputResolver
from report_assembly.config.settings import AssemblyConfig

class ReportBuilder:
    """
    Stateless assembler of Research Reports.
    """
    def __init__(self, 
                 resolver: InputResolver, 
                 summary_repo: SummaryRepository,
                 report_repo: ParquetReportRepository,
                 config: AssemblyConfig):
        self.resolver = resolver
        self.summary_repo = summary_repo
        self.report_repo = report_repo
        self.config = config

    def build_daily_report(self, market: Market, date: datetime) -> ResearchReport:
        # Window: 00:00 to 23:59 of that date
        start = datetime(date.year, date.month, date.day, 0, 0, 0)
        end = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        # 1. Resolve
        narratives = self.resolver.resolve_narratives(market, start, end)
        
        # 2. Summarize
        summaries_list = []
        total_conf = 0.0
        
        for n in narratives:
            s = self.summary_repo.get_summary_by_narrative(n.narrative_id)
            headline = s.headline if s else f"{n.title} (Auto-Title)"
            summaries_list.append({
                "id": n.narrative_id,
                "headline": headline,
                "confidence": n.confidence_score,
                "assets": n.related_assets
            })
            total_conf += n.confidence_score
            
        stats = {
            "total_items": len(narratives),
            "avg_conf": (total_conf / len(narratives)) if narratives else 0.0
        }
        
        # 3. Tone
        if stats["avg_conf"] > 70:
            tone = "High Confidence"
        elif stats["avg_conf"] > 40:
            tone = "Mixed / Moderate"
        else:
            tone = "Low Confidence / Noise"
            
        # 4. Create Object
        report = ResearchReport.create(
            rtype=ReportType.DAILY_BRIEF,
            market=market,
            start=start,
            end=end,
            narratives=summaries_list,
            stats=stats,
            conf_text=tone,
            explanation={
                "builder": "ReportAssemblyEngine", 
                "config": str(self.config),
                "resolved_count": len(narratives)
            }
        )
        
        # 5. Persist
        self.report_repo.save_report(report)
        return report
