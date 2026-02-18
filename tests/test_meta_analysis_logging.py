import re
import pytest
import logging
from src.intelligence.meta_analysis import MetaAnalysis
from traderfund.regime.types import MarketBehavior


# ──────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────

def _extract_latency_ms(log_msg: str) -> float:
    """Parse 'Computation Latency=<n>ms' from a log message."""
    m = re.search(r"Computation Latency=([\d.]+)ms", log_msg)
    assert m, f"Latency field missing in log: {log_msg!r}"
    return float(m.group(1))

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


# ══════════════════════════════════════════════════════════════════════════════
# QA-2 — Value-Precision Logging Assertions
# ══════════════════════════════════════════════════════════════════════════════

class TestMetaAnalysisLoggingValuePrecision:
    """
    Replaces / extends shallow string-presence checks with:
      - Actual regime enum value asserted in log
      - Trust score exact numeric verified
      - Latency > 0 AND < 1000 ms
      - Adjustment reason matches regime context
      - Boundary tests at 0.0, 0.50 (exact), and 1.0
    """

    def test_regime_value_present_in_log_trending(self, caplog):
        """Log contains the actual MarketBehavior enum name, not just 'Regime Context='."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        ma = MetaAnalysis()
        ma.analyze(
            regime_state={"behavior": MarketBehavior.TRENDING_NORMAL_VOL},
            signal_type="MOMENTUM",
        )
        msg = caplog.records[0].message
        assert "TRENDING_NORMAL_VOL" in msg

    def test_regime_value_present_in_log_chop(self, caplog):
        """CHOP regime enum name appears in the log message."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        ma = MetaAnalysis()
        ma.analyze(
            regime_state={"behavior": MarketBehavior.MEAN_REVERTING_LOW_VOL},
            technical_breakout_trust=0.30,
        )
        msg = caplog.records[0].message
        assert "MEAN_REVERTING_LOW_VOL" in msg

    def test_trust_score_exact_1_0_on_success(self, caplog):
        """Successful analysis logs Final Trust Score=1.0 exactly."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(regime_state={"behavior": MarketBehavior.TRENDING_NORMAL_VOL})
        assert "Final Trust Score=1.0" in caplog.records[0].message

    def test_trust_score_exact_0_0_on_no_context(self, caplog):
        """No regime context → Final Trust Score=0.0 exactly."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(regime_state=None)
        assert "Final Trust Score=0.0" in caplog.records[0].message

    def test_trust_score_exact_0_0_on_invariant3_rejection(self, caplog):
        """Invariant 3 rejection → Final Trust Score=0.0 exactly."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(
            regime_state={"behavior": MarketBehavior.MEAN_REVERTING_LOW_VOL},
            technical_breakout_trust=0.75,
        )
        assert "Final Trust Score=0.0" in caplog.records[0].message

    def test_latency_positive_and_below_1000ms_on_success(self, caplog):
        """Latency field is > 0 and < 1000 ms on the happy path."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(regime_state={"behavior": MarketBehavior.TRENDING_NORMAL_VOL})
        latency = _extract_latency_ms(caplog.records[0].message)
        assert latency > 0.0
        assert latency < 1000.0

    def test_latency_positive_and_below_1000ms_on_rejection(self, caplog):
        """Latency is logged even on the REJECTED fast-return path."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(
            regime_state={"behavior": MarketBehavior.MEAN_REVERTING_HIGH_VOL},
            technical_breakout_trust=0.70,
        )
        latency = _extract_latency_ms(caplog.records[0].message)
        assert latency > 0.0
        assert latency < 1000.0

    def test_latency_positive_on_insufficient_context(self, caplog):
        """Latency is always logged even when regime_state is None."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(regime_state=None)
        latency = _extract_latency_ms(caplog.records[0].message)
        assert latency > 0.0
        assert latency < 1000.0

    def test_adjustment_reason_is_success_on_active_path(self, caplog):
        """Adjustment reason is exactly 'Success' when analysis completes normally."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(regime_state={"behavior": MarketBehavior.TRENDING_NORMAL_VOL})
        assert "Adjustment Reason=Success" in caplog.records[0].message

    def test_adjustment_reason_describes_chop_regime_violation(self, caplog):
        """Reason text names CHOP regime when Invariant 3 fires for CHOP."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(
            regime_state={"behavior": MarketBehavior.MEAN_REVERTING_HIGH_VOL},  # CHOP
            technical_breakout_trust=0.80,
            signal_type="BREAKOUT",
        )
        msg = caplog.records[0].message
        assert "CHOP" in msg
        assert "Invariant 3 Violation" in msg

    def test_adjustment_reason_describes_trending_violation(self, caplog):
        """Reason text names TRENDING regime when momentum constraint fires."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(
            regime_state={"behavior": MarketBehavior.TRENDING_NORMAL_VOL},
            momentum_trust=0.40,
            factor_alignment=True,
        )
        msg = caplog.records[0].message
        assert "TRENDING" in msg
        assert "Invariant 3 Violation" in msg

    # ── Boundary cases ────────────────────────────────────────────────────

    def test_boundary_050_exact_in_chop_not_rejected(self, caplog):
        """technical_breakout_trust=0.50 exactly is NOT rejected (code uses strict >)."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        result = MetaAnalysis().analyze(
            regime_state={"behavior": MarketBehavior.MEAN_REVERTING_LOW_VOL},
            technical_breakout_trust=0.50,
        )
        assert result["status"] == "ACTIVE"
        assert "Final Trust Score=1.0" in caplog.records[0].message

    def test_boundary_051_in_chop_is_rejected(self, caplog):
        """technical_breakout_trust=0.51 in CHOP IS rejected (0.51 > 0.50)."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        result = MetaAnalysis().analyze(
            regime_state={"behavior": MarketBehavior.MEAN_REVERTING_LOW_VOL},
            technical_breakout_trust=0.51,
        )
        assert result["status"] == "REJECTED"
        assert "Final Trust Score=0.0" in caplog.records[0].message

    def test_boundary_trust_1_0_logged_for_trending_active(self, caplog):
        """trust_score=1.0 on standard ACTIVE path — value confirmed in log."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(regime_state={"behavior": MarketBehavior.TRENDING_HIGH_VOL})
        assert "Final Trust Score=1.0" in caplog.records[0].message

    def test_boundary_trust_0_0_logged_for_insufficient_context(self, caplog):
        """trust_score=0.0 on INSUFFICIENT_CONTEXT path — value confirmed in log."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        MetaAnalysis().analyze(regime_state=None)
        assert "Final Trust Score=0.0" in caplog.records[0].message

    def test_boundary_momentum_060_exact_in_trending_with_alignment_active(self, caplog):
        """momentum_trust=0.60 exactly with factor_alignment=True is NOT rejected (code uses <)."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        result = MetaAnalysis().analyze(
            regime_state={"behavior": MarketBehavior.TRENDING_NORMAL_VOL},
            momentum_trust=0.60,
            factor_alignment=True,
        )
        assert result["status"] == "ACTIVE"
        assert "Final Trust Score=1.0" in caplog.records[0].message

    def test_boundary_momentum_059_in_trending_with_alignment_rejected(self, caplog):
        """momentum_trust=0.59 with factor_alignment=True IS rejected (0.59 < 0.60)."""
        caplog.set_level(logging.INFO, logger="MetaAnalysis")
        result = MetaAnalysis().analyze(
            regime_state={"behavior": MarketBehavior.TRENDING_NORMAL_VOL},
            momentum_trust=0.59,
            factor_alignment=True,
        )
        assert result["status"] == "REJECTED"
        assert "Final Trust Score=0.0" in caplog.records[0].message
