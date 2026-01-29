"""
India Macro Context Builder (Read-Only).

Computes the high-level macro "weather" state for the India market.
Strictly explanatory. No execution logic.
Uses India-specific proxies as defined in DWBS_INDIA_RESEARCH_INSTANTIATION.

Version: 1.0
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class IndiaMacroContextBuilder:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_path = output_dir / "macro_context.json"

    def build(self, current_data: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
        """
        Builds the India macro context snapshot.

        Args:
            current_data: Dictionary containing latest price/indicator data.
                          Expected keys: 'NIFTY50', 'INDIA_VIX', 'INDIA_10Y',
                          'BANKNIFTY', 'USDINR'.
            timestamp: ISO timestamp string.
        """

        # 1. Extract Proxies (with fallbacks for robustness)

        # Volatility: INDIA VIX
        vix = current_data.get("INDIA_VIX", {}).get("close", 15.0)

        # Rates: India 10Y G-Sec
        # Defaulting to 7.0 if missing
        ten_year = current_data.get("INDIA_10Y", {}).get("close", 7.0)

        # Curve Proxy: India Yield Curve is generally upward sloping.
        # We might not have 2Y. Assume normal curve default.
        curve_shape = "NORMAL"

        # Rate Level Context (India rates are higher than US)
        rate_level = "MID"
        if ten_year > 8.0: rate_level = "HIGH"
        elif ten_year < 6.0: rate_level = "LOW"

        monetary = {
            "policy_stance": "NEUTRAL",
            "rate_level": rate_level,
            "curve_shape": curve_shape,
            "real_rates": "POSITIVE" # Inflation usually lower than 10Y
        }

        # --- Liquidity ---
        # Proxy: Banking Liquidity (Bank Nifty vs Nifty) or USDINR Stability
        # If USDINR is spiking, liquidity stress is higher.
        usdinr_vol = current_data.get("USDINR", {}).get("volatility", 0.0) # Placeholder

        liquidity_state = "STABLE"
        # Simple heuristic: If implied stress is high (mock check)

        liquidity = {
            "impulse": "STABLE",
            "credit_spreads": "NORMAL", # Data usually unavailable, assume normal
            "funding_stress": "LOW"
        }

        # --- Growth / Inflation ---
        growth = {
            "growth_trend": "STABLE", # India generally high growth
            "inflation_regime": "MODERATE",
            "policy_growth_alignment": "SUPPORTIVE"
        }

        # --- Risk ---
        vol_state = "NORMAL"
        if vix < 12: vol_state = "SUPPRESSED"
        elif vix > 20: vol_state = "ELEVATED"

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
            "window_id": f"TICK-IN-{timestamp}",
            "market": "INDIA",
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

        parts.append(f"India rates are {monetary['rate_level'].lower()} with a {monetary['curve_shape'].lower()} curve.")

        # Vol narrative
        if risk["volatility"] == "SUPPRESSED":
            parts.append("India VIX is suppressed, suggesting complacency.")
        elif risk["volatility"] == "ELEVATED":
            parts.append("India VIX is elevated, indicating caution.")

        return " ".join(parts)
