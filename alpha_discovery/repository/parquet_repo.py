import pandas as pd
import uuid
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict
from alpha_discovery.core.models import AlphaHypothesis
from alpha_discovery.core.enums import ValidationState
from .base import AlphaRepository

class ParquetAlphaRepository(AlphaRepository):
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def _get_path(self, date_str: str) -> Path:
        return self.base_dir / date_str

    def save_alpha(self, alpha: AlphaHypothesis) -> None:
        path = self._get_path(alpha.created_at.strftime('%Y-%m-%d'))
        path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{alpha.alpha_id}_v{alpha.version}_{uuid.uuid4().hex[:8]}.parquet"
        file_path = path / filename
        
        d = alpha.to_dict()
        # Serialize lists/dicts
        d['related_assets'] = json.dumps(d['related_assets'])
        d['supporting_signals'] = json.dumps(d['supporting_signals'])
        d['supporting_narratives'] = json.dumps(d['supporting_narratives'])
        d['evidence_payload'] = json.dumps(d['evidence_payload'])
        
        pd.DataFrame([d]).to_parquet(file_path, index=False)

    def get_alpha_history(self, alpha_id: str) -> List[AlphaHypothesis]:
        files = list(self.base_dir.rglob("*.parquet"))
        results = []
        for f in files:
            try:
                df = pd.read_parquet(f)
                match = df[df['alpha_id'] == alpha_id]
                for _, row in match.iterrows():
                    d = row.to_dict()
                    d['related_assets'] = json.loads(d['related_assets'])
                    d['supporting_signals'] = json.loads(d['supporting_signals'])
                    d['supporting_narratives'] = json.loads(d['supporting_narratives'])
                    d['evidence_payload'] = json.loads(d['evidence_payload'])
                    results.append(AlphaHypothesis.from_dict(d))
            except:
                continue
        results.sort(key=lambda x: x.version)
        return results

    def get_active_alphas(self) -> List[AlphaHypothesis]:
        alpha_map: Dict[str, AlphaHypothesis] = {}
        files = list(self.base_dir.rglob("*.parquet"))
        
        for f in files:
            try:
                df = pd.read_parquet(f)
                for _, row in df.iterrows():
                    d = row.to_dict()
                    d['related_assets'] = json.loads(d['related_assets'])
                    d['supporting_signals'] = json.loads(d['supporting_signals'])
                    d['supporting_narratives'] = json.loads(d['supporting_narratives'])
                    d['evidence_payload'] = json.loads(d['evidence_payload'])
                    
                    a = AlphaHypothesis.from_dict(d)
                    
                    if a.alpha_id not in alpha_map:
                        alpha_map[a.alpha_id] = a
                    else:
                        if a.version > alpha_map[a.alpha_id].version:
                            alpha_map[a.alpha_id] = a
            except:
                continue
        
        terminal_states = {ValidationState.INVALIDATED, ValidationState.DECAYED}
        return [a for a in alpha_map.values() if a.validation_state not in terminal_states]
