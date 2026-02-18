import pytest
import logging
from src.intelligence.meta_analysis import MetaAnalysis
from traderfund.regime.types import MarketBehavior

def test_meta_analysis_logging_success(caplog):
    """
    Verify that successful analysis logs the required fields.
    """
    caplog.set_level(logging.INFO, logger="MetaAnalysis")
    ma = MetaAnalysis()
    regime = {"behavior": MarketBehavior.TRENDING_NORMAL_VOL}
    
    # Analyze with signal_type
    ma.analyze(regime_state=regime, signal_type="TEST_SIGNAL")
    
    # Verify logs
    assert len(caplog.records) == 1
    record = caplog.records[0]
    log_msg = record.message
    
    # Check for required fields in the log message
    assert "Trust Decision:" in log_msg
    assert "Signal Type=TEST_SIGNAL" in log_msg
    assert "Regime Context=" in log_msg
    assert "Adjustment Reason=Success" in log_msg
    assert "Final Trust Score=1.0" in log_msg
    assert "Computation Latency=" in log_msg
    assert "ms" in log_msg

def test_meta_analysis_logging_insufficient_context(caplog):
    """
    Verify that insufficient context logs the rejection reason.
    """
    caplog.set_level(logging.INFO, logger="MetaAnalysis")
    ma = MetaAnalysis()
    
    ma.analyze(regime_state=None)
    
    assert len(caplog.records) == 1
    record = caplog.records[0]
    log_msg = record.message
    
    assert "Adjustment Reason=Meta-Analysis MUST NOT execute without L1 context." in log_msg
    assert "Final Trust Score=0.0" in log_msg

def test_meta_analysis_logging_invariant3_violation(caplog):
    """
    Verify that invariant violation logs the rejection reason.
    """
    caplog.set_level(logging.INFO, logger="MetaAnalysis")
    ma = MetaAnalysis()
    regime = {"behavior": MarketBehavior.MEAN_REVERTING_LOW_VOL} # CHOP
    
    ma.analyze(
        regime_state=regime,
        technical_breakout_trust=0.60,
        signal_type="BREAKOUT"
    )
    
    assert len(caplog.records) == 1
    record = caplog.records[0]
    log_msg = record.message
    
    assert "Signal Type=BREAKOUT" in log_msg
    assert "Invariant 3 Violation" in log_msg
    assert "Breakout trust 0.6 > 0.50" in log_msg
    assert "Final Trust Score=0.0" in log_msg
