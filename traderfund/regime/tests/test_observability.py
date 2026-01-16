
import pytest
import json
import logging
from datetime import datetime
from unittest.mock import MagicMock

from traderfund.regime.types import (
    RegimeState, MarketBehavior, DirectionalBias, ConfidenceComponents, RegimeFactors
)
from traderfund.regime.observability import RegimeFormatter, RegimeLogger
from traderfund.regime.gate import StrategyClass

@pytest.fixture
def sample_state():
    return RegimeState(
        behavior=MarketBehavior.TRENDING_NORMAL_VOL,
        bias=DirectionalBias.BULLISH,
        id=1,
        confidence_components=ConfidenceComponents(
            confluence_score=0.9, persistence_score=0.8, intensity_score=0.7
        ),
        total_confidence=0.82,
        is_stable=True
    )

@pytest.fixture
def sample_factors():
    return RegimeFactors(
        trend_strength_norm=0.75,
        volatility_ratio=1.05,
        liquidity_status="NORMAL",
        event_pressure_norm=0.1
    )

class TestRegimeFormatter:
    def test_json_structure(self, sample_state, sample_factors):
        json_str = RegimeFormatter.to_json(sample_state, sample_factors, "NIFTY")
        data = json.loads(json_str)
        
        # Meta Check
        assert data['meta']['symbol'] == "NIFTY"
        assert "timestamp" in data['meta']
        
        # Regime Check
        assert data['regime']['behavior'] == "TRENDING_NORMAL_VOL"
        assert data['regime']['bias'] == "BULLISH"
        assert data['regime']['confidence_detail']['confluence'] == 0.9
        
        # Constraints Check (Momentum allowed in Normal Trend)
        assert "MOMENTUM" in data['constraints']['allowed_strategies']
        assert "MEAN_REVERSION" in data['constraints']['blocked_strategies']

    def test_risk_off_constraints(self, sample_state):
        # Change to EVENT_LOCK
        sample_state.behavior = MarketBehavior.EVENT_LOCK
        
        data = RegimeFormatter.to_dict(sample_state)
        
        # All blocked
        assert "MOMENTUM" in data['constraints']['blocked_strategies']
        assert len(data['constraints']['allowed_strategies']) == 0

    def test_cli_output(self, sample_state):
        # Normal
        s = RegimeFormatter.to_cli_string(sample_state)
        assert "[REGIME] TRENDING_NORMAL_VOL" in s
        assert "Bias=BULLISH" in s
        assert "Stable=T" in s
        assert "(!)" not in s
        
        # Risk Off
        sample_state.behavior = MarketBehavior.UNDEFINED
        s2 = RegimeFormatter.to_cli_string(sample_state)
        assert "(!)" in s2

class TestRegimeLogger:
    def test_logging_levels(self, sample_state):
        mock_logger = MagicMock()
        logger = RegimeLogger(mock_logger)
        
        # Info Level
        logger.log_update(sample_state, "TEST")
        mock_logger.info.assert_called_once()
        
        # Warning Level
        sample_state.behavior = MarketBehavior.TRENDING_HIGH_VOL
        mock_logger.reset_mock()
        logger.log_update(sample_state, "TEST")
        mock_logger.warning.assert_called_once()
