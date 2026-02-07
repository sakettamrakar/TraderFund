"""
Volatility Attention Generator.
Flags symbols showing unusual volatility expansion.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from intelligence.contracts import AttentionSignal

class VolatilityAttention:
    def evaluate(self, symbol: str, market_data: Dict[str, Any], market: str) -> Optional[AttentionSignal]:
        # Parse safely
        vol_data = market_data.get("volatility", {})
        current_vol = vol_data.get("current", 0.0)
        avg_vol = vol_data.get("avg_20d", 1.0)
        
        if avg_vol <= 0: return None
        
        # Heuristic: Vol 2x Average
        ratio = current_vol / avg_vol
        
        if ratio > 2.0:
            return AttentionSignal(
                symbol=symbol,
                signal_type="VOLATILITY_EXPANSION",
                domain="VOLATILITY",
                metric_label="Rel Volatility",
                metric_value=ratio,
                unit="x",
                baseline=f"vs 20d Avg ({avg_vol:.2f})",
                reason=f"Current volatility ({current_vol:.2f}) is > 2x average ({avg_vol:.2f})",
                explanation={
                    "what": f"Volatility is {ratio:.1f}x normal levels",
                    "why": "Expansion marks potential regime shift",
                    "not": "Not a direction signal"
                },
                timestamp=datetime.now().isoformat(),
                market=market
            )
        return None
