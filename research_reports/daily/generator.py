from datetime import datetime, timedelta
from typing import List, Dict
from signals.core.enums import Market
from narratives.repository.base import NarrativeRepository
from presentation.repository.base import SummaryRepository
from research_reports.core.models import ResearchReport, ReportType
from research_reports.repository.parquet_repo import ParquetReportRepository

class DailyReportGenerator:
    def __init__(self, 
                 narrative_repo: NarrativeRepository,
                 summary_repo: SummaryRepository,
                 report_repo: ParquetReportRepository):
        self.narrative_repo = narrative_repo
        self.summary_repo = summary_repo
        self.report_repo = report_repo

    def generate(self, market: Market) -> ResearchReport:
        # 1. Define Window (Last 24h logic simplified)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        # 2. Fetch Narratives
        # In a real app we'd filter by 'updated_at' >= start_time.
        # current get_active_narratives just returns all active.
        active_narratives = self.narrative_repo.get_active_narratives(market)
        
        summaries_list = []
        stats = {"total_narratives": len(active_narratives), "avg_conf": 0.0}
        
        total_conf = 0.0
        
        for n in active_narratives:
            # Fetch Presentation Summary
            s = self.summary_repo.get_summary_by_narrative(n.narrative_id)
            headline = s.headline if s else f"{n.title} (Auto-Title)"
            
            summaries_list.append({
                "id": n.narrative_id,
                "headline": headline,
                "confidence": n.confidence_score,
                "assets": n.related_assets
            })
            total_conf += n.confidence_score
            
        if active_narratives:
            stats["avg_conf"] = total_conf / len(active_narratives)
            
        # 3. Create Confidence/Uncertainty Statement
        if stats["avg_conf"] > 70:
            conf_text = "High Confidence Market Environment"
        elif stats["avg_conf"] > 40:
            conf_text = "Mixed Signals with Moderate Uncertainty"
        else:
            conf_text = "Low Confidence - High Noise Environment"

        # 4. Assemble Report
        report = ResearchReport.create(
            rtype=ReportType.DAILY_BRIEF,
            market=market,
            start=start_time,
            end=end_time,
            narratives=summaries_list,
            stats=stats,
            conf_text=conf_text,
            explanation={"source": "Automated Generator", "item_count": len(summaries_list)}
        )
        
        self.report_repo.save_report(report)
        return report
