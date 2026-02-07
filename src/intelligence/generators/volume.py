"""
Volume Attention Generator.
Flags symbols showing unusual volume activity.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from intelligence.contracts import AttentionSignal

class VolumeAttention:
    def evaluate(self, symbol: str, market_data: Dict[str, Any], market: str) -> Optional[AttentionSignal]:
        # Parse safely
        vol_data = market_data.get("volume", {})
        current_vol = vol_data.get("current", 0.0)
        avg_vol = vol_data.get("avg_20d", 1.0)
        
        if avg_vol <= 0: return None
        
        # Heuristic: 3x Average Volume
        ratio = current_vol / avg_vol
        
        if ratio > 3.0:
            return AttentionSignal(
                symbol=symbol,
                signal_type="VOLUME_SPIKE",
                domain="VOLUME",
                metric_label="Rel Volume",
                metric_value=ratio,
                unit="x",
                baseline=f"vs 20d Avg ({avg_vol/1000:.0f}k)",
                reason=f"Volume is 3x 20-day average",
                explanation={
                    "what": f"Volume spike {ratio:.1f}x normal",
                    "why": "Indicates institutional participation",
                    "not": "Not a buy/sell signal"
                },
                timestamp=datetime.now().isoformat(),
                market=market
            )
        return None
