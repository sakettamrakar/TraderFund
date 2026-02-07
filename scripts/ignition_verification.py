import sys
from pathlib import Path
import os

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from evolution.regime_context_builder import RegimeContextBuilder
from evolution.factor_context_builder import FactorContextBuilder

def run_verification(market):
    print(f"--- Verifying Ignition for {market} ---")
    
    # Paths
    regime_path = project_root / f"docs/evolution/context/regime_context_{market}.json"
    factor_path = project_root / f"docs/evolution/context/factor_context_{market}.json"
    
    # 1. Regime Build
    print(f"Building Regime Context...")
    r_builder = RegimeContextBuilder(output_path=str(regime_path), market=market)
    r_context = r_builder.build_context()
    print(f"Regime Code: {r_context['regime_context']['regime_code']}")
    
    # 2. Factor Build
    print(f"Building Factor Context...")
    f_builder = FactorContextBuilder(context_path=regime_path, output_path=factor_path)
    f_context = f_builder.build()
    mom = f_context['factor_context']['factors']['momentum']
    print(f"Momentum Level: {mom['level']['state']} (Confidence: {mom['level']['confidence']})")
    
    print("Verification Successful.\n")

if __name__ == "__main__":
    try:
        run_verification("US")
        run_verification("INDIA")
    except Exception as e:
        print(f"VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
