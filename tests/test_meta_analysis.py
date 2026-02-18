import pytest
from src.intelligence.meta_analysis import MetaAnalysis
from traderfund.regime.types import MarketBehavior

def test_meta_analysis_no_context():
    ma = MetaAnalysis()
    result = ma.analyze(regime_state=None)
    assert result["trust_score"] == 0.0
    assert result["status"] == "INSUFFICIENT_CONTEXT"
    assert ma.trust_score == 0.0
    assert ma.status == "INSUFFICIENT_CONTEXT"

def test_meta_analysis_with_context():
    ma = MetaAnalysis()
    # Provide behavior for robustness, though code defaults to UNDEFINED
    regime = {"bias": "BULLISH", "confidence": 0.9, "behavior": MarketBehavior.TRENDING_NORMAL_VOL}
    result = ma.analyze(regime_state=regime)
    assert result["trust_score"] > 0.0
    assert result["status"] == "ACTIVE"
    assert ma.regime_state == regime

def test_invariant3_chop_rejection():
    """
    In CHOP or TRANSITION regime: Technical breakout trust ≤ 0.50
    """
    ma = MetaAnalysis()
    regime = {"behavior": MarketBehavior.MEAN_REVERTING_LOW_VOL} # CHOP

    # Violation: trust > 0.50
    result = ma.analyze(
        regime_state=regime,
        technical_breakout_trust=0.51
    )
    assert result["status"] == "REJECTED"
    assert result["trust_score"] == 0.0
    assert "Invariant 3 Violation" in result["reason"]

    # Success: trust <= 0.50
    result = ma.analyze(
        regime_state=regime,
        technical_breakout_trust=0.50
    )
    assert result["status"] == "ACTIVE"

def test_invariant3_transition_rejection():
    """
    In CHOP or TRANSITION regime: Technical breakout trust ≤ 0.50
    """
    ma = MetaAnalysis()
    regime = {"behavior": MarketBehavior.UNDEFINED} # TRANSITION

    # Violation: trust > 0.50
    result = ma.analyze(
        regime_state=regime,
        technical_breakout_trust=0.60
    )
    assert result["status"] == "REJECTED"

    # Success
    result = ma.analyze(
        regime_state=regime,
        technical_breakout_trust=0.40
    )
    assert result["status"] == "ACTIVE"

def test_invariant3_trending_momentum():
    """
    In TRENDING regime: Momentum trust ≥ 0.60 IF factor alignment present
    """
    ma = MetaAnalysis()
    regime = {"behavior": MarketBehavior.TRENDING_NORMAL_VOL} # TRENDING

    # Violation: factor alignment present, momentum trust < 0.60
    result = ma.analyze(
        regime_state=regime,
        momentum_trust=0.59,
        factor_alignment=True
    )
    assert result["status"] == "REJECTED"
    assert "Invariant 3 Violation" in result["reason"]

    # Success: factor alignment present, momentum trust >= 0.60
    result = ma.analyze(
        regime_state=regime,
        momentum_trust=0.60,
        factor_alignment=True
    )
    assert result["status"] == "ACTIVE"

    # Success: no factor alignment, momentum trust can be anything (e.g. low)
    result = ma.analyze(
        regime_state=regime,
        momentum_trust=0.20,
        factor_alignment=False
    )
    assert result["status"] == "ACTIVE"
