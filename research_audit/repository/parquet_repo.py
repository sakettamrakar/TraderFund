import pandas as pd
import json
from pathlib import Path
from research_audit.versioning.models import ReportDiff, ReportVersionMetadata

class ParquetAuditRepository:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.meta_dir = base_dir / "metadata"
        self.diff_dir = base_dir / "diffs"
        
        self.meta_dir.mkdir(parents=True, exist_ok=True)
        self.diff_dir.mkdir(parents=True, exist_ok=True)

    def save_metadata(self, meta: ReportVersionMetadata):
        file_path = self.meta_dir / f"{meta.report_id}_v{meta.version}.parquet"
        pd.DataFrame([meta.to_dict()]).to_parquet(file_path, index=False)

    def save_diff(self, diff: ReportDiff):
        file_path = self.diff_dir / f"{diff.diff_id}.parquet"
        d = dict(diff.__dict__) # dataclass to dict
        # Serialize lists/dicts
        d['added_narrative_ids'] = json.dumps(d['added_narrative_ids'])
        d['removed_narrative_ids'] = json.dumps(d['removed_narrative_ids'])
        d['confidence_deltas'] = json.dumps(d['confidence_deltas'])
        d['generated_at'] = d['generated_at'].isoformat()
        
        pd.DataFrame([d]).to_parquet(file_path, index=False)
