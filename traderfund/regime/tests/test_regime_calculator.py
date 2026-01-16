
import pytest
from traderfund.regime.calculator import RegimeCalculator, RawRegime
from traderfund.regime.types import MarketBehavior, DirectionalBias

class TestRegimeCalculator:
    @pytest.fixture
    def calc(self):
        return RegimeCalculator(
            trend_threshold=0.25,
            high_vol_ratio=1.5,
            liquidity_min=0.2,
            event_pressure_dominant=0.8
        )

    def test_event_lock_priority(self, calc):
        """Event Lock should override everything else."""
        res = calc.calculate(
            trend_strength=0.9,      # Strong Trend
            trend_bias=DirectionalBias.BULLISH,
            volatility_ratio=1.0,
            liquidity_score=1.0,     # High Liquidity
            event_pressure=1.0,
            is_event_locked=True     # LOCKED
        )
        assert res.behavior == MarketBehavior.EVENT_LOCK
        assert res.bias == DirectionalBias.NEUTRAL

    def test_liquidity_dry_priority(self, calc):
        """Liquidity Dry should override Trend/Vol, but is under Event Lock."""
        res = calc.calculate(
            trend_strength=0.9,
            trend_bias=DirectionalBias.BULLISH,
            volatility_ratio=1.0,
            liquidity_score=0.1,    # Below 0.2
            event_pressure=0.0,
            is_event_locked=False
        )
        assert res.behavior == MarketBehavior.UNDEFINED
        assert res.event_state_description == "LIQUIDITY_DRY"

    def test_event_dominant_measure(self, calc):
        """High Pressure should trigger EVENT_DOMINANT."""
        res = calc.calculate(
            trend_strength=0.5,
            trend_bias=DirectionalBias.BEARISH,
            volatility_ratio=1.0,
            liquidity_score=1.0,
            event_pressure=0.9,     # > 0.8
            is_event_locked=False
        )
        assert res.behavior == MarketBehavior.EVENT_DOMINANT
        assert res.bias == DirectionalBias.BEARISH # Passthrough

    def test_technical_matrix(self, calc):
        # 1. Trending + Normal Vol
        res = calc.calculate(0.5, DirectionalBias.BULLISH, 1.0, 1.0, 0.0, False)
        assert res.behavior == MarketBehavior.TRENDING_NORMAL_VOL
        assert res.bias == DirectionalBias.BULLISH

        # 2. Trending + High Vol
        res = calc.calculate(0.5, DirectionalBias.BULLISH, 1.6, 1.0, 0.0, False)
        assert res.behavior == MarketBehavior.TRENDING_HIGH_VOL

        # 3. Mean Rev + Low Vol
        res = calc.calculate(0.1, DirectionalBias.NEUTRAL, 1.0, 1.0, 0.0, False)
        assert res.behavior == MarketBehavior.MEAN_REVERTING_LOW_VOL

        # 4. Mean Rev + High Vol
        res = calc.calculate(0.1, DirectionalBias.NEUTRAL, 2.0, 1.0, 0.0, False)
        assert res.behavior == MarketBehavior.MEAN_REVERTING_HIGH_VOL

    def test_boundary_conditions(self, calc):
        # Exact Trend Threshold
        res = calc.calculate(0.25, DirectionalBias.BULLISH, 1.0, 1.0, 0.0, False)
        assert res.behavior == MarketBehavior.TRENDING_NORMAL_VOL

        # Just below Trend
        res = calc.calculate(0.249, DirectionalBias.BULLISH, 1.0, 1.0, 0.0, False)
        assert res.behavior == MarketBehavior.MEAN_REVERTING_LOW_VOL
