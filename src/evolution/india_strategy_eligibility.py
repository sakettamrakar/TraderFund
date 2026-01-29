"""
India Strategy Eligibility Resolver.
"""
import json
from pathlib import Path
from evolution.strategy_eligibility_resolver import resolve_all_strategies

def resolve_india_eligibility(regime_ctx_path: Path, factor_ctx_path: Path, output_dir: Path):
    """
    Resolves strategy eligibility for India based on India Regime and Factor contexts.
    """
    # Load Contexts
    with open(regime_ctx_path, 'r') as f:
        regime_data = json.load(f)
    current_regime = regime_data.get("regime_context", {}).get("regime", "NEUTRAL")

    with open(factor_ctx_path, 'r') as f:
        factor_data = json.load(f)

    factors = factor_data.get("factor_context", {}).get("factors", {})

    # Map Factor Context to Resolver Inputs
    mom_level = factors.get("momentum", {}).get("level", {}).get("state", "neutral").upper()
    if mom_level == "NEUTRAL": mom_level = "NONE"

    # In absence of detailed Watchers, we default others to NEUTRAL/NONE
    current_factors = {
        "momentum": mom_level,
        "expansion": "NONE",
        "dispersion": "NONE",
        "liquidity": "NEUTRAL"
    }

    # Resolve
    resolution = resolve_all_strategies(current_regime, current_factors)

    # Persist as requested
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "strategy_eligibility.json"
    with open(output_path, "w") as f:
        json.dump(resolution, f, indent=2)

    return resolution
