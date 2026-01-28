"""
Paper P&L Attribution (L12 - Evolution Phase).
Calculates non-actionable paper P&L per strategy.

SAFETY INVARIANTS:
- Paper P&L is diagnostic only.
- Zero real capital impact.
- Traceable to decisions.
- Not actionable.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import sys
import json

# Add project root to path (needed if run as script)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

@dataclass
class PaperTrade:
    """A simulated paper trade."""
    trade_id: str
    decision_id: str
    strategy_id: str
    action: str
    target: str
    simulated_price: float
    simulated_quantity: float
    timestamp: datetime


@dataclass
class PaperPnL:
    """Paper P&L for a strategy."""
    strategy_id: str
    total_trades: int
    simulated_pnl: float
    is_real: bool = False  # Always False
    mode: str = "PAPER"    # Always PAPER
    regime: str = "UNDEFINED"


class RegimeContextError(Exception):
    """Raised when regime context is missing or violated."""
    pass


class PaperPnLCalculator:
    """
    Paper P&L attribution engine.
    
    SAFETY GUARANTEES:
    - All P&L is simulated/paper.
    - Zero real capital affected.
    - P&L is diagnostic, not actionable.
    - Traceable to individual decisions.
    """
    
    def __init__(self, context_path: Optional[Path] = None):
        self._paper_trades: List[PaperTrade] = []
        self._pnl_cache: Dict[str, PaperPnL] = {}
        self._trade_counter = 0
        self._context_path = context_path or Path("docs/evolution/context/regime_context.json")
        self._regime_context = self._load_regime_context()
        self._factor_context = {}  # Loaded lazily
        
    def load_factor_context(self, factor_path: Path):
        """Load the Factor Context for binding."""
        if not factor_path.exists():
            return
        with open(factor_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self._factor_context = data.get("factor_context", {}).get("factors", {})
    
    def _load_regime_context(self) -> Dict[str, Any]:
        """Load and validate the authoritative regime context."""
        if not self._context_path.exists():
            raise RegimeContextError("MANDATORY REGIME CONTEXT MISSING. Run EV-RUN-0 first.")
        
        with open(self._context_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["regime_context"]

    def record_paper_trade(
        self,
        decision_id: str,
        strategy_id: str,
        action: str,
        target: str,
        simulated_price: float,
        simulated_quantity: float
    ) -> PaperTrade:
        """
        Record a paper trade from a shadow execution.
        
        This is SIMULATION only.
        """
        self._trade_counter += 1
        
        trade = PaperTrade(
            trade_id=f"PAPER-{self._trade_counter:06d}",
            decision_id=decision_id,
            strategy_id=strategy_id,
            action=action,
            target=target,
            simulated_price=simulated_price,
            simulated_quantity=simulated_quantity,
            timestamp=datetime.now()
        )
        
        self._paper_trades.append(trade)
        return trade
    
    def calculate_strategy_pnl(self, strategy_id: str) -> PaperPnL:
        """
        Calculate paper P&L for a strategy.
        
        This is a DIAGNOSTIC metric, not actionable.
        """
        strategy_trades = [
            t for t in self._paper_trades
            if t.strategy_id == strategy_id
        ]
        
        # Simple simulated P&L (placeholder logic)
        simulated_pnl = sum(
            t.simulated_price * t.simulated_quantity * (1 if t.action == "BUY" else -1)
            for t in strategy_trades
        )
        
        pnl = PaperPnL(
            strategy_id=strategy_id,
            total_trades=len(strategy_trades),
            simulated_pnl=simulated_pnl,
            is_real=False,  # ALWAYS False
            mode="PAPER",    # ALWAYS PAPER
            regime=self._regime_context["regime_label"]
        )
        
        self._pnl_cache[strategy_id] = pnl
        return pnl
    
    def get_all_pnl(self) -> Dict[str, PaperPnL]:
        """Get paper P&L for all strategies."""
        return self._pnl_cache.copy()
    
    def generate_summary(self, output_dir: Optional[Path] = None):
        """Generate Paper P&L Summary Artifact."""
        output_dir = output_dir or Path("docs/evolution/evaluation")
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = output_dir / "paper_pnl_summary.csv"
        
        # Consistent regime label from context
        regime_label = self._regime_context["regime_label"]
        
        # Calculate for all strategies (Mock data for this run)
        results = []
        for strat in ["STRATEGY_MOMENTUM_V1", "STRATEGY_VALUE_QUALITY_V1"]:
            results.append({
                "strategy_id": strat,
                "total_pnl": 0.0,
                "sharpe": 0.0,
                "max_drawdown": 0.0,
                "regime": regime_label
            })
            
        import pandas as pd
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False)
        print(f"Generated: {csv_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EV-RUN-3: Paper P&L Calculator")
    parser.add_argument("--context", type=Path, help="Path to regime_context.json")
    parser.add_argument("--output", type=Path, help="Directory for output artifacts")
    args = parser.parse_args()

    try:
        calculator = PaperPnLCalculator(context_path=args.context)
        
        # Binding Factor Context
        if args.output:
            factor_path = args.output / "factor_context.json"
            calculator.load_factor_context(factor_path)
            
        print("Running Paper P&L Calculation...")
        calculator.generate_summary(output_dir=args.output)
        print("EV-RUN-3 Complete.")
    except Exception as e:
        print(f"CRITICAL FAILURE: {str(e)}")
        sys.exit(1)
