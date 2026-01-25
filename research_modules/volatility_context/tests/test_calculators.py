"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Unit tests for volatility calculators.

Note: Tests import directly from submodules to avoid triggering the
phase lock in the main __init__.py.
##############################################################################
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import directly from calculators to bypass phase lock
import sys
sys.path.insert(0, str(__file__).rsplit("tests", 1)[0])


class TestATRCalculator:
    """Tests for ATR calculation functions."""

    def test_true_range_basic(self):
        """True range with no previous close should return high - low."""
        from research_modules.volatility_context.calculators.atr import calculate_true_range
        tr = calculate_true_range(high=105, low=100, prev_close=None)
        assert tr == 5.0

    def test_true_range_with_gap_up(self):
        """True range should account for gap up."""
        from research_modules.volatility_context.calculators.atr import calculate_true_range
        # Gap up: prev_close=95, high=105, low=100
        # TR = max(105-100, |105-95|, |100-95|) = max(5, 10, 5) = 10
        tr = calculate_true_range(high=105, low=100, prev_close=95)
        assert tr == 10.0

    def test_true_range_with_gap_down(self):
        """True range should account for gap down."""
        from research_modules.volatility_context.calculators.atr import calculate_true_range
        # Gap down: prev_close=110, high=105, low=100
        # TR = max(105-100, |105-110|, |100-110|) = max(5, 5, 10) = 10
        tr = calculate_true_range(high=105, low=100, prev_close=110)
        assert tr == 10.0

    def test_atr_series(self):
        """ATR should produce a series of correct length."""
        from research_modules.volatility_context.calculators.atr import calculate_atr

        # Create sample data
        data = pd.DataFrame({
            "high": [100 + i + 1 for i in range(30)],
            "low": [100 + i - 1 for i in range(30)],
            "close": [100 + i for i in range(30)],
        })

        atr = calculate_atr(data, period=14)
        assert len(atr) == 30
        assert all(pd.notna(atr.iloc[14:]))  # Should have values after period

    def test_atr_deterministic(self):
        """ATR calculation should be deterministic."""
        from research_modules.volatility_context.calculators.atr import calculate_atr

        data = pd.DataFrame({
            "high": [100 + i + 1 for i in range(30)],
            "low": [100 + i - 1 for i in range(30)],
            "close": [100 + i for i in range(30)],
        })

        atr1 = calculate_atr(data.copy(), period=14)
        atr2 = calculate_atr(data.copy(), period=14)

        pd.testing.assert_series_equal(atr1, atr2)


class TestDailyRangeCalculator:
    """Tests for daily range calculation functions."""

    def test_daily_range_basic(self):
        """Daily range should return high - low."""
        from research_modules.volatility_context.calculators.daily_range import calculate_daily_range
        assert calculate_daily_range(105, 100) == 5.0

    def test_daily_range_pct(self):
        """Daily range percentage should be relative to reference price."""
        from research_modules.volatility_context.calculators.daily_range import calculate_daily_range_pct
        # Range = 5, Reference = 100, Pct = 5%
        pct = calculate_daily_range_pct(105, 100, 100)
        assert pct == 5.0

    def test_range_expansion(self):
        """Range expansion should be ratio of current to average."""
        from research_modules.volatility_context.calculators.daily_range import calculate_range_expansion
        # Current = 10, Avg = 5 → Expansion = 2.0x
        ratio = calculate_range_expansion(10, 5)
        assert ratio == 2.0

    def test_range_expansion_zero_avg(self):
        """Range expansion with zero average should return 0."""
        from research_modules.volatility_context.calculators.daily_range import calculate_range_expansion
        ratio = calculate_range_expansion(10, 0)
        assert ratio == 0.0


class TestVolatilityRegimeClassifier:
    """Tests for regime classification functions."""

    def test_classify_volatility_low(self):
        """Should classify as LOW when ATR is below mean - std."""
        from research_modules.volatility_context.calculators.volatility_regime import classify_volatility
        # Current = 5, Mean = 10, Std = 2 → z = (5-10)/2 = -2.5 → LOW
        label = classify_volatility(5, 10, 2)
        assert label == "LOW"

    def test_classify_volatility_high(self):
        """Should classify as HIGH when ATR is above mean + std."""
        from research_modules.volatility_context.calculators.volatility_regime import classify_volatility
        # Current = 15, Mean = 10, Std = 2 → z = (15-10)/2 = 2.5 → HIGH
        label = classify_volatility(15, 10, 2)
        assert label == "HIGH"

    def test_classify_volatility_normal(self):
        """Should classify as NORMAL when ATR is within 1 std of mean."""
        from research_modules.volatility_context.calculators.volatility_regime import classify_volatility
        # Current = 10, Mean = 10, Std = 2 → z = 0 → NORMAL
        label = classify_volatility(10, 10, 2)
        assert label == "NORMAL"

    def test_classify_trend_trending(self):
        """Should classify as TRENDING when direction is consistent."""
        from research_modules.volatility_context.calculators.volatility_regime import classify_trend
        # 80% up moves = TRENDING
        prices = pd.Series([100 + i for i in range(25)])  # Monotonic up
        label = classify_trend(prices, lookback=20)
        assert label == "TRENDING"

    def test_classify_trend_ranging(self):
        """Should classify as RANGING or UNCLEAR when direction is mixed."""
        from research_modules.volatility_context.calculators.volatility_regime import classify_trend
        # Alternating = no clear direction
        prices = pd.Series([100 + (i % 2) for i in range(25)])
        label = classify_trend(prices, lookback=20)
        assert label in ["RANGING", "UNCLEAR"]  # Either is acceptable for mixed

    def test_classify_range_state_expansion(self):
        """Should classify as EXPANSION when current >> average."""
        from research_modules.volatility_context.calculators.volatility_regime import classify_range_state
        label = classify_range_state(current_range=20, avg_range=10)
        assert label == "EXPANSION"

    def test_classify_range_state_compression(self):
        """Should classify as COMPRESSION when current << average."""
        from research_modules.volatility_context.calculators.volatility_regime import classify_range_state
        label = classify_range_state(current_range=3, avg_range=10)
        assert label == "COMPRESSION"
