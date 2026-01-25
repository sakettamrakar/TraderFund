import pandas as pd
import json
from pathlib import Path
from signal_meta_analytics.core.models import MetaInsight

class ParquetMetaRepository:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_insight(self, insight: MetaInsight) -> None:
        filename = f"{insight.market.value}_{insight.generated_at.strftime('%Y%m%d')}_insights.parquet"
        file_path = self.base_dir / filename
        
        d = insight.to_dict()
        d['metrics_payload'] = json.dumps(d['metrics_payload'])
        
        # Append mode? Parquet doesn't support easy append line-by-line.
        # Batch write logic usually preferred.
        # For this design: Read-Concat-Write or separate files per run.
        # We will use separate files per Insight ID to avoid concurrency issues for now, or group by run.
        # Simplified: Per-Run File? 
        # Actually, let's just write single row per file for simplicity in this agent environment (no lock needed).
        f_path = self.base_dir / f"{insight.insight_id}.parquet"
        pd.DataFrame([d]).to_parquet(f_path, index=False)
