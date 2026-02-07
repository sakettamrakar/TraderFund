"""
Price Attention Generator.
Flags symbols showing large gaps or range expansion.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from intelligence.contracts import AttentionSignal

class PriceBehavior:
    def evaluate(self, symbol: str, market_data: Dict[str, Any], market: str) -> Optional[AttentionSignal]:
        price_data = market_data.get("price", {})
        close = price_data.get("close", 0.0)
        prev_close = price_data.get("prev_close", 0.0)
        
        # STRICT VALIDATION: If data is missing or zero, DO NOT GENERATE SIGNAL.
        if close <= 0 or prev_close <= 0:
            return None
            
        change_pct = (close - prev_close) / prev_close
        
        # Threshold: 5% move
        if abs(change_pct) > 0.05:
            direction = "UP" if change_pct > 0 else "DOWN"
            return AttentionSignal(
                symbol=symbol,
                signal_type=f"LARGE_MOVE_{direction}",
                domain="PRICE",
                metric_label="Daily Change",
                metric_value=change_pct * 100, # Convert to readable %
                unit="%",
                baseline=f"vs Prev Close ({prev_close})",
                reason=f"Price moved {abs(change_pct):.1%} {direction}",
                explanation={
                    "what": f"Price changed by {abs(change_pct):.1%}",
                    "why": "Exceeded 5% daily move threshold",
                    "not": "Not a trend reversal prediction"
                },
                timestamp=datetime.now().isoformat(),
                market=market
            )
        return None
