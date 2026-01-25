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
    
    def __init__(self):
        self._shadow_sink = ShadowExecutionSink()
        self._evaluation_log: List[StrategyEvaluationResult] = []
        self._regime_context = self._load_regime_context()
    
    def _load_regime_context(self) -> Dict[str, Any]:
        """Load and validate the authoritative regime context."""
        context_path = Path("docs/evolution/context/regime_context.json")
        if not context_path.exists():
            raise RegimeContextError("MANDATORY REGIME CONTEXT MISSING. Run EV-RUN-0 first.")
        
        with open(context_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["regime_context"]

    def get_all_strategies(self) -> List[str]:
        """
        Get all registered strategies.
        """
        # Placeholder: would integrate with actual registry
        return [
            "STRATEGY_MOMENTUM_V1",
            "STRATEGY_VALUE_QUALITY_V1",
            "STRATEGY_FACTOR_ROTATION_V1"
        ]
    
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
            state_snapshot = StateSnapshot(regime=self._regime_context["regime_label"])
        elif state_snapshot.regime != self._regime_context["regime_label"]:
             # Force consistency
             state_snapshot.regime = self._regime_context["regime_label"]
        
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

    def generate_activation_matrix(self):
        """Generate the Strategy Activation Matrix artifact."""
        output_dir = Path("docs/evolution/evaluation")
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
    try:
        evaluator = BulkEvaluator()
        print("Running Bulk Strategy Evaluation...")
        evaluator.generate_activation_matrix()
        print("EV-RUN-1 Complete.")
    except Exception as e:
        print(f"CRITICAL FAILURE: {str(e)}")
        sys.exit(1)
