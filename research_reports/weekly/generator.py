from datetime import datetime, timedelta
from typing import List, Dict
from signals.core.enums import Market
from narratives.repository.base import NarrativeRepository
from presentation.repository.base import SummaryRepository
from research_reports.core.models import ResearchReport, ReportType
from research_reports.repository.parquet_repo import ParquetReportRepository

class WeeklyReportGenerator:
    def __init__(self, 
                 narrative_repo: NarrativeRepository,
                 summary_repo: SummaryRepository,
                 report_repo: ParquetReportRepository):
        self.narrative_repo = narrative_repo
        self.summary_repo = summary_repo
        self.report_repo = report_repo

    def generate(self, market: Market) -> ResearchReport:
        # 1. Define Window (Last 7 Days)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        # 2. Fetch Narratives
        # In a real implementation we would query for all narratives modified in the last 7 days.
        # Here we fetch all active + potentially resolved ones if we had that query.
        # We will just iterate active for this proof-of-concept.
        active_narratives = self.narrative_repo.get_active_narratives(market)
        
        summaries_list = []
        stats = {"total_narratives": len(active_narratives), "avg_conf": 0.0}
        
        total_conf = 0.0
        
        for n in active_narratives:
            s = self.summary_repo.get_summary_by_narrative(n.narrative_id)
            headline = s.headline if s else f"{n.title} (Auto-Title)"
            
            # For Weekly, we might want Key Points too
            summaries_list.append({
                "id": n.narrative_id,
                "headline": headline,
                "confidence": n.confidence_score,
                "lifecycle": n.lifecycle_state.value,
                "assets": n.related_assets
            })
            total_conf += n.confidence_score
            
        if active_narratives:
            stats["avg_conf"] = total_conf / len(active_narratives)
            
        # 3. Weekly Synthesis Tone
        if stats["avg_conf"] > 75:
            conf_text = "Strong Structural Trends Observed"
        elif stats["avg_conf"] > 50:
            conf_text = "Developing Context with Mixed signals"
        else:
            conf_text = "Weak Directionality - High Noise"

        # 4. Assemble Report
        report = ResearchReport.create(
            rtype=ReportType.WEEKLY_SYNTHESIS,
            market=market,
            start=start_time,
            end=end_time,
            narratives=summaries_list,
            stats=stats,
            conf_text=conf_text,
            explanation={"source": "Weekly Generator", "window_days": 7}
        )
        
        self.report_repo.save_report(report)
        return report
