import pandas as pd
import json
from pathlib import Path
from signal_evolution.core.models import EvolutionProposal

class ParquetProposalRepository:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_proposal(self, proposal: EvolutionProposal) -> None:
        filename = f"{proposal.proposal_id}.parquet"
        file_path = self.base_dir / filename
        
        d = proposal.to_dict()
        # Flatten complex objects or serialize
        d['evidence_payload'] = json.dumps(d['evidence_payload'])
        # Advisory score is a dataclass, flatten it or dict it
        d['advisory_score'] = json.dumps(proposal.advisory_score.__dict__)
        
        pd.DataFrame([d]).to_parquet(file_path, index=False)
