import pandas as pd
import json
from pathlib import Path
from dataclasses import asdict
from strategy_sandbox.core.models import Strategy, PaperAction, PaperOutcome

class ParquetSandboxRepository:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.strat_dir = base_dir / "strategies"
        self.action_dir = base_dir / "actions"
        self.outcome_dir = base_dir / "outcomes"
        
        for d in [self.strat_dir, self.action_dir, self.outcome_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def save_strategy(self, s: Strategy):
        d = asdict(s)
        d['created_at'] = d['created_at'].isoformat()
        d['market_scope'] = d['market_scope'].value
        d['eligible_categories'] = json.dumps([c.value for c in s.eligible_categories])
        pd.DataFrame([d]).to_parquet(self.strat_dir / f"{s.strategy_id}.parquet", index=False)

    def save_action(self, a: PaperAction):
        d = asdict(a)
        d['timestamp'] = d['timestamp'].isoformat()
        d['action_type'] = d['action_type'].value
        d['supporting_signal_ids'] = json.dumps(d['supporting_signal_ids'])
        d['supporting_narrative_ids'] = json.dumps(d['supporting_narrative_ids'])
        d['reasoning_payload'] = json.dumps(d['reasoning_payload'])
        pd.DataFrame([d]).to_parquet(self.action_dir / f"{a.action_id}.parquet", index=False)

    def save_outcome(self, o: PaperOutcome):
        d = asdict(o)
        d['evaluated_at'] = d['evaluated_at'].isoformat()
        d['outcome_type'] = d['outcome_type'].value
        pd.DataFrame([d]).to_parquet(self.outcome_dir / f"{o.outcome_id}.parquet", index=False)
