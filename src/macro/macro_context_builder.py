"""
Macro Context Builder (Read-Only).

Computes the high-level macro "weather" state based on available market data.
Strictly explanatory. No execution logic.

Version: 1.0
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class MacroContextBuilder:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_path = output_dir / "macro_context.json"

    def build(self, current_data: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
        """
        Builds the macro context snapshot.
        
        Args:
            current_data: Dictionary containing latest price/indicator data.
                          Expected keys: 'SPY', 'QQQ', 'VIX', '^TNX' (10Y), 
                          'SHY' (2Y proxy), 'HYG', 'LQD'.
            timestamp: ISO timestamp string.
        """
        
        # 1. Extract Proxies (with fallbacks for robustness)
        # Note: In a real system, we'd use rolling windows. 
        # Here we use structural proxies for the 'Explanation' layer.
        
        vix = current_data.get("VIX", {}).get("close", 20.0)
        ten_year = current_data.get("^TNX", {}).get("close", 4.0)
        
        # Mocking 2Y for curve calculation (since we might not have it ingested)
        # In prod, ingest 'SHY' or '^IRX'. 
        two_year = ten_year - 0.2 # Assume slightly inverted/flat by default if missing
        
        # 2. Compute States
        
        # --- Monetary ---
        curve_spread = ten_year - two_year
        if curve_spread < -0.1:
            curve_shape = "INVERTED"
        elif curve_spread < 0.2:
            curve_shape = "FLAT"
        else:
            curve_shape = "NORMAL"
            
        rate_level = "MID"
        if ten_year > 5.0: rate_level = "HIGH"
        elif ten_year < 2.0: rate_level = "LOW"
        
        monetary = {
            "policy_stance": "NEUTRAL", # Hard to infer from just price without history
            "rate_level": rate_level,
            "curve_shape": curve_shape,
            "real_rates": "POSITIVE" # Assumption for now
        }
        
        # --- Liquidity ---
        # Proxy: HYG vs LQD (Credit Spreads)
        hyg = current_data.get("HYG", {}).get("close", 75.0)
        lqd = current_data.get("LQD", {}).get("close", 105.0)
        
        # Simple ratio proxy
        # ratio = hyg / lqd. If ratio drops, spreads are widening (HYG underperforming)
        # We'd need history for trend. Retaining 'STABLE' default.
        
        liquidity = {
            "impulse": "STABLE",
            "credit_spreads": "NORMAL",
            "funding_stress": "LOW"
        }
        
        # --- Growth / Inflation ---
        growth = {
            "growth_trend": "STABLE",
            "inflation_regime": "STABLE",
            "policy_growth_alignment": "NEUTRAL"
        }
        
        # --- Risk ---
        vol_state = "NORMAL"
        if vix < 15: vol_state = "SUPPRESSED"
        elif vix > 25: vol_state = "ELEVATED"
        
        risk = {
            "appetite": "MIXED",
            "volatility": vol_state,
            "correlation": "NORMAL"
        }
        
        # 3. Generate Narrative
        narrative = self._generate_narrative(monetary, risk)
        
        # 4. Assemble Context
        context = {
            "timestamp": timestamp,
            "window_id": f"TICK-{timestamp}",
            "monetary": monetary,
            "liquidity": liquidity,
            "growth_inflation": growth,
            "risk": risk,
            "summary_narrative": narrative
        }
        
        # 5. Persist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(context, f, indent=2)
            
        return context

    def _generate_narrative(self, monetary: Dict, risk: Dict) -> str:
        parts = []
        
        # Rate/Curve narrative
        if monetary["curve_shape"] == "INVERTED":
            parts.append("Yield curve is inverted, suggesting late-cycle headwinds.")
        elif monetary["curve_shape"] == "STEEP":
            parts.append("Yield curve is steepening, often a sign of early recovery.")
        else:
            parts.append("Yield curve is relatively flat.")
            
        # Vol narrative
        if risk["volatility"] == "SUPPRESSED":
            parts.append("Volatility is suppressed, encouraging carry trades.")
        elif risk["volatility"] == "ELEVATED":
            parts.append("Risk appetite is fragile with elevated volatility.")
            
        return " ".join(parts)
