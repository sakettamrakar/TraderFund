"""
Factor Context Builder (EV-RUN-CTX-FACTOR).
Establishes the Factor Context for a specific execution window.

SAFETY INVARIANTS:
- READ-ONLY: Loads data/regime, does not modify.
- ATOMIC: Computed once per window.
- SHARED: All strategies see the same factors.
- OBSERVATIONAL: No predictive logic, no strategy optimization.
"""
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd # ADDED

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from evolution.profile_loader import EvaluationProfile
from ingestion.market_loader import MarketLoader # ADDED

class FactorContextBuilder:
    """
    Builds and persists Factor Context for an EV-RUN window.
    """
    
    def __init__(self, context_path: Path, output_path: Path, profile: Optional[EvaluationProfile] = None):
        self.context_path = context_path # Path to regime_context.json
        self.output_path = output_path   # Path to factor_context.json (output)
        self.profile = profile

    def _load_regime_context(self) -> Dict[str, Any]:
        if not self.context_path.exists():
            raise FileNotFoundError(f"Regime Context not found at {self.context_path}")
        with open(self.context_path, 'r', encoding='utf-8') as f:
            return json.load(f)["regime_context"]

    def build(self) -> Dict[str, Any]:
        """
        EPISTEMIC RESTORATION: Factor Context with Data Sufficiency Contract.
        IGNITION: Real Calculation.
        """
        # 1. Load Regime Context
        regime_ctx = self._load_regime_context()
        window = regime_ctx["evaluation_window"]
        regime_code = regime_ctx.get("regime_code", "UNKNOWN")
        market = regime_ctx.get("market", "US")
        
        # 2. Data Loading
        loader = MarketLoader()
        try:
             df = loader.load_benchmark(market)
             # Filter to window_end
             end_dt = pd.to_datetime(window["end"])
             if not df.empty:
                df = df[df.index <= end_dt]
        except Exception as e:
             df = pd.DataFrame()
             print(f"Factor Data Load Error: {e}")

        # 3. Sufficiency Check
        sufficiency_status = "SUFFICIENT"
        validity_reason = "Authentic Calculation"
        
        if df.empty or len(df) < 50:
            sufficiency_status = "INSUFFICIENT"
            validity_reason = "Insufficient Data History"

        # 4. Compute Factors
        if sufficiency_status == "INSUFFICIENT":
            # FAIL-CLOSED
            factors = {
                "momentum": {"level": {"state": "UNKNOWN", "confidence": 0.0}, "strength": "UNKNOWN"},
                "volatility": {"confidence": 0.0},
                "meta": {"notes": "FAIL-CLOSED: Data insufficiency"}
            }
        else:
            # REAL CALCULATIONS
            # Momentum: Current > SMA50
            price = df.iloc[-1]['Close']
            sma20 = df['Close'].rolling(20).mean().iloc[-1]
            sma50 = df['Close'].rolling(50).mean().iloc[-1]
            
            # Trend Score
            mom_strength = "neutral"
            if price > sma20 and sma20 > sma50:
                mom_strength = "strong"
            elif price < sma20 and sma20 < sma50:
                mom_strength = "weak"
                
            # Acceleration (ROC)
            roc_10 = df['Close'].pct_change(10).iloc[-1]
            accel = "positive" if roc_10 > 0.02 else ("negative" if roc_10 < -0.02 else "flat")
            
            # Volatility
            vol_level = loader.load_volatility(market, df)
            
            # Load Rates and Growth
            rates_level = loader.load_rates(market)
            df_growth = loader.load_growth_proxy(market)
            
            # Liquidity Factor (Rates)
            liq_state = "neutral"
            liq_conf = 0.5
            
            # Heuristic for Data Format
            # If > 20, assume Index/Price Base 100
            # If < 20, assume Natural Yield %
            if rates_level > 20:
                # Synthetic Index Logic (Base 100)
                # Calibrated to synthetic noise: > 102 Tight, < 98 Loose
                if rates_level > 102:
                    liq_state = "tight"
                elif rates_level < 98:
                    liq_state = "loose"
                liq_conf = 0.8
            else:
                # Natural Yield Logic
                if rates_level > 4.0:
                    liq_state = "tight"
                elif rates_level < 2.0:
                    liq_state = "loose"
                liq_conf = 0.9
            
            # Breadth (QQQ vs SPY)
            breadth_state = "neutral"
            if not df_growth.empty and not df.empty:
                # Align dates
                aligned = pd.concat([df['Close'], df_growth['Close']], axis=1, join='inner')
                if not aligned.empty:
                    spy_ret = aligned.iloc[:,0].pct_change(20).iloc[-1]
                    qqq_ret = aligned.iloc[:,1].pct_change(20).iloc[-1]
                    if qqq_ret > spy_ret + 0.02:
                        breadth_state = "tech_lead"
                    elif qqq_ret < spy_ret - 0.02:
                        breadth_state = "tech_lag"
            
            factors = {
                "momentum": {
                    "level": {"state": mom_strength, "confidence": 0.9},
                    "acceleration": {"state": accel, "confidence": 0.8},
                    "breadth": {"state": breadth_state, "confidence": 0.8},
                    "strength": mom_strength
                },
                "value": {
                    "spread": {"state": "neutral", "confidence": 0.5}, 
                    "trend": {"state": "flat", "confidence": 0.5},
                    "liquidity_impact": {"state": liq_state, "confidence": liq_conf} 
                },
                "liquidity": {
                    "state": liq_state,
                    "level": rates_level,
                    "confidence": liq_conf
                },
                "volatility": {
                    "level": vol_level,
                    "confidence": 0.9
                },
                "meta": {
                    "factor_alignment": "calculated",
                    "notes": f"Calculated from {market} proxy"
                }
            }

        # 5. Construct Context
        factor_context = {
            "factor_context": {
                "computed_at": datetime.now().isoformat(),
                "window": window,
                "factors": factors,
                "inputs_used": ["market_loader", "proxy_adapter"],
                "sufficiency": {
                    "status": sufficiency_status,
                    "regime_input": regime_code
                },
                "validity": {
                    "viable": sufficiency_status == "SUFFICIENT",
                    "reason": validity_reason
                },
                "version": "2.0.0-IGNITION"
            }
        }

        # 6. Persist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(factor_context, f, indent=2)
            
        print(f"Generated Factor Context at: {self.output_path}")
        return factor_context

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EV-RUN-CTX-FACTOR Builder")
    parser.add_argument("--context", type=Path, required=True, help="Path to regime_context.json")
    parser.add_argument("--output", type=Path, required=True, help="Path to output factor_context.json")
    args = parser.parse_args()

    try:
        builder = FactorContextBuilder(context_path=args.context, output_path=args.output)
        builder.build()
    except Exception as e:
        print(f"FACTOR BUILD FAILURE: {e}")
        sys.exit(1)
