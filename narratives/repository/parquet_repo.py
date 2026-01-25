import pandas as pd
import uuid
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict
from narratives.core.models import Narrative
from narratives.core.enums import NarrativeState
from signals.core.enums import Market
from .base import NarrativeRepository

class ParquetNarrativeRepository(NarrativeRepository):
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def _get_path(self, market: Market, date_str: str) -> Path:
        return self.base_dir / market.value / date_str

    def save_narrative(self, narrative: Narrative) -> None:
        path = self._get_path(narrative.market, narrative.created_at.strftime('%Y-%m-%d'))
        path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{narrative.narrative_id}_v{narrative.version}_{uuid.uuid4().hex[:8]}.parquet"
        file_path = path / filename
        
        d = narrative.to_dict()
        # Serialize complex list/dicts for parquet
        d['related_assets'] = json.dumps(d['related_assets'])
        d['supporting_events'] = json.dumps(d['supporting_events'])
        d['explainability_payload'] = json.dumps(d['explainability_payload'])
        
        pd.DataFrame([d]).to_parquet(file_path, index=False)

    def get_narrative_history(self, narrative_id: str) -> List[Narrative]:
        files = list(self.base_dir.rglob("*.parquet"))
        results = []
        for f in files:
            try:
                df = pd.read_parquet(f)
                match = df[df['narrative_id'] == narrative_id]
                for _, row in match.iterrows():
                    d = row.to_dict()
                    # Deserialize
                    d['related_assets'] = json.loads(d['related_assets'])
                    d['supporting_events'] = json.loads(d['supporting_events'])
                    d['explainability_payload'] = json.loads(d['explainability_payload'])
                    results.append(Narrative.from_dict(d))
            except:
                continue
        results.sort(key=lambda x: x.version)
        return results

    def get_active_narratives(self, market: Market) -> List[Narrative]:
        market_dir = self.base_dir / market.value
        if not market_dir.exists():
            return []
            
        narrative_map: Dict[str, Narrative] = {}
        files = list(market_dir.rglob("*.parquet"))
        
        for f in files:
            try:
                df = pd.read_parquet(f)
                for _, row in df.iterrows():
                    d = row.to_dict()
                    d['related_assets'] = json.loads(d['related_assets'])
                    d['supporting_events'] = json.loads(d['supporting_events'])
                    d['explainability_payload'] = json.loads(d['explainability_payload'])
                    
                    n = Narrative.from_dict(d)
                    
                    if n.narrative_id not in narrative_map:
                        narrative_map[n.narrative_id] = n
                    else:
                        if n.version > narrative_map[n.narrative_id].version:
                            narrative_map[n.narrative_id] = n
            except:
                continue
                
        # Filter for non-terminal states
        active_states = {NarrativeState.BORN, NarrativeState.REINFORCED, NarrativeState.WEAKENED}
        return [n for n in narrative_map.values() if n.lifecycle_state in active_states]
