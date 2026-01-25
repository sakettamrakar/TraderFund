
import pytest
from traderfund.regime.types import (
    MarketBehavior, DirectionalBias, ConfidenceComponents,
    RegimeState, RegimeOutput, RegimeLevel
)
from traderfund.regime.providers.base import (
    ITrendStrengthProvider, ITrendAlignmentProvider,
    IVolatilityRatioProvider, ILiquidityProvider,
    IEventPressureProvider
)

def test_enums_integrity():
    """Verify Enums contain required values per Tech Spec v1.1.0"""
    behaviors = set(item.value for item in MarketBehavior)
    expected_behaviors = {
        "TRENDING_NORMAL_VOL",
        "TRENDING_HIGH_VOL",
        "MEAN_REVERTING_LOW_VOL",
        "MEAN_REVERTING_HIGH_VOL",
        "EVENT_DOMINANT",
        "EVENT_LOCK",
        "UNDEFINED"
    }
    assert expected_behaviors.issubset(behaviors)

    biases = set(item.value for item in DirectionalBias)
    expected_biases = {"BULLISH", "BEARISH", "NEUTRAL"}
    assert expected_biases.issubset(biases)

def test_confidence_components_validation():
    """Verify Pydantic validation for ConfidenceComponents"""
    # Test Valid
    c = ConfidenceComponents(confluence_score=0.5, persistence_score=0.5, intensity_score=0.5)
    assert c.confluence_score == 0.5

    # Test Invalid (Out of bounds)
    with pytest.raises(ValueError):
        ConfidenceComponents(confluence_score=1.1, persistence_score=0.5, intensity_score=0.5)

def test_interfaces_are_abstract():
    """Verify ABCs cannot be instantiated"""
    with pytest.raises(TypeError):
        ITrendStrengthProvider()

    with pytest.raises(TypeError):
        IVolatilityRatioProvider()
    
    with pytest.raises(TypeError):
        ILiquidityProvider()
