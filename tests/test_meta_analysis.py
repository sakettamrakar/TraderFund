import pytest
from src.intelligence.meta_analysis import MetaAnalysis

def test_meta_analysis_no_context():
    ma = MetaAnalysis()
    result = ma.analyze(regime_state=None)
    assert result["trust_score"] == 0.0
    assert result["status"] == "INSUFFICIENT_CONTEXT"
    assert ma.trust_score == 0.0
    assert ma.status == "INSUFFICIENT_CONTEXT"

def test_meta_analysis_with_context():
    ma = MetaAnalysis()
    regime = {"bias": "BULLISH", "confidence": 0.9}
    result = ma.analyze(regime_state=regime)
    assert result["trust_score"] > 0.0
    assert result["status"] == "ACTIVE"
    assert ma.regime_state == regime
