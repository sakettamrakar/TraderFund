"""
Bulk Strategy Evaluator (L12 - Evolution Phase).
Enables bulk strategy evaluation without manual wiring.

SAFETY INVARIANTS:
- All registered strategies evaluable.
- No per-strategy manual setup.
- Bulk iteration supported.
- No execution, only evaluation.
"""
from typing import List, Dict, Any, Optional, Iterator
from datetime import datetime
from pathlib import Path
import sys
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from decision.decision_spec import DecisionSpec, DecisionFactory, ProposedAction, StateSnapshot, DecisionRouting
from decision.shadow_sink import ShadowExecutionSink
from strategy.registry import STRATEGY_REGISTRY

class RegimeContextError(Exception):
    """Raised when regime context is missing or violated."""
    pass

class StrategyEvaluationResult:
    """Result of evaluating a single strategy."""
    def __init__(
        self,
        strategy_id: str,
        decisions_generated: int,
        shadow_executions: int,
        failures: List[Dict[str, Any]],
        diagnostics: Dict[str, Any]
    ):
        self.strategy_id = strategy_id
        self.decisions_generated = decisions_generated
        self.shadow_executions = shadow_executions
        self.failures = failures
        self.diagnostics = diagnostics
        self.timestamp = datetime.now()


class BulkEvaluator:
    """
    Bulk strategy evaluation engine.
    
    SAFETY GUARANTEES:
    - All registered strategies are evaluable.
    - No per-strategy manual wiring.
    - Evaluation produces diagnostics, not actions.
    - Shadow execution only.
    """
    
    def __init__(self, context_path: Optional[Path] = None):
        self._shadow_sink = ShadowExecutionSink()
        self._evaluation_log: List[StrategyEvaluationResult] = []
        self._context_path = context_path or Path("docs/evolution/context/regime_context.json")
        # Infer factor context path from output dir (if available) or assume relative
        self._regime_context = self._load_regime_context()
        self._factor_context = {}  # Loaded lazily or via separate init
    
    def load_factor_context(self, factor_path: Path):
        """Load the Factor Context for binding."""
        if not factor_path.exists():
            print(f"WARNING: Factor Context not found at {factor_path}. Proceeding without it.")
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

    def get_all_strategies(self) -> List[str]:
        """
        Get all registered strategies.
        """
        return list(STRATEGY_REGISTRY.keys())
    
    def evaluate_strategy(
        self,
        strategy_id: str,
        state_snapshot: Optional[StateSnapshot] = None
    ) -> StrategyEvaluationResult:
        """
        Evaluate a single strategy.
        This is SHADOW EXECUTION only.
        """
        # FORBIDDEN: Independent regime computation
        if state_snapshot is None:
            state_snapshot = StateSnapshot(
                regime=self._regime_context["regime_label"],
                factor_context=self._factor_context
            )
        elif state_snapshot.regime != self._regime_context["regime_label"]:
             # Force consistency
             state_snapshot.regime = self._regime_context["regime_label"]
             state_snapshot.factor_context = self._factor_context
        
        failures = []
        decisions = []
        
        # Simulate decision generation for this strategy
        try:
            # Create a test decision
            decision = DecisionFactory.create(
                strategy_ref=strategy_id,
                proposed_action=ProposedAction(
                    action_type="EVALUATE",
                    target="SIMULATION",
                    rationale=f"Bulk evaluation of {strategy_id}"
                ),
                state_snapshot=state_snapshot,
                routing=DecisionRouting.SHADOW
            )
            decisions.append(decision)
            
            # Execute in shadow mode
            self._shadow_sink.execute(decision)
            
        except Exception as e:
            failures.append({
                "type": "EVALUATION_ERROR",
                "strategy_id": strategy_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        result = StrategyEvaluationResult(
            strategy_id=strategy_id,
            decisions_generated=len(decisions),
            shadow_executions=len(decisions) - len(failures),
            failures=failures,
            diagnostics={
                "state_regime": state_snapshot.regime,
                "evaluation_mode": "SHADOW"
            }
        )
        
        self._evaluation_log.append(result)
        return result
    
    def evaluate_all(self, state_snapshot: Optional[StateSnapshot] = None) -> List[StrategyEvaluationResult]:
        """
        Evaluate all registered strategies.
        """
        strategies = self.get_all_strategies()
        results = []
        
        for strategy_id in strategies:
            result = self.evaluate_strategy(strategy_id, state_snapshot)
            results.append(result)
        
        return results
    
    def iterate_strategies(self) -> Iterator[str]:
        """Iterate over all registered strategies."""
        for strategy_id in self.get_all_strategies():
            yield strategy_id
    
    def get_evaluation_log(self) -> List[StrategyEvaluationResult]:
        """Get the complete evaluation log."""
        return self._evaluation_log.copy()

    def generate_activation_matrix(self, output_dir: Optional[Path] = None):
        """Generate the Strategy Activation Matrix artifact."""
        output_dir = output_dir or Path("docs/evolution/evaluation")
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = output_dir / "strategy_activation_matrix.csv"
        
        results = self.evaluate_all()
        
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["strategy_id", "decisions", "shadow", "failures", "regime", "timestamp"])
            for r in results:
                writer.writerow([
                    r.strategy_id,
                    r.decisions_generated,
                    r.shadow_executions,
                    len(r.failures),
                    r.diagnostics.get("state_regime", "UNKNOWN"),
                    r.timestamp.isoformat()
                ])
        print(f"Generated: {csv_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EV-RUN-1: Bulk Strategy Evaluator")
    parser.add_argument("--context", type=Path, help="Path to regime_context.json")
    parser.add_argument("--output", type=Path, help="Directory for output artifacts")
    args = parser.parse_args()

    try:
        evaluator = BulkEvaluator(context_path=args.context)
        
        # Load Factor Context (Expected in output dir)
        if args.output:
            factor_path = args.output / "factor_context.json"
            evaluator.load_factor_context(factor_path)
            
        print("Running Bulk Strategy Evaluation...")
        evaluator.generate_activation_matrix(output_dir=args.output)
        print("EV-RUN-1 Complete.")
    except Exception as e:
        print(f"CRITICAL FAILURE: {str(e)}")
        sys.exit(1)
