
import pytest
from traderfund.regime.gate import StrategyGate, StrategyClass, GateAction
from traderfund.regime.types import (
    RegimeState, MarketBehavior, DirectionalBias, ConfidenceComponents
)

@pytest.fixture
def dummy_regime():
    return RegimeState(
        behavior=MarketBehavior.TRENDING_NORMAL_VOL,
        bias=DirectionalBias.BULLISH,
        id=1,
        confidence_components=ConfidenceComponents(
            confluence_score=0.8, persistence_score=0.8, intensity_score=0.8
        ),
        total_confidence=0.8,
        is_stable=True
    )

class TestStrategyGate:
    def test_global_blocks(self, dummy_regime):
        gate = StrategyGate()
        
        # 1. EVENT_LOCK
        dummy_regime.behavior = MarketBehavior.EVENT_LOCK
        decision = gate.evaluate(dummy_regime, StrategyClass.MOMENTUM)
        assert decision.is_allowed is False
        assert decision.size_multiplier == 0.0
        assert "EVENT_LOCK" in decision.reason

        # 2. UNDEFINED
        dummy_regime.behavior = MarketBehavior.UNDEFINED
        decision = gate.evaluate(dummy_regime, StrategyClass.SCALPING)
        assert decision.is_allowed is False
        assert "UNDEFINED" in decision.reason

    def test_momentum_compatibility(self, dummy_regime):
        gate = StrategyGate()
        
        # Normal Trend -> ALLOW
        dummy_regime.behavior = MarketBehavior.TRENDING_NORMAL_VOL
        d = gate.evaluate(dummy_regime, StrategyClass.MOMENTUM)
        assert d.is_allowed is True
        assert d.size_multiplier == 1.0
        
        # High Vol Trend -> REDUCE
        dummy_regime.behavior = MarketBehavior.TRENDING_HIGH_VOL
        d = gate.evaluate(dummy_regime, StrategyClass.MOMENTUM)
        assert d.is_allowed is True
        assert d.size_multiplier == 0.5
        assert "REDUCED" in d.reason
        
        # Mean Reversion -> BLOCK
        dummy_regime.behavior = MarketBehavior.MEAN_REVERTING_LOW_VOL
        d = gate.evaluate(dummy_regime, StrategyClass.MOMENTUM)
        assert d.is_allowed is False

    def test_scalping_resilience(self, dummy_regime):
        gate = StrategyGate()
        
        # Scalping likes High Vol
        dummy_regime.behavior = MarketBehavior.MEAN_REVERTING_HIGH_VOL
        d = gate.evaluate(dummy_regime, StrategyClass.SCALPING)
        assert d.is_allowed is True
        assert d.size_multiplier == 1.0

    def test_event_strategy_isolation(self, dummy_regime):
        gate = StrategyGate()
        
        # Event Strategy blocked in Normal
        dummy_regime.behavior = MarketBehavior.TRENDING_NORMAL_VOL
        d = gate.evaluate(dummy_regime, StrategyClass.EVENT)
        assert d.is_allowed is False
        
        # Allowed in Event Dominant
        dummy_regime.behavior = MarketBehavior.EVENT_DOMINANT
        d = gate.evaluate(dummy_regime, StrategyClass.EVENT)
        assert d.is_allowed is True
