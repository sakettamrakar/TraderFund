import uuid
from datetime import datetime
from typing import List, Optional
from signals.core.models import Signal
from narratives.core.models import Narrative
from strategy_sandbox.core.models import Strategy, PaperAction
from strategy_sandbox.core.enums import ActionType

# GLOBAL SANDBOX FLAG
SANDBOX_ENABLED = True

class DecisionEngine:
    """
    Rule evaluator for paper trading.
    """
    
    def evaluate(self, strategy: Strategy, signals: List[Signal], 
                 narratives: List[Narrative]) -> Optional[PaperAction]:
        
        if not SANDBOX_ENABLED:
            raise RuntimeError("Sandbox is disabled. Cannot evaluate.")
            
        # 1. Filter eligible signals
        eligible = [
            s for s in signals 
            if s.signal_category in strategy.eligible_categories
            and (s.confidence_score or 0) >= strategy.min_confidence
        ]
        
        if not eligible:
            return None # No actionable signals
            
        # 2. Simple Entry Logic (Mockable)
        # "If any eligible signal is BULLISH/BEARISH, ENTER"
        # Real logic would parse `entry_rules` text.
        
        top_signal = max(eligible, key=lambda s: s.confidence_score or 0)
        
        # Narrative Check (Optional)
        supporting_narr = [n.narrative_id for n in narratives if n.confidence_score > 50]
        
        action = PaperAction(
            action_id=str(uuid.uuid4()),
            strategy_id=strategy.strategy_id,
            action_type=ActionType.ENTER,
            timestamp=datetime.utcnow(),
            asset_id=top_signal.asset_id,
            supporting_signal_ids=[top_signal.signal_id],
            supporting_narrative_ids=supporting_narr[:3], # Limit
            confidence_snapshot=top_signal.confidence_score or 0,
            reasoning_payload={
                "rule": "Top signal exceeded min_confidence threshold.",
                "signal_name": top_signal.signal_name,
                "direction": top_signal.direction.value
            }
        )
        
        return action
