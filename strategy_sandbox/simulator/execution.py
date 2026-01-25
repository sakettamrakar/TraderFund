import uuid
from datetime import datetime
from typing import Dict
from strategy_sandbox.core.models import PaperAction, PaperOutcome
from strategy_sandbox.core.enums import ActionType, OutcomeType

class PaperSimulator:
    """
    Applies paper actions to historical prices.
    """
    def __init__(self, slippage_pct: float = 0.001): # 0.1% default
        self.slippage = slippage_pct
        
    def simulate_outcome(self, action: PaperAction, 
                         entry_price: float, 
                         exit_price: float,
                         holding_hours: float) -> PaperOutcome:
        
        if action.action_type != ActionType.ENTER:
            raise ValueError("Can only simulate outcomes for ENTER actions.")
            
        # Apply Slippage (Pessimistic)
        adj_entry = entry_price * (1 + self.slippage) # Worse entry
        adj_exit = exit_price * (1 - self.slippage)   # Worse exit
        
        pnl = (adj_exit - adj_entry) / adj_entry * 100.0
        
        # Directional evaluation (Assumes BULLISH entry = expecting price UP)
        # Simplified: If exit > entry (before slippage) = correct
        directional = exit_price > entry_price
        
        # Outcome Type
        if pnl > 0.5:
            otype = OutcomeType.WIN
        elif pnl < -0.5:
            otype = OutcomeType.LOSS
        else:
            otype = OutcomeType.SCRATCH
            
        return PaperOutcome(
            outcome_id=str(uuid.uuid4()),
            action_id=action.action_id,
            entry_price=adj_entry,
            exit_price=adj_exit,
            pnl_pct=pnl,
            directional_correct=directional,
            holding_hours=holding_hours,
            outcome_type=otype,
            evaluated_at=datetime.utcnow()
        )
