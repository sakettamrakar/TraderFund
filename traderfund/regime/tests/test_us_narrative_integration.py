# Test: Narrative Regime Enforcement (HARD Mode)
#
# These tests verify that regime enforcement is non-bypassable.
# All tests MUST pass before deployment.

import pytest
from traderfund.regime.narrative_adapter import (
    RegimeNarrativeAdapter,
    NarrativeSignal,
    apply_regime_to_narrative,
    get_regime_weight_for_behavior,
    get_current_us_market_regime,
    WEIGHT_MULTIPLIERS,
    FAIL_SAFE_WEIGHT
)
from traderfund.regime.types import MarketBehavior


class TestHardEnforcement:
    """Test that HARD enforcement cannot be bypassed."""
    
    def test_no_bypass_path_exists(self):
        """Verify adapter has no toggle or bypass mechanism."""
        adapter = RegimeNarrativeAdapter()
        
        # No enabled/disabled flag
        assert not hasattr(adapter, 'enabled')
        assert not hasattr(adapter, 'enforcement_mode')
        assert not hasattr(adapter, 'bypass')
        
    def test_adjust_signal_always_applies_regime(self):
        """Verify adjust_signal always queries regime."""
        adapter = RegimeNarrativeAdapter()
        signal = NarrativeSignal(
            symbol="TEST",
            weight=1.0,
            confidence=0.9,
            narrative_id="test-001",
            summary="Test"
        )
        
        result = adapter.adjust_signal(signal)
        
        # Result must have regime info
        assert result.regime is not None
        assert result.enforcement_reason is not None
        assert result.adjustment_factor is not None


class TestEventLockMuting:
    """Test that EVENT_LOCK always mutes narrative."""
    
    def test_event_lock_weight_is_zero(self):
        """EVENT_LOCK must result in final_weight == 0.0."""
        factor = get_regime_weight_for_behavior("EVENT_LOCK")
        assert factor == 0.0
    
    def test_event_lock_in_mapping(self):
        """EVENT_LOCK must be explicitly mapped to 0.0."""
        assert MarketBehavior.EVENT_LOCK in WEIGHT_MULTIPLIERS
        assert WEIGHT_MULTIPLIERS[MarketBehavior.EVENT_LOCK] == 0.0


class TestMeanRevertingDampening:
    """Test that mean-reverting regimes dampen narratives."""
    
    def test_mean_reverting_low_vol_dampens(self):
        """MEAN_REVERTING_LOW_VOL must have factor < 1.0."""
        factor = get_regime_weight_for_behavior("MEAN_REVERTING_LOW_VOL")
        assert factor < 1.0
        assert factor == 0.5
    
    def test_mean_reverting_high_vol_dampens(self):
        """MEAN_REVERTING_HIGH_VOL must have factor < 1.0."""
        factor = get_regime_weight_for_behavior("MEAN_REVERTING_HIGH_VOL")
        assert factor < 1.0
        assert factor == 0.3


class TestTrendingFullWeight:
    """Test that trending regimes get full weight."""
    
    def test_trending_normal_vol_full_weight(self):
        """TRENDING_NORMAL_VOL must have factor == 1.0."""
        factor = get_regime_weight_for_behavior("TRENDING_NORMAL_VOL")
        assert factor == 1.0


class TestHighVolDampening:
    """Test that HIGH_VOL regimes are dampened."""
    
    def test_trending_high_vol_dampens(self):
        """TRENDING_HIGH_VOL must have factor == 0.2."""
        factor = get_regime_weight_for_behavior("TRENDING_HIGH_VOL")
        assert factor == 0.2


class TestFailSafeBehavior:
    """Test fail-safe behavior for missing/unknown regimes."""
    
    def test_missing_regime_dampens(self):
        """Unknown regime string must return FAIL_SAFE_WEIGHT."""
        factor = get_regime_weight_for_behavior("UNKNOWN_REGIME_XYZ")
        assert factor == FAIL_SAFE_WEIGHT
        assert factor == 0.5
    
    def test_undefined_regime_dampens(self):
        """UNDEFINED regime must return FAIL_SAFE_WEIGHT."""
        factor = get_regime_weight_for_behavior("UNDEFINED")
        assert factor == FAIL_SAFE_WEIGHT
    
    def test_empty_string_dampens(self):
        """Empty string must return FAIL_SAFE_WEIGHT."""
        factor = get_regime_weight_for_behavior("")
        assert factor == FAIL_SAFE_WEIGHT


class TestWeightMappingFrozen:
    """Test that weight mappings are complete and frozen."""
    
    def test_all_behaviors_have_mappings(self):
        """Every MarketBehavior must have a weight mapping."""
        for behavior in MarketBehavior:
            assert behavior in WEIGHT_MULTIPLIERS, f"Missing mapping for {behavior}"
    
    def test_no_weight_exceeds_bounds(self):
        """All weights must be in [0.0, 1.5] range."""
        for behavior, weight in WEIGHT_MULTIPLIERS.items():
            assert 0.0 <= weight <= 1.5, f"Invalid weight {weight} for {behavior}"


class TestTelemetryMandatory:
    """Test that telemetry is always written."""
    
    def test_result_contains_all_fields(self):
        """AdjustedNarrative must contain all required fields."""
        adapter = RegimeNarrativeAdapter()
        signal = NarrativeSignal(
            symbol="AAPL",
            weight=0.8,
            confidence=0.9,
            narrative_id="test-002",
            summary="Test narrative"
        )
        
        result = adapter.adjust_signal(signal)
        
        # All fields must be present
        assert hasattr(result, 'original_weight')
        assert hasattr(result, 'final_weight')
        assert hasattr(result, 'adjustment_factor')
        assert hasattr(result, 'regime')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'lifecycle')
        assert hasattr(result, 'enforcement_reason')


class TestConvenienceFunctions:
    """Test convenience functions work correctly."""
    
    def test_apply_regime_to_narrative(self):
        """apply_regime_to_narrative must return valid result."""
        signal = NarrativeSignal(
            symbol="MSFT",
            weight=1.0,
            confidence=0.85,
            narrative_id="test-003",
            summary="Test"
        )
        
        result = apply_regime_to_narrative(signal)
        
        assert result.original_weight == 1.0
        assert 0.0 <= result.final_weight <= 1.0
        assert result.regime is not None
    
    def test_get_current_regime_returns_snapshot(self):
        """get_current_us_market_regime must return valid snapshot."""
        snapshot = get_current_us_market_regime()
        
        assert snapshot.regime is not None
        assert snapshot.bias is not None
        assert 0.0 <= snapshot.confidence <= 1.0
        assert 0.0 <= snapshot.narrative_weight <= 1.5
