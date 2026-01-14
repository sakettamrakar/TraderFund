"""Pipeline Controller - Core Logic"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from . import config
from .models import ActivationDecision, SymbolState

logger = logging.getLogger(__name__)

def get_score_bucket(score: float) -> str:
    """Classify score into bucket for crossing detection."""
    if score >= config.SCORE_BUCKETS["high"]:
        return "high"
    elif score >= config.SCORE_BUCKETS["medium"]:
        return "medium"
    elif score >= config.SCORE_BUCKETS["low"]:
        return "low"
    return "none"

def detect_bucket_crossing(prev_score: float, curr_score: float) -> Tuple[bool, str]:
    """Detect if score crossed a bucket boundary."""
    prev_bucket = get_score_bucket(prev_score)
    curr_bucket = get_score_bucket(curr_score)
    if prev_bucket != curr_bucket:
        return True, f"{prev_bucket}→{curr_bucket}"
    return False, ""

class PipelineController:
    """Orchestrates selective activation of pipeline stages."""

    def __init__(self):
        self.history_df = self._load_history()
        self.now = datetime.utcnow()

    def _load_history(self) -> pd.DataFrame:
        if config.EXECUTION_HISTORY_PATH.exists():
            return pd.read_parquet(config.EXECUTION_HISTORY_PATH)
        return pd.DataFrame()

    def _get_last_run(self, symbol: str, stage_id: int) -> Optional[datetime]:
        if self.history_df.empty:
            return None
        mask = (self.history_df['symbol'] == symbol) & (self.history_df['stage_id'] == stage_id)
        if not mask.any():
            return None
        latest = self.history_df[mask]['last_run'].max()
        return datetime.fromisoformat(latest)

    def _get_latest_data(self, symbol: str, stage_id: int) -> Dict[str, Any]:
        """Fetch latest score/state for a symbol/stage from historical results."""
        # This is a bit expensive, but accurate
        from research_modules.pipeline_controller import config as pc_config
        
        # Hardcoded paths based on project structure
        paths = {
            1: pc_config.DATA_ROOT / "structural" / "us",
            2: pc_config.DATA_ROOT / "energy" / "us",
            3: pc_config.DATA_ROOT / "participation" / "us",
            4: pc_config.DATA_ROOT / "momentum" / "us",
            5: pc_config.DATA_ROOT / "sustainability" / "us"
        }
        
        if stage_id not in paths:
            return {}

        stage_dir = paths[stage_id]
        if not stage_dir.exists():
            return {}

        # Look for most recent date folder
        dates = sorted([d.name for d in stage_dir.iterdir() if d.is_dir()], reverse=True)
        for d in dates:
            suffix = ("capability" if stage_id==1 else "energy" if stage_id==2 else "trigger" if stage_id==3 else "momentum" if stage_id==4 else "risk")
            p = stage_dir / d / f"{symbol}_{suffix}.parquet"
            if p.exists():
                df = pd.read_parquet(p)
                score_col = list(df.columns)[2] # Usually the score
                state_col = "risk_profile" if stage_id==5 else list(df.columns)[4] if stage_id >= 2 else "none"
                return {
                    "score": float(df[score_col].iloc[0]) if score_col in df.columns else 0.0,
                    "state": str(df[state_col].iloc[0]) if state_col in df.columns else "none"
                }
        return {}

    def decide(self, symbol: str) -> ActivationDecision:
        stages_to_run = []
        stages_skipped = {}
        triggering_conditions = []

        # STAGE 0: Universe Hygiene
        last_s0 = self._get_last_run(symbol, 0)
        if last_s0 is None or (self.now - last_s0).days >= config.STAG_0_INTERVAL:
            stages_to_run.append(0)
            triggering_conditions.append("S0: Interval reached or first run")
        else:
            stages_skipped[0] = config.SKIP_CODES["interval_not_reached"]

        # STAGE 1: Structural Capability
        last_s1 = self._get_last_run(symbol, 1)
        # S1 runs if history is loaded (Layer 2 requirement)
        from ingestion.historical_backfill.config import TRACKER_PATH
        history_ready = False
        if TRACKER_PATH.exists():
            bt = pd.read_parquet(TRACKER_PATH)
            if symbol in bt[bt['status'] == 'success']['symbol'].values:
                history_ready = True

        if history_ready:
            if last_s1 is None or (self.now - last_s1).days >= config.STAG_1_INTERVAL:
                stages_to_run.append(1)
                triggering_conditions.append("S1: History ready & interval reached")
            else:
                stages_skipped[1] = config.SKIP_CODES["interval_not_reached"]
        else:
            stages_skipped[1] = config.SKIP_CODES["history_not_backfilled"]

        # STAGE 2: Energy Setup
        s1_data = self._get_latest_data(symbol, 1)
        if s1_data.get("score", 0) >= config.S1_MIN_SCORE:
            stages_to_run.append(2)
            triggering_conditions.append(f"S2: S1 score {s1_data['score']:.1f} >= {config.S1_MIN_SCORE}")
        else:
            stages_skipped[2] = config.SKIP_CODES["s1_score_insufficient"]

        # STAGE 3: Participation Trigger
        s2_data = self._get_latest_data(symbol, 2)
        if s2_data.get("state") in config.S2_STATES:
            stages_to_run.append(3)
            triggering_conditions.append(f"S3: Energy state '{s2_data['state']}' in focus")
        else:
            stages_skipped[3] = config.SKIP_CODES["energy_state_none"]

        # STAGE 4: Momentum Confirmation
        s3_data = self._get_latest_data(symbol, 3)
        if s3_data.get("state") in config.S3_STATES:
            stages_to_run.append(4)
            triggering_conditions.append(f"S4: Participation '{s3_data['state']}' detected")
        else:
            stages_skipped[4] = config.SKIP_CODES["participation_not_emerging"]

        # STAGE 5: Sustainability & Risk
        s4_data = self._get_latest_data(symbol, 4)
        if s4_data.get("state") in config.S4_STATES:
            stages_to_run.append(5)
            triggering_conditions.append(f"S5: Momentum '{s4_data['state']}' requires risk profiling")
        else:
            stages_skipped[5] = config.SKIP_CODES["momentum_not_emerging"]

        return ActivationDecision(
            symbol=symbol,
            evaluation_date=self.now.date().isoformat(),
            stages_to_run=stages_to_run,
            stages_skipped=stages_skipped,
            triggering_conditions=triggering_conditions
        )
