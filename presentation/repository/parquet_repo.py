import pandas as pd
import uuid
import json
import logging
from pathlib import Path
from typing import Optional
from presentation.core.models import NarrativeSummary
from .base import SummaryRepository

class ParquetSummaryRepository(SummaryRepository):
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def _get_path(self, narrative_id: str) -> Path:
        # Partition by first 2 chars of ID to avoid huge folders
        return self.base_dir / narrative_id[:2]

    def save_summary(self, summary: NarrativeSummary) -> None:
        path = self._get_path(summary.narrative_id)
        path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{summary.narrative_id}_v{summary.version}_summary.parquet"
        file_path = path / filename
        
        d = summary.to_dict()
        # Serialize dicts
        d['model_metadata'] = json.dumps(d['model_metadata'])
        
        pd.DataFrame([d]).to_parquet(file_path, index=False)

    def get_summary_by_narrative(self, narrative_id: str) -> Optional[NarrativeSummary]:
        # Scan for latest
        path = self._get_path(narrative_id)
        if not path.exists():
             return None
             
        files = list(path.glob(f"{narrative_id}_*_summary.parquet"))
        if not files:
             return None
             
        # Load all versions and find latest
        candidates = []
        for f in files:
            try:
                df = pd.read_parquet(f)
                d = df.iloc[0].to_dict()
                d['model_metadata'] = json.loads(d['model_metadata'])
                candidates.append(NarrativeSummary.from_dict(d))
            except:
                continue
                
        if not candidates:
            return None
            
        candidates.sort(key=lambda s: s.version)
        return candidates[-1]
