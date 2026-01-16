
import pytest
from traderfund.regime.core import StateManager
from traderfund.regime.calculator import RawRegime
from traderfund.regime.types import (
    MarketBehavior, DirectionalBias, RegimeFactors
)

class TestStateManager:
    @pytest.fixture
    def manager(self):
        # Setup with small hysteresis for easier testing
        return StateManager(
            hysteresis_risk_on=3,
            hysteresis_risk_off=1,
            hysteresis_default=2,
            cooldown_bars=5 # Short cooldown
        )

    @pytest.fixture
    def factors(self):
        return RegimeFactors(
            trend_strength_norm=0.5,
            volatility_ratio=1.0,
            liquidity_status="NORMAL",
            event_pressure_norm=0.0
        )

    def test_immediate_risk_off(self, manager, factors):
        # Start in Normal
        manager.current_behavior = MarketBehavior.TRENDING_NORMAL_VOL
        
        # Risk Off Signal (HIGH VOL) -> Hysteresis 1 (Immediate)
        raw = RawRegime(MarketBehavior.TRENDING_HIGH_VOL, DirectionalBias.BULLISH, "HighVol")
        
        state = manager.update(raw, factors)
        
        assert state.behavior == MarketBehavior.TRENDING_HIGH_VOL
        assert manager.persistence_counter == 0

    def test_delayed_risk_on(self, manager, factors):
        # Start in High Vol
        manager.current_behavior = MarketBehavior.TRENDING_HIGH_VOL
        
        # Risk On Signal (Normal) -> Hysteresis 3
        # Tick 1
        raw = RawRegime(MarketBehavior.TRENDING_NORMAL_VOL, DirectionalBias.BULLISH, "Norm")
        state = manager.update(raw, factors)
        assert state.behavior == MarketBehavior.TRENDING_HIGH_VOL # Not switched
        assert manager.pending_counter == 1
        
        # Tick 2
        state = manager.update(raw, factors)
        assert state.behavior == MarketBehavior.TRENDING_HIGH_VOL
        assert manager.pending_counter == 2
        
        # Tick 3 (Switch)
        state = manager.update(raw, factors)
        assert state.behavior == MarketBehavior.TRENDING_NORMAL_VOL
        assert manager.persistence_counter == 0 # Reset on switch

    def test_flicker_prevention(self, manager, factors):
        # Current: Normal. Hysteresis Default = 2.
        manager.current_behavior = MarketBehavior.TRENDING_NORMAL_VOL
        
        # Tick 1: Mean Rev (Pending 1)
        raw1 = RawRegime(MarketBehavior.MEAN_REVERTING_LOW_VOL, DirectionalBias.NEUTRAL, "mr")
        manager.update(raw1, factors)
        assert manager.pending_behavior == MarketBehavior.MEAN_REVERTING_LOW_VOL
        
        # Tick 2: Back to Normal (Reset Pending)
        raw2 = RawRegime(MarketBehavior.TRENDING_NORMAL_VOL, DirectionalBias.BULLISH, "tr")
        manager.update(raw2, factors)
        assert manager.pending_behavior is None
        assert manager.pending_counter == 0
        assert manager.current_behavior == MarketBehavior.TRENDING_NORMAL_VOL

    def test_cooldown_logic(self, manager, factors):
        # 1. Be in EVENT_LOCK
        manager.current_behavior = MarketBehavior.EVENT_LOCK
        
        # 2. Transition OUT -> Trigger Cooldown
        # Raw says Normal, but cooldown should kick in.
        raw = RawRegime(MarketBehavior.TRENDING_NORMAL_VOL, DirectionalBias.BULLISH, "Norm")
        
        # First update triggers the transition logic FROM lock.
        # However, risk-on hysteresis is 3. 
        # But wait, logic says: "If current == LOCK and raw != LOCK -> Trigger Timer".
        state = manager.update(raw, factors)
        
        # Since Raw != Current, pending starts. Timer set to 5.
        
        assert manager.cooldown_timer == 5
        # Pending starts for Normal Vol
        assert manager.pending_counter == 1
        
        # Tick 2. Timer > 0.
        # Code: "If Raw is Normal/Low Vol -> Force UNDEFINED"
        # So Raw becomes UNDEFINED.
        # Current is LOCK. Raw is UNDEFINED.
        # Hysteresis for UNDEFINED (Risk Off) is 1.
        # So it should switch to UNDEFINED immediately?
        
        state = manager.update(raw, factors) # Raw passed is Normal, implicitly converted to UNDEFINED inside
        
        # Raw became UNDEFINED. Current was LOCK. Raw != Current.
        # Pending behavior (Normal) != Raw (Undefined). Reset pending?
        # Or does it switch pending to Undefined.
        # Switch to Undefined. 
        # Pending Undefined counter = 1. Risk Off Hysteresis = 1.
        # Switch!
        
        assert state.behavior == MarketBehavior.UNDEFINED
        assert manager.cooldown_timer == 4

    def test_persistence_tracking(self, manager, factors):
        manager.current_behavior = MarketBehavior.TRENDING_NORMAL_VOL
        manager.persistence_counter = 10
        
        raw = RawRegime(MarketBehavior.TRENDING_NORMAL_VOL, DirectionalBias.BULLISH, "Norm")
        state = manager.update(raw, factors)
        
        assert manager.persistence_counter == 11
        assert state.confidence_components.persistence_score > 0.1
