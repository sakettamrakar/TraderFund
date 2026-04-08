import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.models.portfolio_models import PortfolioSnapshot, RegimeState, NarrativeState, FactorState, HoldingMeta
from src.layers.portfolio_intelligence import PortfolioIntelligenceEngine

def load_latest_snapshot(market: str, portfolio_id: str) -> PortfolioSnapshot:
    path = PROJECT_ROOT / "data" / "portfolio_intelligence" / "analytics" / market / portfolio_id / "latest.json"
    with open(path, "r") as f:
        data = json.load(f)
    
    # Map holdings to HoldingMeta
    holding_metas = []
    for h in data.get("holdings", []):
        holding_metas.append(HoldingMeta(
            symbol=h.get("ticker", "UNKNOWN"),
            weight_pct=h.get("weight_pct", 0.0),
            direction="LONG", # Default
            strategy="SWING", # Default or extract
            sector=h.get("sector", "UNKNOWN"),
            days_held=0,
            initial_convergence_score=h.get("conviction_score", 0.5),
            current_convergence_score=h.get("conviction_score", 0.5)
        ))
    
    overview = data.get("overview", {})
    return PortfolioSnapshot(
        holdings=tuple(holding_metas),
        net_exposure_pct=overview.get("net_exposure_pct", 100.0), # Assuming long-only for now if missing
        gross_exposure_pct=overview.get("gross_exposure_pct", 100.0),
        current_drawdown_pct=overview.get("total_pnl_pct", 0.0) if overview.get("total_pnl_pct", 0.0) < 0 else 0.0,
        sector_caps={} # Default
    )

def load_latest_regime(market: str) -> RegimeState:
    # Get latest tick
    tick_root = PROJECT_ROOT / "docs" / "evolution" / "ticks"
    if not tick_root.exists():
        return RegimeState(regime="TRENDING", volatility=0.2, stability_score=0.9)
        
    ticks = sorted(tick_root.glob("tick_*"))
    if not ticks:
        return RegimeState(regime="TRENDING", volatility=0.2, stability_score=0.9)
    
    regime_path = ticks[-1] / market / "regime_context.json"
    if not regime_path.exists():
        return RegimeState(regime="TRENDING", volatility=0.2, stability_score=0.9)

    with open(regime_path, "r") as f:
        data = json.load(f)
    
    ctx = data.get("regime_context", {})
    regime_str = ctx.get("regime", "TRENDING")
    
    # Map to Literal types defined in models.py
    valid_regimes = ["TRENDING", "CHOP", "TRANSITION", "STRESS", "VOLATILE", "ACCUMULATION", "DISTRIBUTION"]
    if regime_str not in valid_regimes:
        regime_str = "TRENDING"
        
    return RegimeState(
        regime=regime_str,
        volatility=0.2,
        stability_score=0.7
    )

def main():
    engine = PortfolioIntelligenceEngine()
    
    market = "INDIA"
    portfolio_id = "zerodha_primary"
    
    print(f"Loading data for {market}/{portfolio_id}...")
    try:
        portfolio = load_latest_snapshot(market, portfolio_id)
        regime = load_latest_regime(market)
        
        print(f"Evaluating Portfolio (Regime: {regime.regime})...")
        report = engine.evaluate(
            portfolio=portfolio,
            regime=regime
        )
        
        output_path = PROJECT_ROOT / "docs" / "intelligence" / f"portfolio_l9_report_{market}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, "w") as f:
            from dataclasses import asdict
            json.dump(asdict(report), f, indent=2)
            
        print(f"Report generated: {output_path}")
        print(f"Global Status: {report.global_status}")
        print(f"Flag Count: {len(report.flags)}")
        for flag in report.flags[:5]:
            print(f"  [{flag.severity}] {flag.code}: {flag.message[:100]}...")
            
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
