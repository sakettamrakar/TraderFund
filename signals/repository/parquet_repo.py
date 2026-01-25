import pandas as pd
import uuid
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from signals.core.models import Signal
from signals.core.enums import Market, SignalState
from .base import SignalRepository

logger = logging.getLogger(__name__)

class ParquetSignalRepository(SignalRepository):
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def _get_partition_path(self, market: Market, date: datetime) -> Path:
        date_str = date.strftime('%Y-%m-%d')
        return self.base_dir / market.value / date_str

    def save_signal(self, signal: Signal) -> None:
        """Writes signal as a single-row parquet file."""
        path = self._get_partition_path(signal.market, signal.created_at)
        path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{signal.signal_id}_v{signal.version}_{uuid.uuid4().hex[:8]}.parquet"
        file_path = path / filename
        
        data = signal.to_dict()
        # Serialize dict/complex types to JSON string for Parquet compatibility
        if isinstance(data.get('explainability_payload'), dict):
            data['explainability_payload'] = json.dumps(data['explainability_payload'])
            
        df = pd.DataFrame([data])
        df.to_parquet(file_path, index=False)

    def get_signal_history(self, signal_id: str) -> List[Signal]:
        """Scans all parquet files to rebuild history for a signal ID."""
        all_signals = []
        files = list(self.base_dir.rglob("*.parquet"))
        
        for f in files:
            try:
                df = pd.read_parquet(f)
                matched = df[df['signal_id'] == signal_id]
                
                if not matched.empty:
                    for _, row in matched.iterrows():
                        row_dict = row.to_dict()
                        # Deserialize payload
                        if isinstance(row_dict.get('explainability_payload'), str):
                            row_dict['explainability_payload'] = json.loads(row_dict['explainability_payload'])
                        
                        all_signals.append(Signal.from_dict(row_dict))
            except Exception:
                continue
                
        all_signals.sort(key=lambda s: s.version)
        return all_signals

    def get_latest_signal(self, signal_id: str) -> Optional[Signal]:
        history = self.get_signal_history(signal_id)
        return history[-1] if history else None

    def get_active_signals(self, market: Market) -> List[Signal]:
        """Retrieves latest version of all signals that are currently ACTIVE."""
        market_dir = self.base_dir / market.value
        if not market_dir.exists():
            return []
            
        signal_map: Dict[str, Signal] = {}
        
        # Optimization: Scan recursively
        files = list(market_dir.rglob("*.parquet"))
        
        for f in files:
            try:
                df = pd.read_parquet(f)
                for _, row in df.iterrows():
                    row_dict = row.to_dict()
                    # Deserialize
                    if isinstance(row_dict.get('explainability_payload'), str):
                        row_dict['explainability_payload'] = json.loads(row_dict['explainability_payload'])
                        
                    sig = Signal.from_dict(row_dict)
                    
                    # Keep latest version
                    if sig.signal_id not in signal_map:
                        signal_map[sig.signal_id] = sig
                    else:
                        if sig.version > signal_map[sig.signal_id].version:
                            signal_map[sig.signal_id] = sig
            except Exception:
                continue
        
        return [s for s in signal_map.values() if s.lifecycle_state == SignalState.ACTIVE]
