import pandas as pd
import uuid
import json
from pathlib import Path
from typing import List
from research_reports.core.models import ResearchReport
from signals.core.enums import Market

class ParquetReportRepository:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def save_report(self, report: ResearchReport) -> None:
        path = self.base_dir / report.market_scope.value / report.generated_at.strftime('%Y')
        path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{report.report_id}_{report.generated_at.strftime('%Y%m%d')}.parquet"
        file_path = path / filename
        
        d = report.to_dict()
        # Serialize Complex Dicts
        d['included_narrative_ids'] = json.dumps(d['included_narrative_ids'])
        d['narrative_summaries'] = json.dumps(d['narrative_summaries'])
        d['signal_stats'] = json.dumps(d['signal_stats'])
        d['explainability_payload'] = json.dumps(d['explainability_payload'])
        
        pd.DataFrame([d]).to_parquet(file_path, index=False)
